#coding=utf-8
'''
Created on 2016��12��13��

@author: feifei
'''
import re
import os
from kg.util.file import load_json
import codecs
import requests
def seg_sent(sent):
    pass

def find_special_char(data):
    special_char=set([])
    for item in data:
        for pos2def in item["pos2definition"]:
            definition=pos2def["definition"]
            for char in definition:
                if True != char.isalpha():
                    special_char.add(char)
    return special_char

def test():
    path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
    path_data= path_project+os.sep+"input"+os.sep+"items.json"
    path_output=path_project+os.sep+"output"+os.sep+"special_chars.txt"
    data=load_json(path_data)
    special_chars=find_special_char(data)
    fp=codecs.open(path_output, 'w','utf-8')
    for i in special_chars:
        fp.write(i+"\n")  
    print special_chars


def get_urls(root):
    response=requests.get(root)
    path_output="\urls.txt"
    pattern='addRow\(\"(.*?)\"'
    result=re.findall(pattern, response.text.encode("utf-8"))
    urls=[]
    for postfix in result:
        urls.append(root+postfix)
                
    fp_out=open(path_output,'w')
    for url in urls:
        fp_out.write(url)
        
if __name__=="__main__":
#     test()
    get_urls('ftp://ccg.vital-it.ch/mga/hg19/fantom5/')


