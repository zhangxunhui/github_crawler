# encoding=utf8
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import csv
import MySQLdb

def readFile(filepath):
    f = open(filepath, "r")
    return f.read()


def writeFile(filepath, content):
    f = open(filepath, "w")
    f.write(content)
    f.close()


def writeCSV(filepath, contentList):
    with open(filepath, mode='w') as f:
        f_writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        for content in contentList:
            f_writer.writerow(content)


def readCSV(filepath):
    result = []
    with open(filepath) as f:
        csv_reader = csv.reader(f, delimiter=',')
        for row in csv_reader:
            result.append(row)
    return result


def connectMysqlDB(config, autocommit = True):

    db = MySQLdb.connect(host='localhost',
                         user=config['mysql']['user'],
                         passwd=config['mysql']['passwd'],
                         db=config['mysql']['db'],

                         local_infile=1,
                         use_unicode=True,
                         charset='utf8mb4',

                         autocommit=autocommit)
    return db