#coding=utf-8
'''
Created on 2016��12��13��

@author: feifei
'''

from bs4 import BeautifulSoup
import requests

def main():
    website="https://gate.d5.mpi-inf.mpg.de/webyago3spotlx/Browser?entityIn=density&codeIn=eng"
    response=requests.get(website)
#     print response.text
    soup=BeautifulSoup(response.text,from_encoding="utf-8")
    print soup.original_encoding
    path="F:\eclipse_doctor\KnowledgeGraph\output\yago_density"
    open(path,"w").write(soup.prettify("utf-8"))
    

if __name__=="__main__":
    main()