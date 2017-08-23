#coding=utf-8
'''
Created on 2017��4��10��

@author: FeiFei
'''
import os
from kg.util.mylogger import log_console_and_file
from kg.util.file import load_json
import codecs
import json
import nltk
from kg.books.analysis_items import extract_item_properties
from collections import Counter
from itertools import product
from kg.books.basic_obj import Token
import datetime
import re
from kg.util.string import cut_token_list, cut_truple_list


path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
path_log_output=path_project+os.sep+"output"+os.sep+"log_pattern_acquire_auto2_5.txt"
logger=log_console_and_file(path_log_output)

prefix_window_size=5
post_window_size=2
support_min=0

       
def tokens_show(tokens):
    truples=[]
    for token in tokens:
        truples.append(token.show())
    return truples

def get_can_pos_set(size):
    can_pos_set=[]
    for i in range(size):
        can_pos=[]
        for j in range(size):
            if i<=j:
                can_pos.append(j)
        can_pos_set.append(can_pos)
    return can_pos_set

def get_fix_chunk(size,attribute_value_tokens,definition_tokens):
    match_pos=get_match_pos(attribute_value_tokens,definition_tokens)
    can_pos_set=[]
    start=match_pos[0]
    if start==-1:
        logger.info('this value cannot match')
        logger.info('definition:\n'+str(tokens_show(definition_tokens)))
        logger.info('attribute_value:\n'+str(tokens_show(attribute_value_tokens)))
        return []
    window=[]
    prefixs2intersect=[]
    for i in range(size):
        if start<size and start<len(definition_tokens):
            can_pos_set=get_can_pos_set(size)
            window=definition_tokens[:size+1]
        elif start>=size and start<len(definition_tokens):
            can_pos_set=get_can_pos_set(size)
            window=definition_tokens[start-size:start+1]
            
        for can_pos in can_pos_set:
            prefix=[]
            for pos in can_pos:
                prefix.append(window[pos])
            prefixs2intersect.append((prefix,i))
        start=start+1
    return  prefixs2intersect 

def get_fix(size,attribute_value_tokens,definition_tokens): 
    chunks=cut_token_list(attribute_value_tokens,[Token(';', ':')])
    prefixs2intersect=[]
    for chunk in chunks:
        prefixs2intersect.extend(get_fix_chunk(size,chunk,definition_tokens))
    return prefixs2intersect

def token2list(token):
    return [token.word,'{'+token.pos+'}']

def get_string_fix(truple_list,fix_combinaitons,intersect):
    for truple in truple_list:
        fix_combinaiton=''
        for i in range(len(truple)):
            fix_combinaiton+=truple[i]+'+'
        fix_combinaitons.append(fix_combinaiton[:-1]+'$'+str(intersect)) 
        
def get_combination_fix(fixs_tokens2intersect):
    fix_combinaitons=[]
    for  (fixs_token,inersect) in fixs_tokens2intersect:
        if len(fixs_token)==1:
            truple_list=[x for x in product(token2list(fixs_token[0]))]
            get_string_fix(truple_list,fix_combinaitons,inersect)  
        elif len(fixs_token)==2:
            truple_list=[x for x in product(token2list(fixs_token[0]),token2list(fixs_token[1]))]
            get_string_fix(truple_list,fix_combinaitons,inersect)
        elif len(fixs_token)==3:
            truple_list=[x for x in product(token2list(fixs_token[0]),token2list(fixs_token[1]),token2list(fixs_token[2]))]
            get_string_fix(truple_list,fix_combinaitons,inersect)
        elif len(fixs_token)==4:
            truple_list=[x for x in product(token2list(fixs_token[0]),token2list(fixs_token[1]),token2list(fixs_token[2]),token2list(fixs_token[3]))]    
            get_string_fix(truple_list,fix_combinaitons,inersect)
        elif len(fixs_token)==5:
            truple_list=[x for x in product(token2list(fixs_token[0]),token2list(fixs_token[1]),token2list(fixs_token[2]),token2list(fixs_token[3]),token2list(fixs_token[4]))]    
            get_string_fix(truple_list,fix_combinaitons,inersect)
    return fix_combinaitons

def is_match_tokens2tokens(tokens1,tokens2):
    '''
    whether two tokens are equal, 
    '''
    for i in range(len(tokens1)):
        if tokens1[i].equal(tokens2[i])==False:
            return False
    return True

def find_prefix(tokens,i):
    '''find the prefixs of a string'''
    prefix=[]
    for j in range(1,i+1):
        prefix.append(tokens[:j])
    return prefix

def find_postfix(tokens,i):
    '''find the postfixs of a string'''
    postfix=[]
    for j in range(1,i+1):
        postfix.append(tokens[j:i+1])
    return postfix

def caculate_partial_table(tokens):
    '''caculate the jump table to decide the step of a word when the word is not a match'''
    if len(tokens)==1:
        return [0]
    ret = [0] 
    for i in range(1,len(tokens)):
        prefix=find_prefix(tokens,i)
        postfix=find_postfix(tokens,i)
        prefix.sort(key=lambda x:len(x))
        postfix.sort(key=lambda x:len(x))
        common=[]
        for i in range(len(prefix)):
            if is_match_tokens2tokens(prefix[i],postfix[i]):
                common.append(len(prefix[i]))
        if len(common)==0:
            ret.append(0)
        else:
            ret.append(max(common))
    return ret  

def KMP_match(attribute_value_tokens,definition_tokens):
    table=caculate_partial_table(attribute_value_tokens)
    m=len(definition_tokens)
    n=len(attribute_value_tokens)
    cur=0
    while cur<=m-n:  
        for i in range(n):
            if definition_tokens[i+cur].word!=attribute_value_tokens[i].word:
                cur += max(i - table[i-1], 1)#有了部分匹配表,我们不只是单纯的1位1位往右移,可以一次移动多位  
                break  
        else:  
            return  cur
    return -1 

def get_match_pos(attribute_value_tokens,tokens):
    start=KMP_match(attribute_value_tokens,tokens)
    end=start+len(attribute_value_tokens)
    return (start,end)

def get_tokens(pos_words):
    tokens=[]
    for word2tag in pos_words:
        token=Token(word2tag[0],word2tag[1])
        tokens.append(token)
    return tokens

def exist_special_token(pattern):
    special_token=['.','{.}',',','{,}',';','{:}']
    for token in pattern[:pattern.index('$')].split('+'):
        if token in special_token:
            return True
    return False

def truple2dict(truple_list):
    dic={}
    for truple in truple_list:
        dic[truple[0]]=truple[1]
    return dic

def filter1(patterns_can):
    patterns_can_filter1=[]
    for pattern_can in patterns_can:
#         print len(pattern_can.split('+'))>=int(re.findall('\$(\d+)',pattern_can)[0])
#         print exist_special_token(pattern_can)
        if len(pattern_can.split('+'))>=int(re.findall('\$(\d+)',pattern_can)[0]) and exist_special_token(pattern_can)==False:
#             print pattern_can
            patterns_can_filter1.append(pattern_can)
    return patterns_can_filter1

def filter3(pattern2priority):
    filter_patterns3={}
    sorted_pattern_priority_can=sorted(pattern2priority.iteritems(),key=lambda asd:asd[1],reverse=True)
    for x in sorted_pattern_priority_can[:len(sorted_pattern_priority_can)/3]:
        filter_patterns3[x[0]]=x[1]
    return filter_patterns3

def get_filter_pattern(patterns_can):
    filter_patterns1=filter1(patterns_can)
    logger.info('filter_patterns1 size: '+str(len(filter_patterns1)))
    logger.info('patterns_can_filter1: '+str(filter_patterns1))  
          
    c_pattern=Counter(filter_patterns1)
    logger.info('c_pattern size: '+str(len(c_pattern)))
#     logger.info('c_pattern: '+str(c_pattern))
    
    filter_patterns2=c_pattern.most_common(len(filter_patterns1)/20)
    logger.info('filter_patterns2 size: '+str(len(filter_patterns2)))
#     logger.info('filter_patterns2: '+str(truple2dict(filter_patterns2)))
    
    pattern2priority=calculate_proprity(truple2dict(filter_patterns2))
    logger.info('pattern2priority size: '+str(len(pattern2priority)))
#     logger.info('pattern2priority: '+str(pattern2priority))
    
    filter_patterns3=filter3(pattern2priority)
    logger.info('filter_patterns3 size: '+str(len(filter_patterns3)))
    logger.info('filter_patterns3: '+str(filter_patterns3))    
    return filter_patterns3

def calculate_proprity(patterns_can):
    '''
    pos weigh 0.5, word weigh 1.0,
    '''
    max_pattern_len=0
    for pattern_can in patterns_can.keys():
        if len(pattern_can.split("+"))>max_pattern_len:
            max_pattern_len=len(pattern_can.split("+"))
#     print max_pattern_len   
    pattern2priority={}    
    for pattern,num in patterns_can.iteritems():
#         print pattern
        prority=0.0
        pattern_words=pattern[:pattern.index('$')].split('+')
        for word in pattern_words:
            weigh_word=0.0
            if '{' in word:
                weigh_word=1.0/(max_pattern_len+1)
            else:
                weigh_word=1.0
            prority+=weigh_word
#         prority=round(prority/len(pattern_words),2)
        prority=round(prority*num,2)
        pattern2priority[pattern]=prority
    return pattern2priority

def merge_pattern(filter_patterns):
    for pattern in filter_patterns:
        words=pattern.split('+')
        
    
def acquire_patterns(data):
    attribute2patterns_can_all={}
    for item in data:
        concept,pronunciation,pos2definition=extract_item_properties(item)
#         logger.info('concept: %s'%concept)
        for pos2def in pos2definition:
            definition=pos2def['definition']
#             logger.info('definition: \n%s'%definition)
            text=nltk.word_tokenize(definition)
            definition_pos=nltk.pos_tag(text)
#             logger.info('definition_pos: \n%s'%definition_pos)
            definition_tokens=get_tokens(definition_pos)
            attributes=pos2def['attributes']
            for attribute_name,attribute_value in attributes.iteritems():
#                 logger.info('attribute_name: %s'%attribute_name)
                attribute_value_text=nltk.word_tokenize(attribute_value)
                attribute_value_tokens=nltk.pos_tag(attribute_value_text)
#                 logger.info('attributes value token: %s'%attribute_value_tokens)
                attribute_tokens=get_tokens(attribute_value_tokens)
                prefixs_tokens2intersect=get_fix(prefix_window_size,attribute_tokens,definition_tokens)
#                 logger.info('prefixs_token: \n%s'%str([str((token.word,token.pos))+": "+str(intersect) for (tokens,intersect) in prefixs_tokens2intersect for token in tokens]))
                prefixs=get_combination_fix(prefixs_tokens2intersect)
#                 logger.info('prefix: \n%s'%str(prefixs))
                if attribute_name in attribute2patterns_can_all.keys():
                    attribute2patterns_can_all[attribute_name].extend(list(set(prefixs)))
                else:
                    attribute2patterns_can_all[attribute_name]=list(set(prefixs))
#                 logger.info('\n')
#             logger.info('\n')
    
    attribute2patterns_all={}      
    for attribue,patterns in attribute2patterns_can_all.iteritems():
        logger.info('final attribue: %s\n'%attribue)
        logger.info('patterns original length: '+str(len(patterns)))
#         logger.info('patterns original:　%s\n'%str(patterns))
        filter_patterns=get_filter_pattern(patterns)
        attribute2patterns_all[attribue]=filter_patterns
#         logger.info('final attribue: %s\n'%attribue)
        logger.info('final pattern:　%s\n'%str(filter_patterns))
    return  attribute2patterns_all
       
def dict_reverse(dict_can):
    dict_new={}                
    for key,value_list in dict_can.iteritems():
        for value in value_list:
            dict_new[value]=key
    return dict_new

def dict_sorted_value(dict_patterns,path):
    fp=codecs.open(path, 'w','utf-8')
    sorted_patterns=sorted(dict_patterns.iteritems(),key=lambda asd:asd[1],reverse=False)
    fp.write('{\n')
    for sorted_pattern in sorted_patterns:
        fp.write('  \"'+sorted_pattern[0]+'\": \"'+sorted_pattern[1]+'\",\n')
    fp.write('}')
    
def main():
    path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
    path_data= path_project+os.sep+"input"+os.sep+"items_tagged_modified.json"
#     path_data= path_project+os.sep+"input"+os.sep+"items_tagged_modified_test.json"
    path_pattern= path_project+os.sep+"output"+os.sep+"Patterns_auto.json"
    path_pattern_reverse= path_project+os.sep+"output"+os.sep+"Patterns_auto_reverse.json"
    path_pattern_reverse_sorted=path_project+os.sep+"output"+os.sep+"Patterns_auto_reverse_sorted.json"
    data=load_json(path_data)
    logger.info("loaded all the data")
    patterns=acquire_patterns(data)
    logger.info("has acquired all the patterns")
    json.dump(patterns, codecs.open(path_pattern, 'w','utf-8'),ensure_ascii=False,indent=2)
    json.dump(dict_reverse(patterns), codecs.open(path_pattern_reverse, 'w','utf-8'),ensure_ascii=False,indent=2)
    dict_sorted_value(dict_reverse(patterns),path_pattern_reverse_sorted)
    logger.info("output over")

def test():
    tokens1=[(u'substance', 'NN'), (u'abuse', 'NN'), (u'is', 'VBZ'), (u'the', 'DT'), (u'misuse', 'NN'), (u'of', 'IN'), (u'legal', 'JJ'), (u'or', 'CC'), (u'illegal', 'JJ'), (u'substances', 'NNS'), (u'with', 'IN'), (u'the', 'DT'), (u'intent', 'NN'), (u'to', 'TO'), (u'alter', 'VB'), (u'some', 'DT'), (u'aspect', 'NN'), (u'of', 'IN'), (u'the', 'DT')]
    tokens2=[(u'the', 'DT'), (u'misuse', 'NN'), (u'of', 'IN'), (u'legal', 'JJ'), (u'or', 'CC'), (u'illegal', 'JJ'), (u'substances', 'NNS')]
#     get_tokens(tokens2)
#     print caculate_partial_table(get_tokens(tokens2))
#     for token_list in get_fix(5, get_tokens(tokens2), get_tokens(tokens1)):
#         for token in token_list:
#             print token.show(),
#         print 
    
    for fix in get_combination_fix([fix for fix in get_fix(5, get_tokens(tokens2), get_tokens(tokens1))]):
        print fix 
        
  
def test1():
    path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
    path_data= path_project+os.sep+"input"+os.sep+"items_tagged_modified_test.json"
#     path_data= path_project+os.sep+"input"+os.sep+"items_tagged_modified_test.json"
    path_pattern= path_project+os.sep+"output"+os.sep+"patterns_auto_test.json"
    data=load_json(path_data)
    logger.info("loaded all the data")
    patterns=acquire_patterns(data)
    logger.info("has acquired all the patterns")
    json.dump(patterns, codecs.open(path_pattern, 'w','utf-8'),ensure_ascii=False,indent=2)
    logger.info("output over")

def test2():
    patterns_can=['The+{NN}+{CC}+resistance$4','{.}+{DT}$1']
    filter1(patterns_can) 

if __name__=='__main__':
    start = datetime.datetime.now()
    logger.info(start)
    print start
    main()
#     test()
#     test1()
#     test2()
    end = datetime.datetime.now()
    logger.info(end)
    print end
    logger.info("cost time: "+str((end - start).microseconds))
    print (end - start).seconds