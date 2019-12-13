import threading
import yaml
import MySQLdb
import copy
# import requests
import urllib2 as ulib
import re, sys
from bs4 import BeautifulSoup
from utils import *
import time
import Queue

cookies = [
    "_ga=GA1.2.1107768544.1561208065; _octo=GH1.1.1372982601.1561208065; _device_id=4f0d01814a2edb7eb0633d41e0f851ed; ajs_user_id=null; ajs_group_id=null; ajs_anonymous_id=%2235373192-66d9-449b-b750-5787e31158e7%22; tz=Europe%2FAmsterdam; user_session=Eq8hMBu1ovPIpgzwJ5KFiNJv79-A5sTiqhgz4WzZB7OFRlbr; __Host-user_session_same_site=Eq8hMBu1ovPIpgzwJ5KFiNJv79-A5sTiqhgz4WzZB7OFRlbr; logged_in=yes; dotcom_user=nigel007; ignored_unsupported_browser_notice=false; has_recent_activity=1; mp_167d2b841f875d338e9aa341312533dc_mixpanel=%7B%22distinct_id%22%3A%20%2216b7f408dd4521-03d3f2e8b7e682-37677e05-fa000-16b7f408dd5402%22%2C%22%24initial_referrer%22%3A%20%22https%3A%2F%2Fwww.iconfont.cn%2F%22%2C%22%24initial_referring_domain%22%3A%20%22www.iconfont.cn%22%2C%22__alias%22%3A%20%22anonymous%408057411815%22%2C%22%24search_engine%22%3A%20%22google%22%7D; _gh_sess=dTRoM1dHZnlEd2E1Q0lqU0NBcm9sYXlaMzFLcHl5emV0YUMrMEVRUmhYek9NdUVyUVc2UUVtQ0p0dlFZMHFXNGR2Vko4a096VkpxTzdDZTA0MjBUUWtpNGRFS1Nld0gwMy9TTEdXZGRCRHhPUHpIcDhEdmVlZk9aNzR4ZDg1ZDh2enk2VGFobUpHb29GSFR2VXBab216Yng4QXRzTGlrbHFNL1hqSnloUmxpQzZaMWtNWDdFVU5kMFZXWFl3QzhtOFZFejlFUE10RTZacHRKaFJMZDRuT3lXbjdnR3BmeEhkNW50bFd4WFg0aytOU2prOGZUMUcvdjlBNGdsSDVNd1lDQkVoVE5pSGp6RlY4T21LS2hEcktLKzJpTUVWWWs1Y2dGbXRhTnRscmVmTG1ISjlIbUdvYkE0dUV2RVd3R3V3R1VVZkMwSFJkNStDbjF4VjQ5Znd3PT0tLVIyKy9QLzNFRDhkOWF3aDFCNGJ4MHc9PQ%3D%3D--d59eed9104a6fa0665b8672054f73146193a8161",
    "_octo=GH1.1.1456500358.1574108177; logged_in=yes; _ga=GA1.2.1159595701.1574108179; _device_id=91d9c81399e2f1ab13d92d87867aeecd; _gh_sess=Q0h4dHFnUXNVMjZBWGZaUlBXbzY4Qnp4T1VjMHFCN3lRU29oLzN2bkZ6K0dxTHJxZzVjcEM5WUpaYnpBZ2g1WUZuOEZ1Nk5GVEM4RnpmT2QxUE81cDBSeVFVQnVTeWlDYzdmanR6OHB2SXF2Ujl5eE12WksyRjVoN1gxU0dZdjRYdFNMbmtlV1BMMkVHVkk1MGdLR1hneWNyckdVbFdsUllPNVl4V3dKeDdxUm95c2NNZVVTNExOaVVqY090bXVBTldGYjdhQ01XNjUrT0hGN04xcTFhQ1E5cURaYmYxVmRMZVYzT0dpdWJ6NzkrMjFFNWtoYWd6NlRhSVNrMkgyeHRRUGJ3YW5DYVJydEFRenNZNnd3OE80SjlnVmdKd0luYytpL0NFTE1iNTQ9LS1CeXB4WmxIZjd6Q1hWUEVIMUNHODdRPT0%3D--025a0f5edbe9e6eddde0ac6054eb01057da21183; tz=Europe%2FAmsterdam; ignored_unsupported_browser_notice=false; user_session=YP-8zBCRGchXUsJLQh6lidlpApVr0P7hcSx0xO21QrgOrrXI; __Host-user_session_same_site=YP-8zBCRGchXUsJLQh6lidlpApVr0P7hcSx0xO21QrgOrrXI; dotcom_user=nigel007; has_recent_activity=1; _gat=1",
    "has_recent_activity=1; _octo=GH1.1.1518588300.1576259939; logged_in=yes; _gh_sess=NEpBK0x0TDYwN1NvUUY3LzhRTy91NERHNXB6aXAxemFXTnRtQ3QvVXlXMlFOK3cxTC9waGs4QlMwOUZZdnRvaGVIVFF0Zkt3eVJhMmtDUkl5aW40OWFqTUFzaDhZZUVXSkEwanhTQU1ZWVUxcmRFLzdHTGVKYk9FNytMOVozbmd1MXdRRUFBZjhRWmpieVRNSCtHbHpPTnUybVpQdHZDVFJjbXVUUjl0V3d6emJEelRqZmt2UmtRZGVmWG5FVm45RmFOU0pRdXlWRGNFWjE2aEVSYWF0a2JCb0ltb20wclk0cVorSm9SbzM1NGlDRnFuV051NytiWEZ4eXl2aTFicWFvR0JLcjJNYld1NWV1Z2ZkMWVzd0E9PS0tU01FL3F2VUt1cnBmUWtXWnVFWGwyZz09--d2103223f3ad9752405e5aab013bb4034c93ce25; _ga=GA1.2.913690471.1576259941; _gat=1; tz=Europe%2FAmsterdam; _device_id=b6bd1814ef13c5c75ccef6b3e8b4aada; user_session=FZg7mWIbXnaSkwdfQpEQJ6dt3JcHof2LFP4J1XjK_Y2e1_C6; __Host-user_session_same_site=FZg7mWIbXnaSkwdfQpEQJ6dt3JcHof2LFP4J1XjK_Y2e1_C6; dotcom_user=nigel008",
    "has_recent_activity=1; _octo=GH1.1.1657552052.1576260049; _ga=GA1.2.494108601.1576260051; _gat=1; tz=Europe%2FAmsterdam; _device_id=0fb171c1b563c99ffe79c2db2c612208; user_session=b9JR-D1hT_2dUIw7rF10rx7pqlpV9io6HGhpsQNP1cr7CDqy; __Host-user_session_same_site=b9JR-D1hT_2dUIw7rF10rx7pqlpV9io6HGhpsQNP1cr7CDqy; logged_in=yes; dotcom_user=nigel009; _gh_sess=U3c2TS9pbHI5WTRMSlNSZUxSSjVwU3o5SnVIREdrVUJrVXhsTnNJT25ZUm1IUXhNbzlkMUlWZU43ZldKZWZoMjViYjllakxZVWVJS3NETnBvR0FJRGZWbENrOFBkQUJaejdPd1FZZkVnNWUzV0l3WVhRNHNEMVE2aHRmMkJkcDFLbnFmWFljUFdwMkdWNExGWFh1NnUxdVN3cHQwRXNzRkZXL1FDRFZpaDVaL2swdFlnTUppQTh4VjRJUFhmUUhzcEF5NVlYWEpTQXFaVWxJYmZodUt6MnJRYXljd082dmpPc0d3UWtQUE54a0FQci85ZG40amN0N3BvcnFreGJxWEpROUdQR0RNZDBKcU9JUVFFaVVEL2F3dzJHYXp3UVRSbnljcjRLTjNIRTdIQ3poR3k3eit4Z3pOc2tQTjNSMTU3Q1UwMi8zSEl0eGNQejBMSVliN3BnPT0tLUNHaVpvSEtKUEpiN0crL1VZcUZjb2c9PQ%3D%3D--96e92e7388f6761118db885c57b4b3df20810ccc"
]

agents = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:70.0) Gecko/20100101 Firefox/70.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:70.0) Gecko/20100101 Firefox/70.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"
]

cookie_times = {}

cookie_time_gap = 1.5 # 1.5s per request

def getCookieAndAgent():
    # get the cookie of user
    cookie = None
    agent = None
    while True:
        for i in range(len(cookies)):
            c = cookies[i]
            a = agents[i]
            # if i == 3:
            #     return c,a
            # else:
            #     continue
            if cookie_times.has_key(i):
                if time.time() - cookie_times[i] < cookie_time_gap:
                    continue
                else:
                    cookie = c
                    agent = a
                    cookie_times[i] = time.time()
                    return cookie, agent
            else:
                cookie = c
                agent = a
                cookie_times[i] = time.time()
                return cookie, agent

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
        sql = "CREATE TABLE `"+ tableName + "` (" \
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

class crawlThread(threading.Thread):
    def __init__(self, q):
        threading.Thread.__init__(self)
        self.q = q
    def run(self):
        while True:
            try:
                work = self.q.get(timeout=0)  # 0s timeout
                project_id = work[0]
                github_id = work[1]

                url = "https://github.com/" + projectDict[project_id]["ownername"] + "/" + \
                      projectDict[project_id][
                          "reponame"] + "/pull/" + str(github_id)
                print url

                c, a = getCookieAndAgent()

                r = ulib.Request(url)
                r.add_header('cookie', c)
                r.add_header('User-Agent', a)
                resp = ulib.urlopen(r)
                if str(resp.code).startswith("2") == True:
                    data = resp.read().decode('utf-8')
                    soup = BeautifulSoup(data, 'html.parser')
                    discussion_timeline_actions = soup.find_all("div", class_=re.compile("discussion-timeline-actions"))
                    if len(discussion_timeline_actions) != 1 or "Already have an account?" in str(
                            discussion_timeline_actions):
                        print "error with this page: " + url
                        sys.exit(-1)
                    else:
                        # print "handled project_id: %d, github_id: %d" % (project_id, github_id)
                        cur.execute("insert into pr_htmls (project_id, github_id, url, discussion_timeline_actions) "
                                    "values (%s, %s, %s, %s)",
                                    (project_id, github_id, url, discussion_timeline_actions[0]))
                else:
                    print "404 error with this page: " + url
            except Queue.Empty:
                return
            except ulib.HTTPError as e:
                if e.code == 404:
                    print "404 error with this page: " + url
            # do whatever work you have to do on work
            self.q.task_done()



threadNum = 4
workQueue = Queue.Queue()

# read all the handled tasks
handled_tasks = []
cur.execute("select project_id, github_id "
            "from pr_htmls ")
items = cur.fetchall()
for item in items:
    handled_tasks.append((item[0], item[1]))

tasks = []
# read all the pull_requests related to each project
for project_id in project_ids:
    cur.execute("select pullreq_id "
                "from pull_requests "
                "where base_repo_id = %s", (project_id,))
    github_ids = cur.fetchall()
    for github_id in github_ids:
        tasks.append((project_id, github_id[0]))
tasks = list(set(tasks) - set(handled_tasks))
print "finish reading pull_requests table"
print "%d tasks left for handling" % (len(tasks))

for (project_id, github_id) in tasks:
    workQueue.put_nowait((project_id, github_id))

for _ in range(threadNum):
    crawlThread(workQueue).start()
workQueue.join()