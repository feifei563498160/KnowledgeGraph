 #coding=utf-8
'''
Created on 2016年11月1日

@author: feifei
'''

# import jieba
import os
# import logging
import chardet
# from bosonnlp import BosonNLP
from kg.util.html_operator import extract_str
from kg.util.html_operator import extract_str_list
from kg.util import mylogger
# import logging


# def bosonnlp_segmentation(str_list):
#     nlp = BosonNLP('NBSC61pl.10304.Fnwc_rUz9fyw')
#     result = nlp.tag(str_list)
#     for tag_map in result:
#         word_tokens = tag_map['word']
#         for word in word_tokens:
#             print word.encode("utf-8")+"|",
#         print "\n"
#         
#         
# def jieba_segmentation(str,usr_dict_path):
#     jieba.load_userdict(usr_dict_path)
#     seg_list= jieba.cut(str,cut_all=False)
#     print '|'.join(seg_list)
    
    
def extract_1_gram(str):
    word_map= {}
    for i in range(len(str)):
        n_gram = str[i]
        if word_map.has_key(n_gram):
            word_map[n_gram]+=1
        else:
            word_map[n_gram]=1
    return word_map
 
 
def extract_2_gram(str):
    word_map= {}
    for i in range(len(str)-1):
        n_gram = str[i]+str[i+1]
        if word_map.has_key(n_gram):
            word_map[n_gram]+=1
        else:
            word_map[n_gram]=1
    return word_map


def extract_3_gram(str):
    word_map= {}
    for i in range(len(str)-2):
        n_gram = str[i]+str[i+1]+str[i+2]
        if word_map.has_key(n_gram):
            word_map[n_gram]+=1
        else:
            word_map[n_gram]=1
    return word_map


def extract_4_gram(str):
    word_map= {}
    for i in range(len(str)-3):
        n_gram = str[i]+str[i+1]+str[i+2]+str[i+3]
        if word_map.has_key(n_gram):
            word_map[n_gram]+=1
        else:
            word_map[n_gram]=1
    return word_map


def extract_5_gram(str):
    word_map= {}
    for i in range(len(str)-5):
        n_gram = str[i]+str[i+1]+str[i+2]+str[i+3]+str[i+4]
        if word_map.has_key(n_gram):
            word_map[n_gram]+=1
        else:
            word_map[n_gram]=1
    return word_map   

def merge_dict(dict1,dict2):
    """
    merge two dict, and the value of the same key should be plused,
    we use double chain merging thought to merge two dict
    """
    if len(dict1)==0:
        return dict2
    if len(dict2)==0:
        return dict1
    sorted_dict1=sorted(dict1.iteritems(),key=lambda asd:asd[0],reverse=False)
    sorted_dict2=sorted(dict2.iteritems(),key=lambda asd:asd[0],reverse=False)
    m=0
    n=0
    cnt=0
    dict={}
    key1=sorted_dict1[m][0]
    key2=sorted_dict2[n][0]
    if key1<=key2:
        dict[key1]=dict1[key1]
    else:
        dict[key2]=dict2[key2]
        
    while m<len(sorted_dict1) and n<len(sorted_dict2):
        key1=sorted_dict1[m][0]
        key2=sorted_dict2[n][0]
        if key1<key2:
            dict[key1]=dict1[key1]
            m+=1
        elif key1>key2:
            dict[key2]=dict2[key2]
            n+=1
        else:
            #if the key is same, we should plus the value
            dict[key1]=dict1[key1]+dict2[key2]
            m+=1
            n+=1
        cnt+=1    
            
    if m<len(sorted_dict1):
        while m<len(sorted_dict1):
            key1=sorted_dict1[m][0]
            dict[key1]=dict1[key1]
            m+=1
    if n<len(sorted_dict2):
        while n<len(sorted_dict2):
            key2=sorted_dict2[n][0]
            dict[key2]=dict2[key2]
            n+=1
       
    return dict

def extract_all_n_gram(str):
    """
    extract all 1,2,3,4,5 gram from a string
    """
#     print str
    dict_n_gram={}
    if len(str)<1:
        pass
    elif len(str)>4:
        dict1 = extract_1_gram(str)
        dict2 = extract_2_gram(str)
        dict3 = extract_3_gram(str)
        dict4 = extract_4_gram(str)
        dict5 = extract_5_gram(str)
        dict_n_gram.update(merge_dict(dict_n_gram, dict1))
        dict_n_gram.update(merge_dict(dict_n_gram, dict2))   
        dict_n_gram.update(merge_dict(dict_n_gram, dict3))   
        dict_n_gram.update(merge_dict(dict_n_gram, dict4))
        dict_n_gram.update(merge_dict(dict_n_gram, dict5))
    elif len(str)==1:
        dict1=extract_1_gram(str)
        dict_n_gram.update(merge_dict(dict_n_gram, dict1))
    elif len(str)==2:
        dict1 = extract_1_gram(str)
        dict2 = extract_2_gram(str)
        dict_n_gram.update(merge_dict(dict_n_gram, dict1))
        dict_n_gram.update(merge_dict(dict_n_gram, dict2))
    elif len(str)==3:
        dict1 = extract_1_gram(str)
        dict2 = extract_2_gram(str)
        dict3 = extract_3_gram(str)
        dict_n_gram.update(merge_dict(dict_n_gram, dict1))
        dict_n_gram.update(merge_dict(dict_n_gram, dict2))   
        dict_n_gram.update(merge_dict(dict_n_gram, dict3)) 
    elif len(str)==4:
        dict1 = extract_1_gram(str)
        dict2 = extract_2_gram(str)
        dict3 = extract_3_gram(str)
        dict4 = extract_4_gram(str)
        dict_n_gram.update(merge_dict(dict_n_gram, dict1))
        dict_n_gram.update(merge_dict(dict_n_gram, dict2))   
        dict_n_gram.update(merge_dict(dict_n_gram, dict3))   
        dict_n_gram.update(merge_dict(dict_n_gram, dict4))     
    return dict_n_gram

def cut_sentence(words): 
    """
    split a string/sentence to separate unit without the punctuation
    """
        # words = (words).decode('utf8')
    start = 0
    i = 0
    sents = []
    punt_list = ':：，,.。、'.decode("utf-8")
#     print len(punt_list),punt_list
#     print len(words)
#     print words
    for word in words:
#         print word,
        if word in punt_list: #检查标点符号下一个字符是否还是标点
#             print chardet.detect(words[start:i+1])
            sents.append(words[start:i])
            start = i+1
            i += 1
        else:
            i += 1
    if start < len(words):
#         print words[start:]
        sents.append(words[start:])
    return sents

def cut_text(contents):
    """
    turn a text  paragraph  into a separate unit 
    """
    seg_units =[]
    for sentence in contents: 
#         print sentence+"|||"
        cut_list=cut_sentence(sentence)
#         print cut_list,
        seg_units.extend(cut_list)
    return seg_units

def extract_candidates_words(str_list, dict):
#     print string 
    units=cut_text(str_list)
#     print units
    for unit in units:
#         print unit
        dict.update(extract_all_n_gram(unit))

def my_segmentation(path,mylogger1):
    
    threshold1=0.1
    threshold2=0.9
    path_dir = os.listdir(path)
    dict={}
    cnt_txt=0
    for dir in path_dir:
        
        child = os.path.join(path,dir)
        f =open(child,"r")
        html = f.read()
        html_contents=extract_str_list(html.decode("gb2312").encode("utf-8"))
        extract_candidates_words(html_contents, dict)
        cnt_txt+=1
#         if cnt_txt>=5:
#             break
    sum_all_candidates_num=0
    for value in dict.values():
#         print value,
        sum_all_candidates_num+=value
        
    print sum_all_candidates_num   
    word_freq_list=sorted(dict.iteritems(),key=lambda asd:asd[1],reverse=False)
    for item in word_freq_list:
        mylogger1.info(item[0]+"\t"+str(item[1]))
         


def main():
    path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
    print path_project
#     usr_dict_path = path_project+"/resourse/toothICD10_freq"
    log_path = path_project+'/tmp/log'
    path=path_project+"/input"
#     log(log_path).info("this is a test")
#     logger =mylogger.log_file(log_path)
    logger1 = mylogger.log_console_and_file(log_path)
    my_segmentation(path,logger1) 
      
if __name__=="__main__":
    test()


    
        
        
        
        