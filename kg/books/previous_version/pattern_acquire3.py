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
from _collections import defaultdict


path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
path_log_output=path_project+os.sep+"output"+os.sep+"log_pattern_acquire_auto3_3.txt"
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
    '''
    when the start<size, we fetch the window util start from 0,
    when the start>=size, we fetch the window util start from start-size,
    '''
    for i in range(1):
#     for i in range(size):
        if start<size and start<len(definition_tokens):
            can_pos_set=get_can_pos_set(start)
            window=definition_tokens[:start]
        elif start>=size and start<len(definition_tokens):
            can_pos_set=get_can_pos_set(size)
            window=definition_tokens[start-size:start]
            
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
        if len(pattern_can.split('+'))>=int(re.findall('\$(\d+)',pattern_can)[0]) and \
        exist_special_token(pattern_can)==False and\
        len(pattern_can.split('+'))>=2:
#             print pattern_can
            patterns_can_filter1.append(pattern_can)
    return patterns_can_filter1

def caculate_freq_single(pattern_cmp,patterns):    
    cnt=0
    for pattern in patterns:
        if pattern.find(pattern_cmp[:pattern_cmp.index('$')])!=-1:
            cnt+=1
    return cnt    
    
def caculate_pattern_freq(patterns_can):
    pattern2freq={}
    for pattern_can in patterns_can:
        freq=caculate_freq_single(pattern_can,patterns_can)
        pattern2freq[pattern_can]=freq
    return pattern2freq

def most_common(patterns_dict,n):
    sorted_patterns=sorted(patterns_dict.iteritems(),key=lambda asd:asd[1],reverse=True)
    return sorted_patterns[:n+1]
        
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
          
    filter_patterns2freq=most_common(caculate_pattern_freq(filter_patterns1),len(filter_patterns1)/20)
    logger.info('filter_patterns2 size: '+str(len(filter_patterns2freq)))
    logger.info('filter_patterns2: '+str(truple2dict(filter_patterns2freq)))
    
    return truple2dict(filter_patterns2freq)

def is_all_POS(pattern):
    pattern_words=pattern[:pattern.index('$')].split('+')
    for pattern_word in pattern_words:
        if '{' not in pattern_word:
            return False
    return True
        
def get_filter_pattern_seq(patterns_can):
    filter1=[]
    for pattern_can in patterns_can:
        if exist_special_token(pattern_can)==False and len(pattern_can.split('+'))>=2 and is_all_POS(pattern_can)==False:
#         if len(pattern_can.split('+'))>=2:
            filter1.append(pattern_can)
    
    filter2=[]       
    for pattern_can in filter1:
        if len(pattern_can.split('+'))>=int(re.findall('\$(\d+)',pattern_can)[0]):
            filter2.append(pattern_can)

    filter_patterns2freq=most_common(caculate_pattern_freq(filter2),len(filter2)/10)
    
    return filter_patterns2freq
    

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
#                 if attribute_name in ['isA','isThe','purpose','used_for']:
#                     continue
#                 if attribute_name in ['isA','isThe']:
#                     continue
                if attribute_name in attribute2patterns_can_all.keys():
                    attribute2patterns_can_all[attribute_name].extend(list(set(prefixs)))
                else:
                    attribute2patterns_can_all[attribute_name]=list(set(prefixs))
#                 logger.info('\n')
#             logger.info('\n')
    
    attribute2patterns_all={}      
    for attribue,patterns in attribute2patterns_can_all.iteritems():
        print 'attribue: '+attribue
        logger.info('final attribue: %s\n'%attribue)
        logger.info('patterns original length: '+str(len(patterns)))
        logger.info('patterns original:　%s\n'%str(patterns))
        filter_patterns=get_filter_pattern_seq(patterns)
        attribute2patterns_all[attribue]=filter_patterns
        
#         logger.info('final attribue: %s\n'%attribue)
        logger.info('final pattern:　%s\n'%str(filter_patterns))
    pattern2single_attribute=filter_efficient(attribute2patterns_all)
    return  pattern2single_attribute
  
  
def filter_efficient(attribute2patterns_all):
    '''
            这个函数是将不能唯一属于一个属性的pattern过滤掉
    '''
    attribute2single_pattterns=valuelist2values(attribute2patterns_all)
    pattern2attributes=defaultdict(list)
    pattern2whole_pattern={}
    for attribute2single_patttern in attribute2single_pattterns: 
        attribute=attribute2single_patttern[0]
        pattern=attribute2single_patttern[1]
#         print pattern
        pattern2attributes[pattern[0][:pattern[0].index('$')]].append(attribute)
        pattern2whole_pattern[pattern[0][:pattern[0].index('$')]]=pattern[0]+'@'+str(pattern[1])
        
    pattern2single_attributes={}    
    for pattern in pattern2attributes.keys():
        if len(pattern2attributes[pattern])>=2:
            pattern2attributes.pop(pattern)
        else:
            pattern2single_attributes[pattern]=pattern2attributes[pattern][0]
            
    pattern_whole2single_attributes={}
    for pattern,single_attribute in pattern2single_attributes.iteritems():
        pattern_whole2single_attributes[pattern2whole_pattern[pattern]]=single_attribute
    return pattern_whole2single_attributes

def merge_pattern_all(pattern2single_attributes):
    '''
             此方法用于合并pattern，并使用合并后的pattern 重新计算频率
    '''
    attribute2patterns=defaultdict(list)
    for pattern,attribute in pattern2single_attributes.iteritems():
        attribute2patterns[attribute].append(pattern)
    
    attribute2patterns_merge={}
    for attribute,patterns in attribute2patterns.iteritems():
        attribute2patterns_merge[attribute]=merge_pattern(patterns)
    
    pattern2attribute=defaultdict(list)
    for attribute,patterns in attribute2patterns_merge:
        for pattern in patterns:
            pattern2attribute[pattern]=attribute
    return pattern2attribute

def merge_pattern(patterns):
    patterns_can=[[]] 
    for i in range(len(patterns)):
        pos_i=contain_pattern(patterns[i],patterns_can)
        if pos_i==-1:
            pattern_can_i=set([])
            pattern_can_i.add(patterns[i])
            patterns_can.append(pattern_can_i)
        pos_i=contain_pattern(patterns[i],patterns_can)
#         freq_i=re.findall('@(\d+)', patterns[i])[0]
        for j in range(i+1):
#             freq_j=re.findall('@(\d+)', patterns[j])[0]
            if len(patterns[i].split('+'))==len(patterns[j].split('+')) and has_commom_word(patterns[i],patterns[j]):
                pos_j=contain_pattern(patterns[j],patterns_can)
                if pos_j!=-1:
                    patterns_can[pos_i].add(patterns[j])
                    
    for x in patterns_can:
        print x

def contain_pattern(pattern_cmp,patterns_list_list):
    for i in range(len(patterns_list_list)):
        for pattern in patterns_list_list[i]:
            if len(pattern_cmp.split('+'))==len(pattern.split('+')) and has_commom_word(pattern_cmp,pattern):
#             if pattern in patterns_list_list[i][j]:
                return i
    return -1     
    
    
def has_commom_word(pattern1,pattern2):
    pattern1_words=pattern1[:pattern1.index('$')].split('+')
    pattern2_words=pattern2[:pattern2.index('$')].split('+')
    for i in range(len(pattern1_words)):
        if '{' in pattern1_words[i] or '{' in pattern2_words[i]:
            continue
        if pattern1_words[i]==pattern2_words[i]:
            return True
    return False
            
def valuelist2values(dict_can):   
    attribute2single_patttern=[]    
    for key,value_list in dict_can.iteritems():
        for value in value_list:
            attribute2single_patttern.append((key,value))
    return attribute2single_patttern
   
def sorted_by_attribute_pattern(pattern2attributes,path):
    attribute2patterns=defaultdict(list)
    for pattern,attribute in pattern2attributes.iteritems():
        attribute2patterns[attribute].append(pattern)
    
    pattern2attributes_sorted=[]
    for attribute,pattern_list in attribute2patterns.iteritems():
        pattern_list_sorted=sorted(pattern_list)
        for pattern in pattern_list_sorted:
            pattern2attributes_sorted.append((pattern,attribute))
        
    fp=codecs.open(path, 'w','utf-8')
    fp.write('{\n')
    for pattern2attribute in pattern2attributes_sorted:
        fp.write('  \"'+pattern2attribute[0]+'\": \"'+pattern2attribute[1]+'\",\n')
    fp.write('}')

def calculate_proprity2pattern(patterns):
    '''
    pos weigh 0.5, word weigh 1.0,
    '''
    data_new={}
    max_pattern_len=0
    for pattern in patterns.keys():
        if len(pattern.split("+"))>max_pattern_len:
            max_pattern_len=len(pattern.split("+"))
    print max_pattern_len       
    for pattern,attribute in patterns.iteritems():
#         print pattern
        pattern_words=pattern[:pattern.index('$')].split('+')
        prority=0.0
        for word in pattern_words:
            weigh_word=0.0
            if '|' in word:
                can_words=word.split('|')
                for can_word in can_words:
                    if '{' in can_word:
                        weigh_word+=1.0/(max_pattern_len+1)
                    else:
                        weigh_word+=1.0
                weigh_word=weigh_word/len(can_words)
            else:
                if '{' in word:
                    weigh_word=1.0/(max_pattern_len+1)
                else:
                    weigh_word=1.0
            prority+=weigh_word
#         prority=round(prority/len(pattern_words),2)
        prority=round(prority,2)
        pattern_new=pattern+'#'+str(prority)
        data_new[pattern_new]=attribute
    return data_new   
   
def main():
    path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
    path_data= path_project+os.sep+"input"+os.sep+"items_tagged_modified.json"
#     path_data= path_project+os.sep+"input"+os.sep+"items_tagged_modified_test.json"
    path_pattern= path_project+os.sep+"output"+os.sep+"Patterns_auto.json"
    path_pattern_sorted= path_project+os.sep+"output"+os.sep+"pattern_auto_sorted_by_attribute_pattern.json"
#     path_pattern_sorted_by_attribute=path_project+os.sep+"output"+os.sep+"pattern_auto_sorted_by_attribute.json"
    data=load_json(path_data)
    logger.info("loaded all the data")
    patterns=acquire_patterns(data)
    patterns_priority=calculate_proprity2pattern(patterns)
    logger.info("has acquired all the patterns")
    json.dump(patterns_priority, codecs.open(path_pattern, 'w','utf-8'),ensure_ascii=False,indent=2)
#     json.dump(dict_reverse(patterns), codecs.open(path_pattern_reverse, 'w','utf-8'),ensure_ascii=False,indent=2)
#     dict_sorted_value(dict_reverse(patterns),path_pattern_reverse_sorted)
    sorted_by_attribute_pattern(patterns_priority,path_pattern_sorted)
    logger.info("output over")


def test():
    tokens1=[(u'substance', 'NN'), (u'abuse', 'NN'), (u'is', 'VBZ'), (u'the', 'DT'), (u'misuse', 'NN'), (u'of', 'IN'), (u'legal', 'JJ'), (u'or', 'CC'), (u'illegal', 'JJ'), (u'substances', 'NNS'), (u'with', 'IN'), (u'the', 'DT'), (u'intent', 'NN'), (u'to', 'TO'), (u'alter', 'VB'), (u'some', 'DT'), (u'aspect', 'NN'), (u'of', 'IN'), (u'the', 'DT')]
    tokens2=[(u'the', 'DT'), (u'misuse', 'NN'), (u'of', 'IN'), (u'legal', 'JJ'), (u'or', 'CC'), (u'illegal', 'JJ'), (u'substances', 'NNS')]
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
    patterns=["according+to$0@15#2.0","according+{TO}$0@15#1.17","named+according+to$0@7#3.0","named+{VBG}+{TO}$0@7#1.33","{VBN}+according+{TO}$0@7#1.33",]
    patterns=["are+the+incorporates$0@7#3.0",
  "are+the+{NNS}$0@7#2.17",
  "are+{DT}+incorporates$0@7#2.17",
  "base+made+of$0@7#3.0",
  "base+{VBN}+of$0@7#2.17",
  "base+{VBN}+{IN}$0@7#1.33",
  "cast+made+of$0@7#3.0",
  "cast+made+{IN}$0@7#2.17",
  "cast+{NN}+of$0@7#2.17",
  "composed+of$0@23#2.0",
  "composed+primarily+of$0@7#3.0",
  "composed+primarily+{IN}$0@7#2.17",
  "composed+{IN}$0@23#1.17",
  "liquid+are$0@15#2.0",
  "liquid+{VBP}$0@15#1.17",
  "made+of$0@30#2.0",
  "primarily+of$0@15#2.0",
  "primarily+{IN}$0@15#1.17",
  "the+incorporates$0@15#2.0",
  "the+liquid+{VBP}$0@7#2.17",
  "the+{NNS}$0@15#1.17",
  "the+{NN}+are$0@7#2.17",
  "the+{NN}+{VBP}$0@7#1.33",
  "{DT}+incorporates$0@15#1.17",
  "{DT}+liquid+{VBP}$0@7#1.33",
  "{NN}+are$0@27#1.17",
  "{NN}+composed+of$0@7#2.17",
  "{NN}+made+of$0@14#2.17",
  "{NN}+{VBN}+of$0@14#1.33",
  "{RB}+of$0@15#1.17",
  "{VBN}+of$0@38#1.17",
  "{VBN}+primarily+of$0@7#2.17",
  "{VBN}+{RB}+of$0@7#1.33",
  "{VBP}+the+incorporates$0@7#2.17",
  "{VBP}+the+{NNS}$0@7#1.33",]
    merge_pattern(patterns)

def test3():
    attribute_value_tokens=[(u'misuse', 'NN'), (u'of', 'IN'), (u'legal', 'JJ')]
    definition_tokens=[(u'substance', 'NN'), (u'abuse', 'NN'), (u'is', 'VBZ'), (u'the', 'DT'), (u'misuse', 'NN'), (u'of', 'IN'), (u'legal', 'JJ'), (u'or', 'CC'), (u'illegal', 'JJ'), (u'substances', 'NNS')]
    
    for (prefixs,num) in get_fix_chunk(5,get_tokens(attribute_value_tokens),get_tokens(definition_tokens)):
        for token in prefixs:
            print token.show(),
        print '\n'
        
if __name__=='__main__':
    start = datetime.datetime.now()
    logger.info(start)
    print start
#     main()
#     test()
#     test1()
    test2()
#     test3()
    end = datetime.datetime.now()
    logger.info(end)
    print end
    logger.info("cost time: "+str((end - start).microseconds))
    print str((end - start).seconds)+' s'