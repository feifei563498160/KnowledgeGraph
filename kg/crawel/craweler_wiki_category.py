#coding=utf-8
'''
Created on 2016年11月24日

@author: feifei
'''
# import urllib2
import requests
import re
import os
import datetime
# from bs4 import BeautifulSoup
from multiprocessing import Pool


def get_category_and_common_concept_urls(level,url_super,url_root,pattern_category_url,pattern_common_concept,urls_category_all,common_concept_all):
    """
    this method can extract url recursively
    """
#     print "extract url: "+url_super+" pattern is "+pattern_url
    response=requests.get(url_super)
    urls_category_result=re.findall(pattern_category_url, response.text.encode("utf-8"))
    common_concept_result=re.findall(pattern_common_concept, response.text.encode("utf-8"))
    print "level="+str(level)
    print url_super+" has category result:"+str(len(urls_category_result))
    print url_super+" has common_concept result:"+str(len(common_concept_result))
    
    #this condition is the convergence
    if len(urls_category_result)==0:
        common_concept_all.update(common_concept_all.union(common_concept_result))
        return 
    if level>=2:
        level-=1
        return
    urls_category_all.add(url_super)
#     urls_category_result_set=set(urls_category_result)
#     urls_category_all.add(url_super)
    urls_category_result_set=set(urls_category_result)
    for url_sub in urls_category_result_set:
        whole_url=url_root+url_sub
        if whole_url not in urls_category_all:
            level+=1
            get_category_and_common_concept_urls(level,whole_url,url_root,pattern_category_url,pattern_common_concept,urls_category_all,common_concept_all)
#             urls_category_all.update(urls_category_all.union(urls_category_result_sub))
            level-=1
            common_concept_all.update(common_concept_all.union(common_concept_result))
            
            
def extract_category(url):
    pattern_category="href=\"/wiki/Category:[\s\S]*?\">([\s\S]*?)</a>‎ <span title=\"Contains (\d+) subcategor(ies|y), (\d+) page[s]?, and (\d+) file[s]?\"[\s\S]*?</span></div>"
    doc=requests.get(url)
    return re.findall(pattern_category, doc.text)

def extract_common_concept(url):
    pattern_common_concept="<li><a href=\"/wiki/(?!Category:)[\s\S]*?\" title=\"[\s\S]*?\">([\s\S]*?)</a></li>"
    doc=requests.get(url)
    return re.findall(pattern_common_concept, doc.text)           
            
def crawel_category_multiprocess(url_list):
    categories=[]
    pool=Pool(8)
    match_list_all=pool.map(extract_category,url_list)
    pool.close()
    pool.join()
    for match_list in match_list_all:
        for match in match_list:
            categories.append(match[0])
    return categories

def crawel_common_concept_multiprocess(url_list):
    common_concepts=[]
    pool=Pool(8)
    match_list_all=pool.map(extract_common_concept,url_list)
    pool.close()
    pool.join()
    for match_list in match_list_all:
        for match in match_list:
            common_concepts.append(match[0])
    return common_concepts

def output_txt(lines,path):
    newlines=[]
    for line in lines:
        newlines.append(line.strip()+"\n")
    with open(path,'w') as f:
        f.writelines(newlines)


def main():
    """
    we extract the category url, meanwhile we can ectract the common concept
    """
    websites=["https://en.wikipedia.org/wiki/Category:Dentistry",
              "https://en.wikipedia.org/wiki/Category:Gingiva",
              "https://en.wikipedia.org/wiki/Category:Glands_of_mouth",
              "https://en.wikipedia.org/wiki/Category:Gustatory_system",
              "https://en.wikipedia.org/wiki/Category:Oral_hygiene",
              "https://en.wikipedia.org/wiki/Category:Teeth"]
    
    pattern_category_url="href=\"(/wiki/Category:[\s\S]*?)\"[\s\S]*?</a>‎ <span title=\"(?=Contains)"
    
#     pattern_common_concept_url="<li><a href=\"(/wiki/(?!Category:)[\s\S]*?)\""
    pattern_common_concept="<li><a href=\"/wiki/(?!Category:)[\s\S]*?\" title=\"[\s\S]*?\">([\s\S]*?)</a></li>"
    root_url="https://en.wikipedia.org"
    
    start = datetime.datetime.now()
    print "start craweler all urls, start time:"+ start.strftime("%Y-%m-%d %H:%M:%S")
    urls_category_all=set([])
    common_concepts_all=set([])
    for website in websites:
        level=0
        get_category_and_common_concept_urls(level,website,root_url,pattern_category_url,pattern_common_concept,urls_category_all,common_concepts_all)
    end = datetime.datetime.now()
    runtime=(end - start).seconds
    print "urls has been craweled,runtime: "+str(runtime)
    
    start = datetime.datetime.now()
    print "starting to extract concept, start time:"+start.strftime("%Y-%m-%d %H:%M:%S")
    categries_all=crawel_category_multiprocess(urls_category_all)
    end = datetime.datetime.now()
    runtime=(end - start).seconds
    print "extracting concept over,runtime:"+str(runtime)
    
    path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
    path_category = path_project+os.sep+"output"+os.sep+"category.txt"
    path_common_concept = path_project+os.sep+"output"+os.sep+"category.txt"
    print "output into the file: "+path_category+"; "+path_common_concept
    output_txt(categries_all, path_category)
    output_txt(common_concepts_all, path_common_concept)

if __name__=="__main__":
    main()

    
    