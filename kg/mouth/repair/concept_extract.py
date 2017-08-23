#coding=utf-8
'''
Created on 2016年10月31日

@author: feifei
'''
from kg.util.html_operator import extract_str
from kg.util.html_operator import extract_str_list

# from nltk.parse import stanford
import jieba
import os
from bosonnlp import BosonNLP


def bosonnlp_segmentation(str_list):
    nlp = BosonNLP('NBSC61pl.10304.Fnwc_rUz9fyw')
    result = nlp.tag(str_list)
    for tag_map in result:
        word_tokens = tag_map['word']
        for word in word_tokens:
            print word.encode("utf-8")+"|",
        print "\n"
        
        
def jieba_segmentation(str,usr_dict_path):
    jieba.load_userdict(usr_dict_path)
    seg_list= jieba.cut(str,cut_all=False)
    print '|'.join(seg_list)

   
if __name__=="__main__":
    path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir, os.pardir))
    print path_project
    path=path_project+"/input/data1.html"
    f =open(path,"r")
    html = f.read() 
    contents=extract_str_list(html.decode("gb2312").encode("utf-8"))
    content=extract_str(html.decode("gb2312").encode("utf-8"))
    jieba_segmentation(content)
    
#     extract_n_gram(html.decode("gb2312").encode("utf-8"))
