import multiprocessing
import yaml
import MySQLdb
import urllib2 as ulib
import re, sys
from bs4 import BeautifulSoup
from utils import *
import time


if __name__ == "__main__":
    urls = ["https://github.com/marketplace/category/continuous-integration",
            "https://github.com/marketplace/category/continuous-integration?after=Y3Vyc29yOjIw",
            "https://github.com/marketplace/category/continuous-integration?after=Y3Vyc29yOjQw",
            "https://github.com/marketplace/category/continuous-integration?after=Y3Vyc29yOjYw",
            "https://github.com/marketplace/category/continuous-integration?after=Y3Vyc29yOjgw",
            "https://github.com/marketplace/category/continuous-integration?after=Y3Vyc29yOjEwMA%3D%3D",
            "https://github.com/marketplace/category/continuous-integration?after=Y3Vyc29yOjEyMA%3D%3D",
            "https://github.com/marketplace/category/continuous-integration?after=Y3Vyc29yOjE0MA%3D%3D",
            "https://github.com/marketplace/category/continuous-integration?after=Y3Vyc29yOjE2MA%3D%3D",
            "https://github.com/marketplace/category/continuous-integration?after=Y3Vyc29yOjE4MA%3D%3D",
            "https://github.com/marketplace/category/continuous-integration?after=Y3Vyc29yOjIwMA%3D%3D",
            "https://github.com/marketplace/category/continuous-integration?after=Y3Vyc29yOjIyMA%3D%3D",
            "https://github.com/marketplace/category/continuous-integration?after=Y3Vyc29yOjI0MA%3D%3D",
            "https://github.com/marketplace/category/continuous-integration?after=Y3Vyc29yOjI2MA%3D%3D",
            "https://github.com/marketplace/category/continuous-integration?after=Y3Vyc29yOjI4MA%3D%3D",
            "https://github.com/marketplace/category/continuous-integration?after=Y3Vyc29yOjMwMA%3D%3D",
            "https://github.com/marketplace/category/continuous-integration?after=Y3Vyc29yOjMyMA%3D%3D",
            "https://github.com/marketplace/category/continuous-integration?after=Y3Vyc29yOjM0MA%3D%3D",
            "https://github.com/marketplace/category/continuous-integration?after=Y3Vyc29yOjM2MA%3D%3D",
            "https://github.com/marketplace/category/continuous-integration?after=Y3Vyc29yOjM4MA%3D%3D",
            "https://github.com/marketplace/category/continuous-integration?after=Y3Vyc29yOjQwMA%3D%3D",
            "https://github.com/marketplace/category/continuous-integration?after=Y3Vyc29yOjQyMA%3D%3D",
            "https://github.com/marketplace/category/continuous-integration?after=Y3Vyc29yOjQ0MA%3D%3D",
            "https://github.com/marketplace/category/continuous-integration?after=Y3Vyc29yOjQ2MA%3D%3D",
            "https://github.com/marketplace/category/continuous-integration?after=Y3Vyc29yOjQ4MA%3D%3D",
            "https://github.com/marketplace/category/continuous-integration?after=Y3Vyc29yOjUwMA%3D%3D",
            "https://github.com/marketplace/category/continuous-integration?after=Y3Vyc29yOjUyMA%3D%3D",
            "https://github.com/marketplace/category/continuous-integration?after=Y3Vyc29yOjU0MA%3D%3D",
            "https://github.com/marketplace/category/continuous-integration?after=Y3Vyc29yOjU2MA%3D%3D",
            "https://github.com/marketplace/category/continuous-integration?after=Y3Vyc29yOjU4MA%3D%3D",
            "https://github.com/marketplace/category/continuous-integration?after=Y3Vyc29yOjYwMA%3D%3D"]
    toolList = []
    for url in urls:
        r = ulib.Request(url)
        resp = ulib.urlopen(r)
        if str(resp.code).startswith("2") == True:
            data = resp.read().decode('utf-8')
            soup = BeautifulSoup(data, 'html.parser')
            tools = soup.find_all("a", class_=re.compile("col-md-6 mb-4 d-flex no-underline"), href = True)
            for tool in tools:
                href = tool['href'].strip()
                # find the name
                name = tool.find("h3", class_=re.compile("h4")).getText().strip()
                print 'handling tool: ' + name
                # insert into file
                if [name, href] in toolList:
                    print "tool: " + name + " already exists"
                    continue
                toolList.append([name, href])
        else:
            print "404 error with this page: " + url
            sys.exit(-1)
        time.sleep(2)
    writeCSV("market_ci_tools.csv", toolList)