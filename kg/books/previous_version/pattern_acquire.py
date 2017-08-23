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


path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
path_log_output=path_project+os.sep+"output"+os.sep+"log_pattern_acquire_auto1.txt"
logger=log_console_and_file(path_log_output)

prefix_window_size=3
post_window_size=2
support_min=0

       
def tokens_show(tokens):
    truples=[]
    for token in tokens:
        truples.append(token.show())
    return truples

def get_can_pos_set(fix,size):
    can_pos_set=[]
    if fix=='pre':
        for i in range(size):
            can_pos=[]
            for j in range(size):
                if i<=j:
                    can_pos.append(j)
            can_pos_set.append(can_pos)
    elif fix=='post':
        for i in range(size):
            can_pos=[]
            for j in range(size):
                if i>=j:
                    can_pos.append(j)
            can_pos_set.append(can_pos)       
    else:
        print 'It is not pre or post'
    return can_pos_set
        
def get_fix(fix,size,attribute_value_tokens,definition_tokens): 
    match_pos=get_match_pos(attribute_value_tokens,definition_tokens)
    can_pos_set=[]
    start=match_pos[0]
    end=match_pos[1]
    if fix=='pre':
        window=[]
        if start<size:
            can_pos_set=get_can_pos_set('pre',start)
            window=definition_tokens[:start]
        else:
            can_pos_set=get_can_pos_set('pre',size)
            window=definition_tokens[start-size:start]
        prefixs=[]
        for can_pos in can_pos_set:
            prefix=[]
            for pos in can_pos:
                prefix.append(window[pos])
            prefixs.append(prefix)
        return  prefixs  
    elif fix=='post':
        window=[]
        if end==len(definition_tokens):
            window=[]
            return []
        if len(definition_tokens)-end-1<size:
            can_pos_set=get_can_pos_set('post',len(definition_tokens)-1-end)
            window=definition_tokens[end:]
        else:
            can_pos_set=get_can_pos_set('post',size)
            window=definition_tokens[end:end+size]
        postfixs=[]
        for can_pos in can_pos_set:
            postfix=[]
            for pos in can_pos:
                postfix.append(window[pos])
            postfixs.append(postfix) 
        return  postfixs  
    else:
        print 'It is not pre or post'  
 

def token2list(token):
    return [token.word,token.pos]

def get_string_fix(truple_list,fix_combinaitons):
    for truple in truple_list:
        fix_combinaiton=''
        for i in range(len(truple)):
            fix_combinaiton+=truple[i]+'+'
        fix_combinaitons.append(fix_combinaiton) 
        
def get_combination_fix(fixs_tokens):
    fix_combinaitons=[]
    for i in range(len(fixs_tokens)):
        if len(fixs_tokens[i])==1:
            truple_list=[x for x in product(token2list(fixs_tokens[i][0]))]
            get_string_fix(truple_list,fix_combinaitons)  
        elif len(fixs_tokens[i])==2:
            truple_list=[x for x in product(token2list(fixs_tokens[i][0]),token2list(fixs_tokens[i][1]))]
            get_string_fix(truple_list,fix_combinaitons)
        elif len(fixs_tokens[i])==3:
            truple_list=[x for x in product(token2list(fixs_tokens[i][0]),token2list(fixs_tokens[i][1]),token2list(fixs_tokens[i][2]))]
            get_string_fix(truple_list,fix_combinaitons)
        elif len(fixs_tokens[i])==4:
            truple_list=[x for x in product(token2list(fixs_tokens[i][0]),token2list(fixs_tokens[i][1]),token2list(fixs_tokens[i][2]),token2list(fixs_tokens[i][3]))]    
            get_string_fix(truple_list,fix_combinaitons)
    return fix_combinaitons
 
def get_combination_pattern(prefixs,postfixs):
    pattern_can=[]
    if len(prefixs)==0 and len(postfixs)!=0:
        for truple in [x for x in product(postfixs)]:
            pattern_can.append('...+'+truple[0])
    elif len(prefixs)!=0 and len(postfixs)==0:
        for truple in [x for x in product(prefixs)]:
            pattern_can.append(truple[0]+'...+')
    elif len(prefixs)==0 and len(postfixs)==0:
        return []
    else:
        for truple in [x for x in product(prefixs,postfixs)]:
            pattern_can.append(truple[0]+'...+'+truple[1])
    return pattern_can


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
            if definition_tokens[i+cur].word==attribute_value_tokens[i].word:
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

def get_filter_pattern(patterns_can):
    c_pattern=Counter(patterns_can)
    filter_patterns=[]
    for pattern,num in c_pattern.iteritems():
#         print float(num)/len(patterns_can)
        if float(num)/len(patterns_can)>support_min:
            filter_patterns.append(pattern)
    return filter_patterns

def merge_pattern(filter_patterns):
    for pattern in filter_patterns:
        words=pattern.split('+')
        
    
def acquire_patterns(data):
    attribute2patterns_can_all={}
    for item in data:
        concept,pronunciation,pos2definition=extract_item_properties(item)
        logger.info('concept: %s'%concept)
        for pos2def in pos2definition:
            definition=pos2def['definition']
            logger.info('definition: \n%s'%definition)
            text=nltk.word_tokenize(definition)
            definition_pos=nltk.pos_tag(text)
            logger.info('definition_pos: \n%s'%definition_pos)
            definition_tokens=get_tokens(definition_pos)
            attributes=pos2def['attributes']
            for attribute_name,attribute_value in attributes.iteritems():
                logger.info('attribute_name: %s'%attribute_name)
                attribute_value_text=nltk.word_tokenize(attribute_value)
                attribute_value_tokens=nltk.pos_tag(attribute_value_text)
                logger.info('attributes value token: %s'%attribute_value_tokens)
                attribute_tokens=get_tokens(attribute_value_tokens)
                prefixs_tokens=get_fix('pre',prefix_window_size,attribute_tokens,definition_tokens)
                logger.info('prefixs_token: \n%s'%str([(token.word,token.pos) for tokens in prefixs_tokens for token in tokens]))
#                 postfixs_tokens=get_fix('post',prefix_window_size,attribute_tokens,definition_tokens)
#                 logger.info('postfixs_token: \n%s'%str([(token.word,token.pos) for tokens in postfixs_tokens for token in tokens]))
                prefixs=get_combination_fix(prefixs_tokens)
                logger.info('prefix: \n%s'%str(prefixs))
#                 postfixs=get_combination_fix(postfixs_tokens)
#                 logger.info('postfix: \n%s'%str(postfixs))

#                 logger.info('all candidate patterns: \n%s'%str(patterns))
#                 if attribute_name in attribute2patterns_can_all.keys():
#                     attribute2patterns_can_all[attribute_name].extend(patterns)
#                 else:
#                     attribute2patterns_can_all[attribute_name]=patterns
                logger.info('\n')
            logger.info('\n')
    
    attribute2patterns_all={}      
    for attribue,patterns  in attribute2patterns_can_all.iteritems():
        filter_patterns=get_filter_pattern(patterns)
        attribute2patterns_all[attribue]=filter_patterns
        logger.info('final attribue: %s\n'%attribue)
        logger.info('final pattern:　%s\n'%str(filter_patterns))
    return  attribute2patterns_can_all
       
                
                
def main():
    path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
    path_data= path_project+os.sep+"input"+os.sep+"items_tagged_modified.json"
#     path_data= path_project+os.sep+"input"+os.sep+"items_tagged_modified_test.json"
    path_pattern= path_project+os.sep+"output"+os.sep+"Patterns_auto.json"
    data=load_json(path_data)
    logger.info("loaded all the data")
    patterns=acquire_patterns(data)
    logger.info("has acquired all the patterns")
    json.dump(patterns, codecs.open(path_pattern, 'w','utf-8'),ensure_ascii=False,indent=2)
    logger.info("output over")

def test():
    tokens1=[(u'substance', 'NN'), (u'abuse', 'NN'), (u'is', 'VBZ'), (u'the', 'DT'), (u'misuse', 'NN'), (u'of', 'IN'), (u'legal', 'JJ'), (u'or', 'CC'), (u'illegal', 'JJ'), (u'substances', 'NNS'), (u'with', 'IN'), (u'the', 'DT'), (u'intent', 'NN'), (u'to', 'TO'), (u'alter', 'VB'), (u'some', 'DT'), (u'aspect', 'NN'), (u'of', 'IN'), (u'the', 'DT')]
    tokens2=[(u'the', 'DT'), (u'misuse', 'NN'), (u'of', 'IN'), (u'legal', 'JJ'), (u'or', 'CC'), (u'illegal', 'JJ'), (u'substances', 'NNS')]
#     get_tokens(tokens2)
#     print caculate_partial_table(get_tokens(tokens2))
    print get_fix('post', 3, get_tokens(tokens2), get_tokens(tokens1))
    for fix in get_combination_fix([fix for fix in get_fix('post', 3, get_tokens(tokens2), get_tokens(tokens1))]):
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
      
if __name__=='__main__':
    start = datetime.datetime.now()
    logger.info(start)
    print start
#     main()
#     test()
    test1()
    end = datetime.datetime.now()
    logger.info(end)
    print end
    logger.info("cost time: "+str((end - start).microseconds))
    print (end - start).seconds