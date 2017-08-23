#coding=utf-8
'''
Created on 2016年10月31日

@author: feifei
'''

from bs4  import BeautifulSoup
import os


def extract_str(html):
    """
    extract words from a html document to a string
    """
    soup = BeautifulSoup(html)
#     print soup.prettify()
    content = ""
    tags_p= soup.findAll("p")
    for tag in tags_p:
        tags_span=tag.findAll("span")
        for tag_p in tags_span:
            content += tag_p.string.replace("&nbsp;","").replace("\n","")
        content+="\n"  
#     print content
    return content

def extract_str_list(html):
    """
    extract words from a html document into a string list
    """
    soup = BeautifulSoup(html)
#     print soup.prettify()
    content = []
    tags_p= soup.findAll("p")
    for tag in tags_p:
        tags_span=tag.findAll("span")
        tmp = ""
        for tag_p in tags_span:
            tmp += tag_p.string.replace("&nbsp;","").replace("\n","")
        content.append(tmp)
#     print content
    return content   
    
def ectract_folder(path):
    path_dir = os.listdir(path)
    for dir in path_dir:
        child = os.path.join(path,dir)
        f =open(child,"r")
        html = f.read()
        extract_str(html.decode("gb2312").encode("utf-8"))

if __name__=="__main__":
    print "start running"
    path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
    path=path_project+"/input" 
    ectract_folder(path)