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
path_log_output=path_project+os.sep+"output"+os.sep+"log_pattern_acquire_auto4_0.txt"
logger=log_console_and_file(path_log_output)

prefix_window_size=5
post_window_size=2
support_min=0


'''
the flowing methods aim to match attribute value and the definition
'''

def is_match_tokens2tokens(tokens1,tokens2):
    '''
    whether two tokens are equal, 
    '''
    for i in range(len(tokens1)):
#         if tokens1[i].equal(tokens2[i])==False:
        if tokens1[i][0]==tokens2[i][0]:
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
            if definition_tokens[i+cur][0]!=attribute_value_tokens[i][0]:
                cur += max(i - table[i-1], 1)#有了部分匹配表,我们不只是单纯的1位1位往右移,可以一次移动多位  
                break  
        else:  
            return  cur
    return -1

def KMP_match_token(attribute_value_tokens,definition_tokens):
    table=caculate_partial_table(attribute_value_tokens)
    m=len(definition_tokens)
    n=len(attribute_value_tokens)
    cur=0
    while cur<=m-n:  
        for i in range(n):
            if definition_tokens[i+cur][0]!=attribute_value_tokens[i][0] or definition_tokens[i+cur][1]!=attribute_value_tokens[i][1]:
                cur += max(i - table[i-1], 1)#有了部分匹配表,我们不只是单纯的1位1位往右移,可以一次移动多位  
                break  
        else:  
            return  cur
    return -1 

def get_match_pos(attribute_value_tokens,tokens):
    start=KMP_match(attribute_value_tokens,tokens)
    end=start+len(attribute_value_tokens)
    return (start,end)

def get_match_pos_token(attribute_value_tokens,tokens):
    start=KMP_match_token(attribute_value_tokens,tokens)
    end=start+len(attribute_value_tokens)
    return (start,end)

'''
the flowing methods aim to produce candidate patterns
'''
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
        logger.info('definition:\n'+str((definition_tokens)))
        logger.info('attribute_value:\n'+str((attribute_value_tokens)))
        return []
    window=[]
    prefixs2shift=[]
    '''
    when the start<size, we fetch the window util start from 0,
    when the start>=size, we fetch the window util start from start-size,
    '''
    for i in range(3):
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
            prefixs2shift.append((prefix,i))
        start=start+1
    return  prefixs2shift 

def get_fix(size,attribute_value_tokens,definition_tokens): 
    chunks=cut_truple_list(attribute_value_tokens,[(';', ':')])
    prefixs2shift=[]
    for chunk in chunks:
        prefixs2shift.extend(get_fix_chunk(size,chunk,definition_tokens))
    return prefixs2shift


def get_string_fix(truple_list,fix_combinaitons,shift,fixs_token):
    for truple in truple_list:
        fix_combinaiton='+'.join(truple)
        fix_combinaitons.append((fix_combinaiton+'$'+str(shift),fixs_token))
        
def truple2list(truple):
    return [truple[0],'{'+truple[1]+'}']
        
def get_combination_fix(fixs_tokens):
    patterns2fixs_tokens=[]
    print fixs_tokens[0]
    for  (fixs_token,shift) in fixs_tokens:
        truple_list=[]
        if len(fixs_token)==1:
            truple_list=[x for x in product(truple2list(fixs_token[0]))]
        elif len(fixs_token)==2:
            truple_list=[x for x in product(truple2list(fixs_token[0]),truple2list(fixs_token[1]))]
        elif len(fixs_token)==3:
            truple_list=[x for x in product(truple2list(fixs_token[0]),truple2list(fixs_token[1]),truple2list(fixs_token[2]))]
        elif len(fixs_token)==4:
            truple_list=[x for x in product(truple2list(fixs_token[0]),truple2list(fixs_token[1]),truple2list(fixs_token[2]),truple2list(fixs_token[3]))]    
        elif len(fixs_token)==5:
            truple_list=[x for x in product(truple2list(fixs_token[0]),truple2list(fixs_token[1]),truple2list(fixs_token[2]),truple2list(fixs_token[3]),truple2list(fixs_token[4]))]    
        get_string_fix(truple_list,patterns2fixs_tokens,shift,fixs_token) 
    return patterns2fixs_tokens


'''
the flowing methods aim to filter patterns according to some rules
'''
def exist_special_token(pattern):
    special_token=['.','{.}',',','{,}',';','{:}']
    for token in pattern[:pattern.index('$')].split('+'):
        if token in special_token:
            return True
    return False

def caculate_freq_single(pattern2fix_tokens_can_cmp,patterns2fix_tokens_can):    
    cnt=0
    for pattern2fix_tokens_can in patterns2fix_tokens_can:
        if pattern2fix_tokens_can[0].find(pattern2fix_tokens_can_cmp[0][:pattern2fix_tokens_can_cmp[0].index('$')])!=-1:
            cnt+=1
    return cnt    
    
def caculate_pattern_freq(patternTfix_tokens_cans):
    patternTfix_tokensTfreqs=[]
    for patternTfix_tokens_can in patternTfix_tokens_cans:
        freq=caculate_freq_single(patternTfix_tokens_can,patternTfix_tokens_cans)
        patternTfix_tokensTfreqs.append((patternTfix_tokens_can,freq))
    return patternTfix_tokensTfreqs

def most_common(pattern_tuples,n):
    sorted_patterns=sorted(pattern_tuples,key=lambda asd:asd[1],reverse=True)
    return sorted_patterns[:n+1]
        
def is_all_POS(pattern):
    pattern_words=pattern[:pattern.index('$')].split('+')
    for pattern_word in pattern_words:
        if '{' not in pattern_word:
            return False
    return True

def filter_special_token_A_full_POS(patterns2fix_tokens_can):
    filter1=[]
    for pattern2fix_tokens in patterns2fix_tokens_can:
        if exist_special_token(pattern2fix_tokens[0])==False and len(pattern2fix_tokens[0].split('+'))>=2 and is_all_POS(pattern2fix_tokens[0])==False:
#         if len(pattern_can.split('+'))>=2:
            filter1.append(pattern2fix_tokens)
    return filter1

def filter_wrong_shift(patterns2fix_tokens_can):
    filter2=[]       
    for pattern2fix_tokens in patterns2fix_tokens_can:
        if len(pattern2fix_tokens[0].split('+'))>=int(re.findall('\$(\d+)',pattern2fix_tokens[0])[0]):
            filter2.append(pattern2fix_tokens)
    return filter2

def get_filter_pattern_seq(patterns2fix_tokens_can):
    filter1=filter_special_token_A_full_POS(patterns2fix_tokens_can)
    filter2=filter_wrong_shift(filter1)
    filter_patternsTfix_tokensTfreq=most_common(caculate_pattern_freq(filter2),len(filter2)/10)
    return filter_patternsTfix_tokensTfreq
    
  
def filter_efficient(attribute2patternTfix_tokensTfreq_all):
    '''
            这个函数是将不能唯一属于一个属性的pattern过滤掉
    '''
    attributeTsingle_patternTfix_tokensTfreqs=valuelist2values(attribute2patternTfix_tokensTfreq_all)
    #pattern2attributes键为真实的pattern 值为该pattern映射的属性
    real_pattern2attributes=defaultdict(set)
    #pattern2whole_pattern键为真实的pattern 值为包含了后缀符号如$ # @的完整的pattern
    pattern2whole_pattern={}
    for attributeTsingle_patternTfix_tokensTfreq in attributeTsingle_patternTfix_tokensTfreqs: 
        attribute=attributeTsingle_patternTfix_tokensTfreq[0]
        patternTfix_tokensTfreq=attributeTsingle_patternTfix_tokensTfreq[1]
        patternTfix_tokens=patternTfix_tokensTfreq[0]
        pattern=patternTfix_tokens[0]
        freq=patternTfix_tokensTfreq[1]
#         print pattern
        real_pattern2attributes[pattern[:pattern.index('$')]].add(attribute)
        pattern2whole_pattern[pattern[:pattern.index('$')]]=(pattern+'@'+str(freq),patternTfix_tokens[1])
        
    pattern2single_attributes={}    
    for pattern in real_pattern2attributes.keys():
        if len(real_pattern2attributes[pattern])>=2:
            real_pattern2attributes.pop(pattern)
        else:
            #得到pattern和属性的唯一对应
            pattern2single_attributes[pattern]=list(real_pattern2attributes[pattern])[0]
            
    pattern_wholeTfix_tokensTsingle_attributes=[]
    for pattern,single_attribute in pattern2single_attributes.iteritems():
        pattern_wholeTfix_tokensTsingle_attributes.append((pattern2whole_pattern[pattern],single_attribute))
    
    
    return pattern_wholeTfix_tokensTsingle_attributes

def merge_pattern_all(patternTfix_tokensTattribute_tuples):
    '''
             此方法用于合并pattern，并使用合并后的pattern 重新计算频率
    '''
    attribute2patterns=defaultdict(list)
    for (patternTfix_tokens,attribute) in patternTfix_tokensTattribute_tuples:
        attribute2patterns[attribute].append(patternTfix_tokens)
    
    attribute2patterns_merge=[]
    for attribute,patternTfix_tokens_list in attribute2patterns.iteritems():
        attribute2patterns_merge.append((attribute,merge_pattern(patternTfix_tokens_list)))
    
    pattern2attribute=defaultdict(list)
    for attribute,patterns in attribute2patterns_merge:
        for pattern in patterns:
            pattern2attribute[pattern]=attribute
    return pattern2attribute

def merge_pattern(patternTfix_tokens_list):
    patterns_can=[[]] 
    for i in range(len(patternTfix_tokens_list)):
        pos_i=contain_pattern(patternTfix_tokens_list[i],patterns_can)
        if pos_i==-1:
            pattern_can_i=[]
            pattern_can_i.append(patternTfix_tokens_list[i])
            patterns_can.append(pattern_can_i)
        pos_i=contain_pattern(patternTfix_tokens_list[i],patterns_can)
#         freq_i=re.findall('@(\d+)', patterns[i])[0]
        for j in range(i+1):
#             freq_j=re.findall('@(\d+)', patterns[j])[0]
            if is_from_same_tokens(patternTfix_tokens_list[i],patternTfix_tokens_list[j]):
                pos_j=contain_pattern(patternTfix_tokens_list[j],patterns_can)
                if pos_j!=-1:
                    patterns_can[pos_i].append(patternTfix_tokens_list[j])
    
    patterns_can_remove_dup=[]      
    for patterns_common_POS in patterns_can:
        if len(patterns_common_POS)==0:
            continue
        patterns_common_POS_remove_dup=[]
        for pattern in patterns_common_POS:
            if is_contain_pattern(pattern,patterns_common_POS_remove_dup)==False:
                patterns_common_POS_remove_dup.append(pattern)
        patterns_can_remove_dup.append(patterns_common_POS_remove_dup)
    
    logger.info(str(patterns_can_remove_dup))
    merge_similar_patterns(patterns_can_remove_dup)
    
    final_patterns=[]
    for patterns_common_POS in patterns_can_remove_dup:
        final_patterns.append(choice_final_pattern(patterns_common_POS))
        
    return final_patterns

def merge_similar_patterns(patterns_can_remove_dup):
    '''
            合并属于同一个token list的pattern候选串
    '''
    remove_pos=[]
    m=len(patterns_can_remove_dup)-1
    while m >=0:
        tokens_m=patterns_can_remove_dup[m][0][1]
        n=m-1
        while n>=0:
            tokens_n=patterns_can_remove_dup[n][0][1]
            if len(tokens_m)<len(tokens_n):
                if get_match_pos_token(tokens_m, tokens_n)[0]!=-1:
                    if is_worse(tokens_m,tokens_n):
                        remove_pos.append(m)
                    else:
                        remove_pos.append(n)
            else:
                if get_match_pos_token(tokens_n, tokens_m)[0]!=-1:
                    if is_worse(tokens_n,tokens_m):
                        remove_pos.append(n)
                    else:
                        remove_pos.append(m)
            n-=1
        m-=1 
    
    for i in range(len(patterns_can_remove_dup)-1,-1,-1):
        if i in remove_pos:
            del patterns_can_remove_dup[i]
#     print patterns_can_remove_dup   
                    
def is_worse(tokens1,tokens2):
    flag=True
    start_pos=get_match_pos_token(tokens1, tokens2)[0]
    if start_pos!=0:
        #当短的pattern是长的pattern的中间部位
        if (start_pos+len(tokens1))!=len(tokens2):
            flag=is_add(tokens2[:start_pos]) or is_add(tokens2[len(tokens1):])
        #当短的pattern是长的pattern的后半段
        else:
            flag=is_add(tokens2[:start_pos])
    else:
        #当短的pattern是长的pattern的前半段
        flag=is_add(tokens2[len(tokens1):])
    return flag

def is_add(tokens):
    for token in tokens:
        if token[1] in ['NN','NNS','NNP','NNPS','CC','DT','JJ','JJR','JJS','PDT','POS','PRP','PRP$','RB','RBR','RBS','WDT','WP','WP$','WRB']:
            return False
#         if token[1] in ['VB','VBN','VBD','VBG','VBZ','VBP','IN']:
#             continue
    return True    

def choice_final_pattern(patternTtokens_list):
    tokens=patternTtokens_list[0][1]
    pattern_final=''
    for i in range(len(tokens)):
        if i==0:
            #对后面token的限制
            if tokens[i][1]=='DT' and tokens[i+1][1] in ['NN','NNS']:
                pattern_final+='{'+tokens[i][1]+'}'+'+'
            elif tokens[i][1]=='JJ' and tokens[i+1][1] in ['IN']:
                pattern_final+='{'+tokens[i][1]+'}'+'+'
            elif tokens[i][1]=='NN' and (tokens[i+1][1] in ['IN','VB','VBD','VBG','VBN','VBP','VBZ'] or tokens[i+1][0]=='are'):
                pattern_final+='{'+tokens[i][1]+'}'+'+'
            else:
                pattern_final+=tokens[i][0]+'+'
        elif i==len(tokens)-1:
            #对前面token的限制
            if tokens[i][1]=='JJ' and tokens[i-1][1] in ['VB','VBZ']:
                pattern_final+='{'+tokens[i][1]+'}'+'+'
            elif tokens[i][1]=='RB' and tokens[i-1][1] in ['CC','MD','VB','VBD','VBG','VBN','VBP','VBZ'] and tokens[i][1]!='not':
                pattern_final+='{'+tokens[i][1]+'}'+'+'
            elif tokens[i][1]=='NNS' and tokens[i-1][0]=='the':
                pattern_final+='{'+tokens[i][1]+'}'+'+'
            else:
                pattern_final+=tokens[i][0]+'+'       
        else:
            if tokens[i][1]=='JJ' and (tokens[i-1][1] in ['VB','VBZ'] or tokens[i+1][1] in ['IN']):
                pattern_final+='{'+tokens[i][1]+'}'+'+'
            elif tokens[i][1]=='RB' and tokens[i-1][1] in ['CC','MD','VB','VBD','VBG','VBN','VBP','VBZ']:
                pattern_final+='{'+tokens[i][1]+'}'+'+'
            elif tokens[i][1]=='NNS' and tokens[i-1][0]=='the':
                pattern_final+='{'+tokens[i][1]+'}'+'+'
            elif tokens[i][1]=='DT' and tokens[i+1][1] in ['NN','NNS']:
                pattern_final+='{'+tokens[i][1]+'}'+'+'
            elif tokens[i][1]=='NN' and (tokens[i+1][1] in ['IN','VB','VBD','VBG','VBN','VBP','VBZ'] or tokens[i+1][0]=='are'):
                pattern_final+='{'+tokens[i][1]+'}'+'+'
            else:
                pattern_final+=tokens[i][0]+'+'
            
    shift=re.findall('\$(\d+)', patternTtokens_list[0][0])[0]
    freq=0
    for patternTfix_tokens in patternTtokens_list:
        freq+=int(re.findall('@(\d+)', patternTfix_tokens[0])[0])
        
    return pattern_final[:-1]+'$'+str(shift)+'@'+str(freq)      

def is_from_same_tokens(patternTfix_tokens1,patternTfix_tokens2):
    if len(patternTfix_tokens1[1]) != len(patternTfix_tokens2[1]):
        return False
    else:
        for i in range(len(patternTfix_tokens1[1])):
            if patternTfix_tokens1[1][i][0] != patternTfix_tokens2[1][i][0] or patternTfix_tokens1[1][i][1] != patternTfix_tokens2[1][i][1]:
                return False
    return True

def is_contain_pattern(patternTfix_tokens_cmp,patternTfix_tokens_list):
    for patternTfix_tokens in patternTfix_tokens_list:
        if patternTfix_tokens[0]==patternTfix_tokens_cmp[0]:
            return True
    return False
        
def contain_pattern(patternTfix_tokens_cmp,patternTfix_tokens_list_list):
    for i in range(len(patternTfix_tokens_list_list)):
        for patternTfix_tokens_list in patternTfix_tokens_list_list[i]:
            if is_from_same_tokens(patternTfix_tokens_cmp,patternTfix_tokens_list):
#             if pattern in patterns_list_list[i][j]:
                return i
    return -1     
     
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
    
    attribute2patterns_sorted=sorted(attribute2patterns.iteritems(),key=lambda asd:asd[0],reverse=False)
    pattern2attributes_sorted=[]
    for (attribute,pattern_list) in attribute2patterns_sorted:
        pattern_list_sorted=sorted(pattern_list)
        for pattern in pattern_list_sorted:
            pattern2attributes_sorted.append((pattern,attribute))
        
    fp=codecs.open(path, 'w','utf-8')
    fp.write('{\n')
    for pattern2attribute in pattern2attributes_sorted:
        fp.write('  \"'+pattern2attribute[0]+'\": \"'+pattern2attribute[1]+'\",\n')
    fp.write('}')


'''
the next method manage the whole process to acquire the patterns we want
'''
def acquire_patterns(data):
    attribute2patterns_can_all={}
    for item in data:
        pos2definition=item["pos2definition"]
#         logger.info('concept: %s'%concept)
        for pos2def in pos2definition:
            definition=pos2def['definition']
#             logger.info('definition: \n%s'%definition)
            text=nltk.word_tokenize(definition)
            definition_tokens=nltk.pos_tag(text)
#             logger.info('definition_pos: \n%s'%definition_pos)
            attributes=pos2def['attributes']
            for attribute_name,attribute_value in attributes.iteritems():
#                 logger.info('attribute_name: %s'%attribute_name)
                attribute_value_text=nltk.word_tokenize(attribute_value)
                attribute_value_tokens=nltk.pos_tag(attribute_value_text)
#                 logger.info('attributes value token: %s'%attribute_value_tokens)
                prefixs_tokens2shift=get_fix(prefix_window_size,attribute_value_tokens,definition_tokens)
#                 logger.info('prefixs_token: \n%s'%str([str((token.word,token.pos))+": "+str(intersect) for (tokens,intersect) in prefixs_tokens2intersect for token in tokens]))
                patterns2fixs_tokens=get_combination_fix(prefixs_tokens2shift)
#                 logger.info('prefix: \n%s'%str(prefixs))
#                 if attribute_name in ['isA','isThe','purpose','used_for']:
#                     continue
#                 if attribute_name in ['isA','isThe']:
#                     continue
                if attribute_name in attribute2patterns_can_all.keys():
                    attribute2patterns_can_all[attribute_name].extend(patterns2fixs_tokens)
                else:
                    attribute2patterns_can_all[attribute_name]=patterns2fixs_tokens
#                 logger.info('\n')
#             logger.info('\n')
    
    attribute2patterns_all={}   
    for attribue,patterns2fix_tokens in attribute2patterns_can_all.iteritems():
        print 'attribue: '+attribue
        logger.info('final attribue: %s\n'%attribue)
        logger.info('patterns original length: '+str(len(patterns2fix_tokens)))
        logger.info('patterns original:　%s\n'%str(patterns2fix_tokens))
        filter_patterns=get_filter_pattern_seq(patterns2fix_tokens)
        attribute2patterns_all[attribue]=filter_patterns
        logger.info('final pattern:　%s\n'%str(filter_patterns))
    pattern2single_attribute=filter_efficient(attribute2patterns_all)
    return  pattern2single_attribute

def calculate_proprity2pattern(patterns):
    '''
    pos weigh 1.0/max_pattern_len, word weigh 1.0,
    '''
    data_new={}
    max_pattern_len=0
    print 'attribute num: '+str(len(set(patterns.values())))
    for pattern in patterns.keys():
        if len(pattern.split("+"))>max_pattern_len:
            max_pattern_len=len(pattern.split("+"))
#     print max_pattern_len       
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
    patternTfix_tokensTattribute_tuples=acquire_patterns(data)
    patterns=merge_pattern_all(patternTfix_tokensTattribute_tuples)
    patterns_priority=calculate_proprity2pattern(patterns)
    logger.info("has acquired all the patterns")
    json.dump(patterns_priority, codecs.open(path_pattern, 'w','utf-8'),ensure_ascii=False,indent=2)
#     json.dump(dict_reverse(patterns), codecs.open(path_pattern_reverse, 'w','utf-8'),ensure_ascii=False,indent=2)
#     dict_sorted_value(dict_reverse(patterns),path_pattern_reverse_sorted)
    sorted_by_attribute_pattern(patterns_priority,path_pattern_sorted)
    logger.info("output over")


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
    patterns=[(u'composed+of$0@23', [(u'composed', 'VBN'), (u'of', 'IN')])    
,(u'the+incorporates$0@15', [(u'the', 'DT'), (u'incorporates', 'NNS')])    
,(u'{NN}+{VBN}+of$0@14', [(u'base', 'NN'), (u'made', 'VBN'), (u'of', 'IN')])    
,(u'{RB}+of$0@15', [(u'primarily', 'RB'), (u'of', 'IN')])    
,(u'are+the+incorporates$0@7', [(u'are', 'VBP'), (u'the', 'DT'), (u'incorporates', 'NNS')])    
,(u'{VBP}+the+{NNS}$0@7', [(u'are', 'VBP'), (u'the', 'DT'), (u'incorporates', 'NNS')])    
,(u'the+{NNS}$0@15', [(u'the', 'DT'), (u'incorporates', 'NNS')])    
,(u'primarily+{IN}$0@15', [(u'primarily', 'RB'), (u'of', 'IN')])    
,(u'liquid+are$0@15', [(u'liquid', 'NN'), (u'are', 'VBP')])    
,(u'{VBN}+of$0@38', [(u'made', 'VBN'), (u'of', 'IN')])    
,(u'composed+{IN}$0@23', [(u'composed', 'VBN'), (u'of', 'IN')])    
,(u'{VBP}+{DT}+incorporates$0@7', [(u'are', 'VBP'), (u'the', 'DT'), (u'incorporates', 'NNS')])    
,(u'are+the+{NNS}$0@7', [(u'are', 'VBP'), (u'the', 'DT'), (u'incorporates', 'NNS')])    
,(u'are+{DT}+incorporates$0@7', [(u'are', 'VBP'), (u'the', 'DT'), (u'incorporates', 'NNS')])    
,(u'are+{DT}+{NNS}$0@7', [(u'are', 'VBP'), (u'the', 'DT'), (u'incorporates', 'NNS')])    
,(u'{DT}+incorporates$0@15', [(u'the', 'DT'), (u'incorporates', 'NNS')])    
,(u'{NN}+made+of$0@14', [(u'base', 'NN'), (u'made', 'VBN'), (u'of', 'IN')])    
,(u'liquid+{VBP}$0@15', [(u'liquid', 'NN'), (u'are', 'VBP')])    
,(u'{VBP}+the+incorporates$0@7', [(u'are', 'VBP'), (u'the', 'DT'), (u'incorporates', 'NNS')])    
,(u'{NN}+are$0@27', [(u'liquid', 'NN'), (u'are', 'VBP')])    
,(u'primarily+of$0@15', [(u'primarily', 'RB'), (u'of', 'IN')])    
,(u'cast+made+of$0@7', [(u'cast', 'NN'), (u'made', 'NN'), (u'of', 'IN')])    
,(u'made+of$0@30', [(u'made', 'VBN'), (u'of', 'IN')])]
    print merge_pattern(patterns)

def test3():
    patterns_can_remove_dup=[[(u'atrophy+{VBG}+from$0@7', [(u'atrophy', 'NN'), (u'resulting', 'VBG'), (u'from', 'IN')]), 
                              (u'atrophy+resulting+{IN}$0@7', [(u'atrophy', 'NN'), (u'resulting', 'VBG'), (u'from', 'IN')]), 
                              (u'atrophy+{VBG}+{IN}$0@7', [(u'atrophy', 'NN'), (u'resulting', 'VBG'), (u'from', 'IN')]), 
                              (u'atrophy+resulting+from$0@7', [(u'atrophy', 'NN'), (u'resulting', 'VBG'), (u'from', 'IN')])],
                            [(u'{NN}+resulting+{IN}$0@21', [(u'metal', 'NN'), (u'resulting', 'VBG'), (u'from', 'IN')]), 
                             (u'{NN}+{VBG}+from$0@21', [(u'metal', 'NN'), (u'resulting', 'VBG'), (u'from', 'IN')]), 
                             (u'{NN}+resulting+from$0@21', [(u'metal', 'NN'), (u'resulting', 'VBG'), (u'from', 'IN')])], 
                            [(u'generated+by$0@15', [(u'generated', 'VBN'), (u'by', 'IN')]), 
                             (u'generated+{IN}$0@15', [(u'generated', 'VBN'), (u'by', 'IN')])], 
                            [(u'{VBG}+from$0@60', [(u'resulting', 'VBG'), (u'from', 'IN')]), 
                             (u'resulting+from$0@60', [(u'resulting', 'VBG'), (u'from', 'IN')])], 
                            [(u'part+resulting+from$0@7', [(u'part', 'NN'), (u'resulting', 'VBG'), (u'from', 'IN')])]]
    merge_similar_patterns(patterns_can_remove_dup)
if __name__=='__main__':
    start = datetime.datetime.now()
    logger.info(start)
    print start
    main()
#     test()
#     test1()
#     test2()
#     test3()
    end = datetime.datetime.now()
    logger.info(end)
    print end
    logger.info("cost time: "+str((end - start).microseconds))
    print str((end - start).seconds)+' s'