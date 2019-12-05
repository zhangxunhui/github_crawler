import multiprocessing
import yaml
import MySQLdb
import copy
# import requests
import urllib2 as ulib
import re, sys
from bs4 import BeautifulSoup
from utils import *
import time

# create table
def create_table(cur, tableName):
    # whether the table exists
    try:
        cur.execute("select max(id) from {}".format(tableName))
        cur.fetchone()
        exists = True
    except Exception as e:
        exists = False
    if exists == False:
        sql = "CREATE TABLE `pr_htmls` (" \
              "`id` int(11) NOT NULL AUTO_INCREMENT," \
              "`project_id` int(11) DEFAULT NULL," \
              "`github_id` int(11) DEFAULT NULL," \
              "`url` text," \
              "`discussion_timeline_actions` longtext," \
              "PRIMARY KEY (`id`)," \
              "KEY `project_id` (`project_id`)" \
              ") ENGINE=InnoDB DEFAULT CHARSET=utf8;"
        cur.execute(sql)

# read config file
f = open('config.yaml', 'r')
config = yaml.load(f.read(), Loader=yaml.BaseLoader)

db = MySQLdb.connect(host='localhost',
                     user=config['mysql']['user'],
                     passwd=config['mysql']['passwd'],
                     db=config['mysql']['db'],

                     local_infile=1,
                     use_unicode=True,
                     charset='utf8mb4',

                     autocommit=True)
print "successfully connected to mysql database"
cur = db.cursor()

# create the table for storing results
create_table(cur, "pr_htmls")

# read all the projects that need to be handled
project_ids = readFile("final_selected_projects.txt").split("\n")
project_ids = [int(p) for p in project_ids if p != ""]
projectDict = {}
for project_id in project_ids:
    cur.execute("select u.login, p.name "
                "from projects p, users u "
                "where p.id = %s "
                "and u.id = p.owner_id", (project_id,))
    p = cur.fetchone()
    projectDict[project_id] = {"ownername": p[0], "reponame": p[1]}
print "finish reading selected projects"


def crawl(attr):
    project_id = int(attr.split("_")[0])
    github_id = int(attr.split("_")[1])
    # print "handling project_id: %d, github_id: %d" % (project_id, github_id)
    url = "https://github.com/" + projectDict[project_id]["ownername"] + "/" + projectDict[project_id][
        "reponame"] + "/pull/" + str(github_id)
    # print url

    # user login
    cookie = "_ga=GA1.2.1107768544.1561208065; _octo=GH1.1.1372982601.1561208065; _device_id=4f0d01814a2edb7eb0633d41e0f851ed; ajs_user_id=null; ajs_group_id=null; ajs_anonymous_id=%2235373192-66d9-449b-b750-5787e31158e7%22; user_session=0ci29p2I-jZE4CQZNJ0Nia8GiTlqVa-DkN5yy6J2pa-1_jEa; __Host-user_session_same_site=0ci29p2I-jZE4CQZNJ0Nia8GiTlqVa-DkN5yy6J2pa-1_jEa; logged_in=yes; dotcom_user=nigel007; has_recent_activity=1; _gat=1; tz=Europe%2FAmsterdam; mp_167d2b841f875d338e9aa341312533dc_mixpanel=%7B%22distinct_id%22%3A%20%2216b7f408dd4521-03d3f2e8b7e682-37677e05-fa000-16b7f408dd5402%22%2C%22%24initial_referrer%22%3A%20%22https%3A%2F%2Fwww.iconfont.cn%2F%22%2C%22%24initial_referring_domain%22%3A%20%22www.iconfont.cn%22%2C%22__alias%22%3A%20%22anonymous%408057411815%22%2C%22%24search_engine%22%3A%20%22google%22%7D; _gh_sess=TE9SaUh6a01EdnphN3lVSi9qYWJFZm5RLy9NWW0ydktKa0JHbU5MU3NZUEN4RjVKOFNUZStjTEF2NVp0ZzVSUnQrL0xiSGMyMVVac1NlWGsySlNTbWgzcXBkVHVUcUNjc0d5ZkFwdkQ2YXhaQlNtbVhUbkQ5eTV6VmRqaUcrZ3Z0VFpWNFBab3pNTUFDanY4cUtLYzdoYjlCd1JZOXZ1dUJTOWxrMWpqQnZvPS0tTFJqc1dTWVpIU3FRdTRjbjA3d1Y0Zz09--92132ff6f4b8a81372d01559dc7bc3119bd4cfe5"
    # r = requests.Request(url)
    r = ulib.Request(url)
    r.add_header('cookie', cookie)
    r.add_header('User-Agent',
                 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36')
    resp = ulib.urlopen(r)
    if str(resp.code).startswith("2") == True:
        data = resp.read().decode('utf-8')
        soup = BeautifulSoup(data, 'html.parser')
        discussion_timeline_actions = soup.find_all("div", class_=re.compile("discussion-timeline-actions"))
        if len(discussion_timeline_actions) != 1:
            print "error with this page: " + url
            sys.exit(-1)
        else:
            # print "handled project_id: %d, github_id: %d" % (project_id, github_id)
            cur.execute("insert into pr_htmls (project_id, github_id, url, discussion_timeline_actions) "
                        "values (%s, %s, %s, %s)",
                        (project_id, github_id, url, discussion_timeline_actions[0]))
    else:
        print "404 error with this page: " + url
        sys.exit(-1)


def newLoop():

    # define the pool for multiprocessing
    cores = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(cores)

    print "A new loop: " + str(time.time())
    tasks = []

    # read all the handled tasks
    handled_tasks = []
    cur.execute("select project_id, github_id "
                "from pr_htmls ")
    items = cur.fetchall()
    for item in items:
        handled_tasks.append(str(item[0]) + "_" + str(item[1]))

    # read all the pull_requests related to each project
    for project_id in project_ids:
        cur.execute("select pullreq_id "
                    "from pull_requests "
                    "where base_repo_id = %s", (project_id,))
        github_ids = cur.fetchall()
        for github_id in github_ids:
            tasks.append(str(project_id) + "_" + str(github_id[0]))
    tasks = list(set(tasks) - set(handled_tasks))
    print "finish reading pull_requests table"
    print "%d tasks left for handling" % (len(tasks))

    if len(tasks) == 0:
        print "finished"
        return

    # put all the tasks into the pool
    pool.map(crawl, tasks)
    pool.close()
    pool.join()


if __name__ == "__main__":
    while(True):
        try:
            newLoop()
        except Exception as e:
            print e.message
            time.sleep(5)
            pass
        else:
            break