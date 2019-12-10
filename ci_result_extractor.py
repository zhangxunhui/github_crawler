# encoding=utf8

import yaml
import MySQLdb
import re
from bs4 import BeautifulSoup
from utils import *

import sys
reload(sys)
sys.setdefaultencoding('utf8')

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
              "`id` int(11) NOT NULL AUTO_INCREMENT, " \
              "`pr_html_id` int(11) DEFAULT NULL, " \
              "`project_id` int(11) DEFAULT NULL, " \
              "`github_id` int(11) DEFAULT NULL, " \
              "`created_at` datetime DEFAULT NULL, " \
              "`tool_name` varchar(255) DEFAULT NULL, " \
              "`strong_name` varchar(255) DEFAULT NULL, " \
              "`description` varchar(255) DEFAULT NULL, " \
              "`detail_href` varchar(255) DEFAULT NULL, " \
              "`result` varchar(255) DEFAULT NULL, " \
              "PRIMARY KEY (`id`)," \
              "KEY `project_id` (`project_id`)" \
              ") ENGINE=InnoDB DEFAULT CHARSET=utf8;"
        cur.execute(sql)

if __name__ == "__main__":
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

                         autocommit=False)
    print "successfully connected to mysql database"
    cur = db.cursor()

    # create the table for storing results
    create_table(cur, "pr_cis")

    # read all the market tools
    market_tools = readCSV("market_ci_tools.csv")
    market_tool_names = [m[0].lower() for m in market_tools]

    # read all the handled prs
    cur.execute("select max(pr_html_id) "
                "from pr_cis")
    handled_max_id = cur.fetchone()[0]
    if handled_max_id is None:
        handled_max_id = 0

    # read pr_htmls table
    cur.execute("select id, project_id, github_id, discussion_timeline_actions "
                "from pr_htmls where id > %s", (handled_max_id,))
    items = cur.fetchall()

    for item in items:

        pr_html_id = item[0]
        project_id = item[1]
        github_id = item[2]

        cur.execute("select u.login, p.name "
                    "from users u, projects p "
                    "where u.id = p.owner_id "
                    "and p.id = %s", (project_id,))
        tmp = cur.fetchone()
        ownername = tmp[0]
        reponame = tmp[1]
        url = "https://github.com/" + ownername + "/" + reponame + "/pull/" + str(github_id)
        print url

        # print "handling item: %d/%d" % (project_id, github_id)

        discussion_timeline_actions = item[3]

        # build beautifulsoup obj
        soup = BeautifulSoup(discussion_timeline_actions, 'html.parser')
        tool_results = soup.find_all("div", class_=re.compile("merge-status-item d-flex flex-items-baseline"))

        # find all the tools
        for t in tool_results:

            which_tool = None

            # name & description
            name = t.find("strong", class_=re.compile("text-emphasized")).getText().strip().lower()
            if name.startswith('coverage/') or name.startswith('legal/cla') or name.startswith('datree') or \
                    name.startswith("cla/") or name.startswith("license/cla") or name.startswith("deploy/netlify") or \
                    name.startswith('review/gitmate') or name.startswith("lgtm") or name.startswith("dco") or \
                    name.startswith('wip') or name.startswith("licence/cla") or name.endswith("pivotal-cla"):
                # https://github.com/piqueserver/piqueserver/pull/496(coverage/coveralls) this is not a ci tool
                # https://github.com/odoo/odoo/pull/26490(used by odoo/odoo project itself) not a ci tool (manually check)
                # https://github.com/edx/open-edx-proposals/pull/100 (Datree is not a ci tool)
                # https://github.com/kubernetes/kubernetes/pull/72875 (cla is the check of Contribution License Agreement)
                # https://github.com/sendgrid/sendgrid-go/pull/360 (license/cla is also for cla check)
                # https://github.com/coala/coala-bears/pull/2825 (netlify is something about continuous deployment)
                # https://github.com/coala/coala-bears/pull/2825 (GitMate.io helps you managing your issues using machine learning algorithms - https://github.com/apps/GitMate)
                # https://github.com/ansible/ansible-lint/pull/518 (LGTM is part of continuous security analysis - https://github.com/marketplace/lgtm)
                # https://github.com/ansible/ansible-lint/pull/518 (DCO - This App enforces the Developer Certificate of Origin (DCO) on Pull Requests)
                # https://github.com/ansible/ansible-lint/pull/518 (WIP - This app Allow authors of pull requests to set status to pending while still working on it)
                # https://github.com/spf13/viper/pull/272 (licence/cla)
                # https://github.com/spring-projects/spring-data-mongodb/pull/737 (ci/pivotal-cla!!!)
                continue
            desc = t.find("div", class_=re.compile("text-gray.*")).getText()
            desc = desc.replace(name, "").replace(u'\ufffd', "").strip()

            # name exceptions:
            # 1. https://github.com/apache/kafka/pull/7782 (jenkins)
            if project_id == 45297 and name.startswith("jdk"):
                which_tool = 'jenkins'

            # executor url
            executor = t.find("a", class_=re.compile("d-inline-block tooltipped*"), href = True)
            # https://github.com/kubernetes/kubernetes/pull/72875 (there are many websites for k8s tools)
            if executor is not None:
                if executor["href"].endswith("k8s-ci-robot"):
                    which_tool = "k8s"
                elif executor["href"].endswith("onnxbot"):
                    continue # https://github.com/pytorch/pytorch/pull/7653 (onnx is an interchangeable AI model, AI developers can more easily move models between state-of-the-art tools and choose the combination that is best for them)
                elif executor["href"].endswith("azure-pipelines"):
                    continue # https://github.com/ansible/ansible-lint/pull/518 (Azure Pipelines is an app for Continuously build, test, and deploy to any platform and cloud)
                elif executor["href"].startswith("/apps/netlify"):
                    continue # https://github.com/hashicorp/vault/pull/5815
                elif executor["href"].startswith("https://tfe.hashicorp.engineering"):
                    continue # Terraform is something like docker/kubernates, a devops platform, not a CI tool
                elif executor["href"].startswith("https://snyk.io"):
                    continue # https://github.com/jmxtrans/jmxtrans/pull/686 (Snyk is on a mission to help developers use open source and stay secure - not CI tool)
                elif executor["href"].startswith("https://cla.hashicorp.com"):
                    continue # https://github.com/hashicorp/vault/pull/5815
            # ci_result
            ci_result = None
            merge_status_div = str(t.find("svg", class_=re.compile("octicon.*")))
            matcher = re.match('<svg.*?d\-block (.*?)\"', merge_status_div)
            if matcher:
                r = matcher.group(1)
                if r == "text-red":
                    ci_result = 'failed'
                elif r == "text-green":
                    ci_result = 'passed'
                elif r == "color-yellow-7":
                    # https://github.com/OpenLiberty/open-liberty/pull/7051
                    # https://github.com/makersacademy/rps-challenge/pull/1096
                    ci_result = 'unfinished'
                else:
                    # print "haven't met this before! Project_id: %d, Github_id: %d" % (project_id, github_id)
                    print url
                    sys.exit(-1)
            else:
                # print "error: this ci tools does not have result. Project_id: %d, Github_id: %d" % (project_id, github_id)
                print url
                sys.exit(-1)

            # href of detail tag
            href = None
            detail = t.find("a", class_=re.compile("status-actions"), href = True)
            if detail is not None:
                if detail.getText().strip() != "Details":
                    # print "something new for the page. Project_id: %d, Github_id: %d" % (project_id, github_id)
                    print url
                    sys.exit(-1)
                else:
                    href = detail["href"]

            # get the name of the target ci tool
            # 1. match by name
            if which_tool is None:
                if name.startswith('ci') or name.startswith('continuous-integration'):
                    which_tool = name.split("/")[1].lower()
                    if str(which_tool).startswith("circleci:"):
                        which_tool = "circleci"
                elif name.startswith('concourse-ci'):
                    which_tool = 'concourse-ci'
                else:
                    which_tool = name.split("/")[0].lower()
                # handle some exceptions
                if which_tool.startswith("travis ci"):
                    which_tool = 'travis-ci'  # https://github.com/travis-ci/travis-build/pull/1571

                # 2. verify by url
                if which_tool == "travis-ci":
                    # https://github.com/mate-academy/layout_style-it-up/pull/28 (Travis ci can be configed on Github page)
                    pass # don't need to check, these must be ci tools
                else:
                    if href is not None:
                        if which_tool not in href:
                            if which_tool == "jenkins" or which_tool == 'concourse-ci':
                                pass # jenkins has it's own configed web url
                                # https://github.com/spring-projects/spring-data-mongodb/pull/737 (concourse-ci)
                            elif "jenkins" in href:
                                which_tool = "jenkins" # https://github.com/pytorch/pytorch/pull/7653
                            elif which_tool.startswith("pull-kubernetes"):
                                pass # https://github.com/kubernetes/kubernetes/pull/72875 temporary
                            elif href.startswith("http://buildbot.holoviews.org") or "duktape" in href\
                                    or (project_id == 75061625 and name == "rtc build"):
                                # https://github.com/holoviz/holoviews/pull/3385 (web not used anymore)
                                # https://github.com/svaarala/duktape/pull/575 (Duktape is an embeddable ECMAScript® engine with a focus on portability and compact footprint. By integrating Duktape into your C/C++ program you can easily extend its functionality through scripting)
                                # https://github.com/OpenLiberty/open-liberty/pull/2693 (this cannot be decided)
                                continue
                            elif "travis-ci" in href:
                                which_tool = "travis-ci" # https://github.com/flot/flot/pull/1225
                            elif "circleci" in href:
                                which_tool = 'circleci'
                            else:
                                # print "error with this ci tool name: %s. Project_id: %d, Github_id: %d" % (which_tool, project_id, github_id)
                                print url
                                sys.exit(-1)

            # read pr_create time
            cur.execute("select created_at "
                        "from pull_request_history prh, pull_requests pr "
                        "where pr.id = prh.pull_request_id "
                        "and prh.action = 'opened' "
                        "and pr.base_repo_id = %s "
                        "and pr.pullreq_id = %s", (project_id, github_id))
            created_at = cur.fetchone()
            if created_at is None:
                # record miss in pull_request_history table (e.g. pr_id: 58108981)
                created_at = None
            else:
                created_at = created_at[0]

            # 3. insert into table
            cur.execute("insert into pr_cis (project_id, pr_html_id, github_id, created_at, tool_name, strong_name, description, detail_href, result) values "
                        "(%s, %s, %s, %s, %s, %s, %s, %s, %s)", (project_id, pr_html_id, github_id, created_at, which_tool, name, desc, href, ci_result))
        db.commit() # commit after a pr is handled
    print "finish"