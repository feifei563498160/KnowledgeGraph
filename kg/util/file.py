#coding=utf-8
'''
Created on 2016年12月5日

@author: feifei
'''
import json
import codecs
def read_n(num,path):
    with open(path,'r') as f:
        return f.read(100)
        
def output(lines,path):   
    with open(path,'w') as f:
        f.writelines(lines)
        
def load_json(path):
    return json.load(codecs.open(path, encoding='UTF-8')) 
      
if __name__=="__main__":
    path='H:\KnowledgeGraphCurrent\yago\yago3_tsv\yagoWordnetIds.tsv'
    print open(path,'r').read(3000) 