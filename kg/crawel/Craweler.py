#coding=utf-8
'''
Created on 2016年11月24日

@author: feifei
'''
# import urllib2
import requests
import re
import os
import json
import collections
import datetime
# from bs4 import BeautifulSoup
from multiprocessing import Pool
import urllib2

def get_urls(url_super,url_root,pattern_url):
#     print "extract url: "+url_super+" pattern is "+pattern_url
    response=requests.get(url_super)
    urls_result=re.findall(pattern_url, response.text)
#     print url_super+" has result:"+str(len(urls_result))
    if len(urls_result)==0:
        return []
    urls_all=set([])
    urls_all.add(url_super)
    urls_result_set=set(urls_result)
    for url_sub in urls_result_set:
        whole_url=url_root+url_sub
        pattern_url="<a href=\"("+url_sub+"[\s\S]*?)\""
        if whole_url not in urls_all:
            urls_sub=get_urls(whole_url,url_root,pattern_url)
            urls_all.update(urls_all.union(urls_sub))
    return  urls_all

def extract_concept(url):
    sub_reg=url.split("/")[-1]
    pattern="<a href=\"/("+sub_reg+"[\s\S]*?)\" title.*?>([\s\S]*?)</a>"
    doc=requests.get(url)
    return re.findall(pattern, doc.text)
#     for match in match_result:
#         code2concept[match[0]]=match[1]
            
            
def crawel_multiprocess(url_list):
    code2concept={}
    pool=Pool(8)
    match_list_all=pool.map(extract_concept,url_list)
    pool.close()
    pool.join()
    for match_list in match_list_all:
        for match in match_list:
            code2concept[match[0]]=match[1]
    return code2concept

def output2json(dic,path):
    dict=collections.OrderedDict(sorted(dic.iteritems(), key=lambda d:d[0]))
    json.dump(dict, open(path, 'w'),indent=2)



def main():
    pattern_url_root="<a href=\"(/[A-Z][\s\S]*?)\"" 
    url_root="http://www.atccode.com"
    
    start = datetime.datetime.now()
    print "start craweler all urls, start time:"+ start.strftime("%Y-%m-%d %H:%M:%S")
    urls=get_urls(url_root,url_root,pattern_url_root)
    end = datetime.datetime.now()
    runtime=(end - start).seconds
    print "urls has been craweled,runtime: "+str(runtime)
    
    start = datetime.datetime.now()
    print "starting to extract concept, start time:"+start.strftime("%Y-%m-%d %H:%M:%S")
    code2concept=crawel_multiprocess(urls)
    end = datetime.datetime.now()
    runtime=(end - start).seconds
    print "extracting concept over,runtime:"+str(runtime)
    
    path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
    path = path_project+os.sep+"output"+os.sep+"code2concept.json"
    print "output into the file: "+path
    output2json(code2concept,path)
    
def test_proxy(): 
    proxies = {
#         "http": "http://218.20.227.183:1080",
#         "https": "http://218.20.227.183:1080",
        "http": "http://122.192.32.76:7280",
        "https": "http://122.192.32.76:7280",
    }

    header_info={
            'Host': 'ss1.bdstatic.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
#                 'Upgrade-Insecure-Requests':"1"
            }
#     header={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0',}
    session = requests.Session()
    url = "http://www.baidu.com/" 
#     response=requests.get(url=url,headers=header_info,proxies=proxies)
    response=session.get(url=url,headers=header_info)
#     response=urllib2.Request.get.get(url,header=header_info)
#     print response.headers
    print response.headers

if __name__=="__main__":
#     main()
    test_proxy()
    
    
    