# encoding=utf8

import yaml
import MySQLdb
import re
from utils import *

import time
import threading
import Queue
import xlsxwriter

import sys
reload(sys)
sys.setdefaultencoding('utf8')

f = open('config.yaml', 'r')
config = yaml.load(f.read(), Loader=yaml.BaseLoader)

result_table_name = "reduced_pull_request_cis"
THREAD_NUM = 20


if __name__ == "__main__":

    conn = connectMysqlDB(config)
    cur = conn.cursor()

    # randomly select 1000 distinct project_id, github_id
    cur.execute("select id, project_id, github_id, ci_or_not from reduced_pull_request_cis where ci_or_not=1 ORDER BY RAND() limit 500")

    items_1 = cur.fetchall()

    cur.execute("select id, project_id, github_id, ci_or_not from reduced_pull_request_cis where ci_or_not=0 ORDER BY RAND() limit 3000")

    items_2 = cur.fetchall()

    items = items_1 + items_2

    result = {} # record the ci result and the text descriptions
    
    has_ci_num = 0
    not_has_ci_num = 0

    for item in items:
        id = item[0]
        project_id = item[1]
        github_id = item[2]

        ci_or_not = item[3]
    
        # read the contexts and descriptions and target_urls
        cur.execute("select context, description, target_url from selected_pr_statuses where project_id=%s and github_id=%s", (project_id, github_id))
        texts = cur.fetchall()

        contexts = []
        descriptions = []
        target_urls = []

        for text in texts:
            context = text[0]
            description = text[1]
            target_url = text[2]

            if context is not None and context.strip() != "":
                contexts.append(context)
            if description is not None and description.strip() != "":
                descriptions.append(description)
            if target_url is not None and target_url.strip() != "":
                target_urls.append(target_url)

        if len(contexts) == 0 or len(descriptions) == 0:
            continue
        
        if ci_or_not == 1:
            has_ci_num += 1
            if has_ci_num > 200:
                continue
        else:
            not_has_ci_num += 1
            if not_has_ci_num > 200:
                continue
        
        # get pr url
        cur.execute("select u.login, p.name from reduced_users u, reduced_projects p where p.owner_id=u.id and p.id=%s", (project_id,))
        u_eles = cur.fetchone()
        u_owner = u_eles[0]
        u_repo = u_eles[1]
        url = "https://github.com/" + u_owner + "/" + u_repo + "/pull/" + str(github_id)

        result.setdefault(url, {})
        result[url]["ci_or_not"] = ci_or_not

        result[url]["contexts"] = "\n".join(contexts)
        result[url]["descriptions"] = "\n".join(descriptions)
        result[url]["target_urls"] = "\n".join(target_urls)

    print "finish reading contexts and descriptions"

    # insert into xlsx file
    result_file_name = "ci_extractor_yu_verify.xlsx"

    workbook = xlsxwriter.Workbook(result_file_name)
    worksheet = workbook.add_worksheet()

    print "how many results are there: %d" % (len(result))

    row = 0
    for (key, value) in result.items():
        url = key
        worksheet.write_string(row, 0, url)
        # github_id = str(key[1])
        # worksheet.write_string(row, 1, github_id)
        contexts = value["contexts"]
        worksheet.write_string(row, 1, contexts)
        descriptions = value["descriptions"]
        worksheet.write_string(row, 2, descriptions)
        target_urls = value["target_urls"]
        worksheet.write_string(row, 3, target_urls)
        ci_or_not = str(value["ci_or_not"])
        worksheet.write_string(row, 4, ci_or_not)
        row += 1
    workbook.close()

    print "finish"