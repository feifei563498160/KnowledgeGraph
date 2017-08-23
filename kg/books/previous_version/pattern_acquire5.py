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
from itertools import product
from kg.books.basic_obj import Token,Pattern
import kg.books.regular_verify7
import datetime
import re
from kg.util.string import cut_token_list, cut_truple_list
from _collections import defaultdict
import copy

path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
path_log_output=path_project+os.sep+"output"+os.sep+"log_pattern_acquire_auto5_6.txt"
logger=log_console_and_file(path_log_output)

prefix_window_size=5
post_window_size=2

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
    
    window_whole=[]
    if start<size and start<len(definition_tokens):
        window_whole.extend(definition_tokens[:start+2])
    elif start>=size and start<len(definition_tokens):
        window_whole.extend(definition_tokens[start-size:start+2])
          
    window=[]
    prefixsTshiftTwindow=[]
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
            prefixsTshiftTwindow.append((prefix,i,window_whole))
        start=start+1
    
    return  prefixsTshiftTwindow

def get_fix(size,attribute_value_tokens,definition_tokens): 
    chunks=cut_truple_list(attribute_value_tokens,[(';', ':')])
    prefixsTshiftTwindow=[]
    for chunk in chunks:
        prefixsTshiftTwindow.extend(get_fix_chunk(size,chunk,definition_tokens))
    return prefixsTshiftTwindow


def get_string_fix(truple_list,patternShiftFixtokenWindowList,shift,fixs_token,window):
    for truple in truple_list:
        pattern_real='+'.join(truple)
        patternShiftFixtokenWindowList.append((pattern_real,shift,fixs_token,window))
        
def truple2list(truple):
    return [truple[0],'{'+truple[1]+'}']
        
def get_combination_fix(prefixsTshiftTwindow):
    patternShiftFixtokenWindowList=[]
    for  (fixs_token,shift,window) in prefixsTshiftTwindow:
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
        get_string_fix(truple_list,patternShiftFixtokenWindowList,shift,fixs_token,window) 
    return patternShiftFixtokenWindowList


'''
the flowing methods aim to filter patterns according to some rules
'''
def exist_special_token(pattern_real):
    special_token=['.','{.}',',','{,}',';','{:}']
    for token in pattern_real.split('+'):
        if token in special_token:
            return True
    return False

def is_all_POS(pattern_real):
    pattern_words=pattern_real.split('+')
    for pattern_word in pattern_words:
        if '{' not in pattern_word:
            return False
    return True

def filter_special_token_A_full_POS(patternShiftFixtokenWindowList):
    filter1=[]
    for patternShiftFixtokenWindow in patternShiftFixtokenWindowList:
        pattern_real=patternShiftFixtokenWindow[0]
        if exist_special_token(pattern_real)==False and len(pattern_real.split('+'))>=2 and is_all_POS(pattern_real)==False:
#         if len(pattern_can.split('+'))>=2:
            filter1.append(patternShiftFixtokenWindow)
    return filter1

def filter_wrong_shift(patternShiftFixtokenWindowList):
    filter2=[]       
    for patternShiftFixtokenWindow in patternShiftFixtokenWindowList:
        pattern=patternShiftFixtokenWindow[0]
        shift=patternShiftFixtokenWindow[1]
        if len(pattern[0].split('+'))>=shift:
            filter2.append(patternShiftFixtokenWindow)
    return filter2

def caculate_freq_single(patternShiftFixtokenWindow_cmp,patternShiftFixtokenWindowList): 
    '''
            这个计算方式将不同shift的pattern 只要patern相同  就认为是相同pattern
    '''   
    cnt=0
    pattern_real_cmp=patternShiftFixtokenWindow_cmp[0]
    for patternShiftFixtokenWindow in patternShiftFixtokenWindowList:
        pattern_real=patternShiftFixtokenWindow[0]
        if pattern_real.find(pattern_real_cmp)!=-1:
            cnt+=1
    return cnt    
    
def caculate_pattern_freq(patternShiftFixtokenWindowList):
    patternShiftFixtokenWindowFreqList=[]
    for patternShiftFixtokenWindow in patternShiftFixtokenWindowList:
        freq=caculate_freq_single(patternShiftFixtokenWindow,patternShiftFixtokenWindowList)
        patternShiftFixtokenWindowFreqList.append(patternShiftFixtokenWindow+(freq,))
    return patternShiftFixtokenWindowFreqList

def most_common(pattern_tuples,n):
    sorted_patterns=sorted(pattern_tuples,key=lambda asd:asd[4],reverse=True)
    return sorted_patterns[:n+1]

def get_filter_pattern_seq(patternShiftFixtokenWindowList):
    filter1=filter_special_token_A_full_POS(patternShiftFixtokenWindowList)
    filter2=filter_wrong_shift(filter1)
    filter_patternShiftFixtokenWindowFreqList=most_common(caculate_pattern_freq(filter2),len(filter2)/10)
    return filter_patternShiftFixtokenWindowFreqList

def valuelist2values(dict_can):   
    attribute2single_patttern=[]    
    for key,value_list in dict_can.iteritems():
        for value in value_list:
            attribute2single_patttern.append((key,)+value)
    return attribute2single_patttern
   
def filter_efficient(attribute2patternShiftFixtokenWindowFreqList):
    '''
            这个函数是将不能唯一属于一个属性的pattern过滤掉
    '''
    attributePatternShiftFixtokenWindowFreqList=valuelist2values(attribute2patternShiftFixtokenWindowFreqList)
    #pattern2attributes键为真实的pattern 值为该pattern映射的属性
    pattern_real2attributes=defaultdict(set)
    #pattern2whole_pattern键为真实的pattern 值为包含了后缀符号如$ # @的完整的pattern
    pattern_real2pattern_whole={}
    for attributePatternShiftFixtokenWindowFreq in attributePatternShiftFixtokenWindowFreqList: 
        attribute=attributePatternShiftFixtokenWindowFreq[0]
        pattern_real=attributePatternShiftFixtokenWindowFreq[1]
        pattern_real2attributes[pattern_real].add(attribute)
        pattern_real2pattern_whole[pattern_real]=attributePatternShiftFixtokenWindowFreq
        
    pattern2single_attributes={}    
    for pattern in pattern_real2attributes.keys():
        if len(pattern_real2attributes[pattern])>=2:
            pattern_real2attributes.pop(pattern)
        else:
            #得到pattern和属性的唯一对应
            pattern2single_attributes[pattern]=list(pattern_real2attributes[pattern])[0]
            
    patternAttributeShiftFreqFixtokenWindowList=[]
    for pattern,single_attribute in pattern2single_attributes.iteritems():
        #aPSFWF=attributePatternShiftFixtokenWindowFreq
        aPSFWF=pattern_real2pattern_whole[pattern]
        pattern_tuple=(aPSFWF[1],aPSFWF[0],aPSFWF[2],aPSFWF[5],aPSFWF[3],aPSFWF[4])
        patternAttributeShiftFreqFixtokenWindowList.append(pattern_tuple)
    return patternAttributeShiftFreqFixtokenWindowList

def contain_PASFFW_by_Fixtokens(PASFFW_cmp,PASFFWListList):
    for i in range(len(PASFFWListList)):
        for PASFFW in PASFFWListList[i]:
            if is_from_same_tokens(PASFFW_cmp,PASFFW):
#             if pattern in patterns_list_list[i][j]:
                return i
    return -1  

def is_from_same_tokens(PASFFW1,PASFFW2):
    #PASFFW: patternAttributeShiftFreqFixtokenWindow
    if len(PASFFW1[4]) != len(PASFFW2[4]):
        return False
    else:
        for i in range(len(PASFFW1[4])):
            if PASFFW1[4][i][0] != PASFFW2[4][i][0] or PASFFW1[4][i][1] != PASFFW2[4][i][1]:
                return False
    return True

def is_contain_pattern(PASFFW_cmp,PASFFWList_sameTokens_RemoveDup):
    for PASFFW_sameTokens_RemoveDup in PASFFWList_sameTokens_RemoveDup:
        if PASFFW_sameTokens_RemoveDup[0]==PASFFW_cmp[0]:
            return True
    return False

# def mergeSimilarPatterns(PASFFWListList):
#     '''
#             合并属于同一个token list的不同长度或形式的pattern进行合并  如 {NN}+is+a 和is+a 可以合并成is+a
#     PASFFW: patternAttributeShiftFreqFixtokenWindow
#     '''
#     remove_pos=[]
#     m=len(PASFFWListList)-1
#     while m >=0:
#         tokens_m=PASFFWListList[m][0][4]
#         n=m-1
#         while n>=0:
#             tokens_n=PASFFWListList[n][0][4]
#             if len(tokens_m)<len(tokens_n):
#                 if get_match_pos_token(tokens_m, tokens_n)[0]!=-1:
#                     if is_worse(tokens_m,tokens_n):
#                         remove_pos.append(m)
#                     else:
#                         remove_pos.append(n)
#             else:
#                 if get_match_pos_token(tokens_n, tokens_m)[0]!=-1:
#                     if is_worse(tokens_n,tokens_m):
#                         remove_pos.append(n)
#                     else:
#                         remove_pos.append(m)
#             n-=1
#         m-=1 
#     
#     for i in range(len(PASFFWListList)-1,-1,-1):
#         if i in remove_pos:
#             del PASFFWListList[i]
#             
# def is_worse(tokens1,tokens2):
#     flag=True
#     start_pos=get_match_pos_token(tokens1, tokens2)[0]
#     if start_pos!=0:
#         #当短的pattern是长的pattern的中间部位
#         if (start_pos+len(tokens1))!=len(tokens2):
#             flag=is_add(tokens2[:start_pos]) or is_add(tokens2[len(tokens1):])
#         #当短的pattern是长的pattern的后半段
#         else:
#             flag=is_add(tokens2[:start_pos])
#     else:
#         #当短的pattern是长的pattern的前半段
#         flag=is_add(tokens2[len(tokens1):])
#     return flag
# 
# def is_add(tokens):
#     for token in tokens:
#         if token[1] in ['NN','NNS','NNP','NNPS','CC','DT','JJ','JJR','JJS','PDT','POS','PRP','PRP$','RBR','RBS','WDT','WP','WP$','WRB']:
#             return False
# #         if token[1] in ['VB','VBN','VBD','VBG','VBZ','VBP','IN']:
# #             continue
#     return True   

def rebulidPattern(tokens):
    pattern_final=''
    for i in range(len(tokens)):
        if i==0:
            #对后面token的限制
            if tokens[i][1]=='DT' and tokens[i+1][1] in ['NN','NNS']:
                pattern_final+='{'+tokens[i][1]+'}'+'+'
            elif tokens[i][1]=='JJ' and tokens[i+1][1] in ['IN']:
                pattern_final+='{'+tokens[i][1]+'}'+'+'
            elif tokens[i][1]=='NN' and (tokens[i+1][1] in ['IN','VB','VBD','VBG','VBN','VBP','VBZ'] or tokens[i+1][0]=='are') and tokens[i][0] not in ['term','example']:
                pattern_final+='{'+tokens[i][1]+'}'+'+'
            else:
                pattern_final+=tokens[i][0]+'+'
        elif i==len(tokens)-1:
            #对前面token的限制
            if tokens[i][1]=='JJ' and tokens[i-1][1] in ['VB','VBZ']:
                pattern_final+='{'+tokens[i][1]+'}'+'+'
            elif tokens[i][1]=='RB' and tokens[i-1][1] in ['CC','MD','VB','VBD','VBG','VBN','VBP','VBZ'] and tokens[i][0]!='not':
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
            elif tokens[i][1]=='NN' and (tokens[i+1][1] in ['IN','VB','VBD','VBG','VBN','VBP','VBZ'] or tokens[i+1][0]=='are') and tokens[i][0] not in ['term','example']:
                pattern_final+='{'+tokens[i][1]+'}'+'+'
            else:
                pattern_final+=tokens[i][0]+'+'
    return pattern_final[:-1]

def get_final_PASFFW(PASFFWList):
    #这个list中的fix_tokens都是一样的  只需要根据fix_tokens 来决定最终的pattern形式
    tokens=PASFFWList[0][4]
    pattern_final=rebulidPattern(tokens)
    shift=PASFFWList[0][2]
    freq=PASFFWList[0][3]
#     for PASFFW in PASFFWList:
#         freq+=PASFFW[3]
    return (pattern_final,PASFFWList[0][1],shift,freq,PASFFWList[0][4],PASFFWList[0][5])  

def is_from_same_window(PASFFW1,PASFFW2):
    if len(PASFFW1[5]) != len(PASFFW2[5]):
        return False
    else:
        for i in range(len(PASFFW1[5])):
            if PASFFW1[5][i][0] != PASFFW2[5][i][0] or PASFFW1[5][i][1] != PASFFW2[5][i][1]:
                return False
    return True
    
def contain_PASFFW_by_Window(PASFFW_cmp,PASFFWListList):
    for i in range(len(PASFFWListList)):
        for PASFFW in PASFFWListList[i]:
            if is_from_same_window(PASFFW_cmp,PASFFW):
#             if pattern in patterns_list_list[i][j]:
                return i
    return -1

def get_final_pattern(PASFFWList):
    window=PASFFWList[0][5]
    rules=['{NN}|{NNS}|{NNP}|{NNPS}+:',
           '{RB}+is+{JJ}',
           '{VBN}|{VBD}|{VBZ}|{VB}+{IN}',
           '{PRP}+{VBZ}',
           '{MD}+{VB}',
           'to+{VB}',
           'is+not+a',
           'for+{VBG}',
           '{RB}+for',
           ]
    #最后一条规则是以大写字母开头
    pattern_final=''
    for rule in rules:
        #此处应使用pattern和def_tokens的比较方式
        start=kg.books.regular_verify7.KMP_match(rule+'$', window)
        if start!=-1:
            matchTokens=window[start:start+len(rule.split('+'))]
            pattern_final=rebulidPattern(matchTokens)
    shift=0
    freq=0
    
    return "%s$%d@%d" % (pattern_final,shift,freq)

def getWholePattern(PASFFW):
    return "%s$%d@%d" % (PASFFW[0],PASFFW[2],PASFFW[3])

def containIntersectPASFFW(PASFFW_cmp,PASFFWListList):
    for i in range(len(PASFFWListList)):
        for PASFFW in PASFFWListList[i]:
            if is_intersectPASFFW(PASFFW_cmp,PASFFW)>=0:
                return i
    return -1

def is_intersectPASFFW(PASFFW1,PASFFW2):
    #判断两个串是否是首尾相交的
    pattern1=PASFFW1[0]
    pattern2=PASFFW2[0]
    if pattern2.find(pattern1)!=-1: 
        return 1    #pattern2包含pattern1
    if pattern1.find(pattern2)!=-1:
        return 0    #pattern1包含pattern2
    
    pattern1_words=pattern1.split('+')
    pattern2_words=pattern2.split('+')
    overlap_words=set(pattern1_words) & set(pattern2_words)
    if len(overlap_words)==0:
        return -1
    
    pos_1=[]
    pos_2=[]
    for word in overlap_words:
        pos_1.append(pattern1_words.index(word))
        pos_2.append(pattern2_words.index(word))
    
    if min(pos_1)==0 and max(pos_2)==len(pattern2_words)-1:
        return 2   #PASFFW2在前
    elif min(pos_2)==0 and max(pos_1)==len(pattern1_words)-1:
        return 3
    else:
        return -1

def get_final_tokens(PASFFWList):
    PASFFWList_new=[]
    for i in range(len(PASFFWList)):
        for j in range(i+1,len(PASFFWList),1):
            cmp=is_intersectPASFFW(PASFFWList[i],PASFFWList[j])
            if cmp==-1:
                continue
            elif cmp==0:
                PASFFWList_new.append(PASFFWList[i])
            elif cmp==1:
                PASFFWList_new.append(PASFFWList[j])
            elif cmp==2:
                end=[x[0] for x in PASFFWList[j][4]].index(PASFFWList[i][4][0][0])
                fixtokens=PASFFWList[j][4][:end]+PASFFWList[i][4]
                shift=PASFFWList[i][2]
                freq=min(PASFFWList[i][3],PASFFWList[j][3])
                pattern='+'.join(PASFFWList[j][0].split('+')[:end]+PASFFWList[i][0].split('+'))
                PASFFWList_new.append((pattern,PASFFWList[i][1],shift,freq,fixtokens,PASFFWList[i][5]))
            elif cmp==3:
                end=[x[0] for x in PASFFWList[i][4]].index(PASFFWList[j][4][0][0])
                fixtokens=PASFFWList[i][4][:end]+PASFFWList[j][4]
                shift=PASFFWList[j][2]
                freq=min(PASFFWList[i][3],PASFFWList[j][3])
                pattern='+'.join(PASFFWList[i][0].split('+')[:end]+PASFFWList[j][0].split('+'))
                PASFFWList_new.append((pattern,PASFFWList[j][1],shift,freq,fixtokens,PASFFWList[j][5]))   
    del PASFFWList[:]
    PASFFWList.extend(PASFFWList_new)

def merge_near_patterns(PASFFWList):
#     #这时传入的list 中的PASFFW 整合了某个fix_tokens的所有结果 得到一个最好的结果
#     #将来自同一window的pattern合并到一个list中
#     PASFFWListList=[[]] 
#     for i in range(len(PASFFWList)):
#         pos_i=contain_PASFFW_by_Window(PASFFWList[i],PASFFWListList)
#         if pos_i==-1:
#             pattern_can_i=[]
#             pattern_can_i.append(PASFFWList[i])
#             PASFFWListList.append(pattern_can_i)
#         pos_i=contain_PASFFW_by_Window(PASFFWList[i],PASFFWListList)
# #         freq_i=re.findall('@(\d+)', patterns[i])[0]
#         for j in range(i+1):
# #             freq_j=re.findall('@(\d+)', patterns[j])[0]
#             if is_intersectPASFFW(PASFFWList[i],PASFFWList[j])>=0:
#                 pos_j=contain_PASFFW_by_Window(PASFFWList[j],PASFFWListList)
#                 if pos_j!=-1:
#                     PASFFWListList[pos_i].append(PASFFWList[j])
#      
#     PASFFW_print=''                
#     for PASFFWList in PASFFWListList:
#         if len(PASFFWList)==0:
#             continue
#         PASFFW_print+="same window: %s\n"%str(PASFFWList[0][5])
#         for PASFFW in PASFFWList:
#             PASFFW_print+=PASFFW[0]+', '+PASFFW[1]+', '+str(PASFFW[2])+', '+str(PASFFW[3])+'\n'
#         PASFFW_print+='-----------\n'
#     logger.info("merge by the same window: \n"+PASFFW_print)
#                      
#     #去掉重复  因为是list  会重复
#     PASFFWListList_RemoveDup=[]      
#     for PASFFWList in PASFFWListList:
#         if len(PASFFWList)==0:
#             continue
#         PASFFWList_sameWindow_RemoveDup=[]
#         for PASFFW in PASFFWList:
#             if is_contain_pattern(PASFFW,PASFFWList_sameWindow_RemoveDup)==False:
#                 PASFFWList_sameWindow_RemoveDup.append(PASFFW)
#         PASFFWListList_RemoveDup.append(PASFFWList_sameWindow_RemoveDup)
#      
#      
#     PASFFW_RDup_print=''                
#     for PASFFWList in PASFFWListList_RemoveDup:
#         PASFFW_RDup_print+="same window: %s\n"%str(PASFFWList[0][5])
#         for PASFFW in PASFFWList:
#             PASFFW_RDup_print+=PASFFW[0]+', '+PASFFW[1]+', '+str(PASFFW[2])+', '+str(PASFFW[3])+'\n'
#         PASFFW_RDup_print+='----------------------------\n'
#     logger.info("remove the dup PASFFW: \n"+PASFFW_RDup_print)
     
    #经过四次迭代 基本上就稳定了 PASFFWList就不变了
    for i in range(4):
        PASFFWList=get_final_tokens(PASFFWList)
     
     
    final_pattern=[]
    for PASFFWList in PASFFWList:
        pattern=get_final_pattern(PASFFWList)
        if pattern[:pattern.index('$')]=='':
            final_pattern.extend([getWholePattern(x) for x in PASFFWList])
        else:   
            final_pattern.append(pattern)
              
    final_pattern_print=''
    for pattern in final_pattern:
        final_pattern_print+=pattern+'\n'
    logger.info("get the final patterns: \n"+final_pattern_print)
      
    return  final_pattern

# 
        
def merge_pattern(patternAttributeShiftFreqFixtokenWindowList):
    PASFFWList=patternAttributeShiftFreqFixtokenWindowList
    print "----------------merge patterns of attribute: %s ----------------" % PASFFWList[0][1]
    logger.info("----------------merge patterns of attribute: %s ----------------" % PASFFWList[0][1])
    #PASFFW: patternAttributeShiftFreqFixtokenWindow
    #将来自同一fix_tokens的pattern合并到一个list中
    PASFFWListList=[[]] 
    for i in range(len(PASFFWList)):
        pos_i=contain_PASFFW_by_Fixtokens(PASFFWList[i],PASFFWListList)
        if pos_i==-1:
            pattern_can_i=[]
            pattern_can_i.append(PASFFWList[i])
            PASFFWListList.append(pattern_can_i)
        pos_i=contain_PASFFW_by_Fixtokens(PASFFWList[i],PASFFWListList)
#         freq_i=re.findall('@(\d+)', patterns[i])[0]
        for j in range(i+1):
#             freq_j=re.findall('@(\d+)', patterns[j])[0]
            if is_from_same_tokens(PASFFWList[i],PASFFWList[j]):
                pos_j=contain_PASFFW_by_Fixtokens(PASFFWList[j],PASFFWListList)
                if pos_j!=-1:
                    PASFFWListList[pos_i].append(PASFFWList[j])
    
    PASFFW_print=''                
    for PASFFWList in PASFFWListList:
        if len(PASFFWList)==0:
            continue
        PASFFW_print+="same fix tokens: %s\n"%str(PASFFWList[0][4])
        for PASFFW in PASFFWList:
            PASFFW_print+=PASFFW[0]+', '+PASFFW[1]+', '+str(PASFFW[2])+', '+str(PASFFW[3])+'\n'
        PASFFW_print+='----------\n'
    logger.info("merge by the same fix tokens: \n"+PASFFW_print)
    #去掉重复  因为是list  会重复
    PASFFWListList_RemoveDup=[]      
    for PASFFWList in PASFFWListList:
        if len(PASFFWList)==0:
            continue
        PASFFWList_sameTokens_RemoveDup=[]
        for PASFFW in PASFFWList:
            if is_contain_pattern(PASFFW,PASFFWList_sameTokens_RemoveDup)==False:
                PASFFWList_sameTokens_RemoveDup.append(PASFFW)
        PASFFWListList_RemoveDup.append(PASFFWList_sameTokens_RemoveDup)
    
    PASFFW_RDup_print=''                
    for PASFFWList in PASFFWListList_RemoveDup:
        print PASFFWList
        PASFFW_RDup_print+="same fix tokens: %s\n"%str(PASFFWList[0][4])
        for PASFFW in PASFFWList:
            PASFFW_RDup_print+=PASFFW[0]+', '+PASFFW[1]+', '+str(PASFFW[2])+', '+str(PASFFW[3])+'\n'
        PASFFW_RDup_print+='--------------------\n'
    logger.info("remove the dup PASFFW: \n"+PASFFW_RDup_print)
    
#     mergeSimilarPatterns(PASFFWListList_RemoveDup)
    
    
#     PASFFW_RDup_MergeSame_print=''                
#     for PASFFWList in PASFFWListList_RemoveDup:
#         PASFFW_RDup_MergeSame_print+="same fix tokens: %s\n"%str(PASFFWList[0][4])
#         for PASFFW in PASFFWList:
#             PASFFW_RDup_MergeSame_print+=PASFFW[0]+', '+PASFFW[1]+', '+str(PASFFW[2])+', '+str(PASFFW[3])+'\n'
#         PASFFW_RDup_MergeSame_print+='--------------------------------------\n'
#     logger.info("after merging similar pattern: \n"+PASFFW_RDup_MergeSame_print)
    
    final_PASFFWList=[]
    for PASFFWList_RemoveDup in PASFFWListList_RemoveDup:
        final_PASFFWList.append(get_final_PASFFW(PASFFWList_RemoveDup))
    
    final_PASFFWList_print=''
    for PASFFW in final_PASFFWList:
        final_PASFFWList_print+=PASFFW[0]+', '+PASFFW[1]+', '+str(PASFFW[2])+', '+str(PASFFW[3])+'\n'  
    logger.info("get the final PASFFWList: \n"+final_PASFFWList_print)
    
    logger.info("get the final PASFFWList: \n"+str(final_PASFFWList))
    final_pattern_list=merge_near_patterns(final_PASFFWList)
    
    return final_pattern_list

def merge_pattern_all(patternAttributeShiftFreqFixtokenWindowList):
    '''
             此方法用于合并pattern，并使用合并后的pattern 重新计算频率
    '''
    attribute2PASFFWList=defaultdict(list)
    for patternAttributeShiftFreqFixtokenWindow in patternAttributeShiftFreqFixtokenWindowList:
        attribute=patternAttributeShiftFreqFixtokenWindow[1]
        attribute2PASFFWList[attribute].append(patternAttributeShiftFreqFixtokenWindow)
    
    attribute2patterns_merge=[]
    for attribute,patternAttributeShiftFreqFixtokenWindowList in attribute2PASFFWList.iteritems():
        attribute2patterns_merge.append((attribute,merge_pattern(patternAttributeShiftFreqFixtokenWindowList)))
        
    pattern2attribute=defaultdict(list)
    for attribute,patterns in attribute2patterns_merge:
        for pattern in patterns:
            pattern2attribute[pattern]=attribute
    return pattern2attribute

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
#         logger.info('patterns original:　%s\n'%str(patterns2fix_tokens))
        filter_patterns=get_filter_pattern_seq(patterns2fix_tokens)
        attribute2patterns_all[attribue]=filter_patterns
        logger.info('final patterns length %d:　%s\n'%(len(filter_patterns),str(filter_patterns)))
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
        print pattern,attribute
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
    logger.info('patternTfix_tokensTattribute_tuples: %d\n' % len(patternTfix_tokensTattribute_tuples)+str(patternTfix_tokensTattribute_tuples))
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
#     merge_similar_patterns(patterns_can_remove_dup)


def test_get_final_tokens():
    PASFFWList=[(u'would+prevent', u'effect', 1, 15, [(u'would', 'MD'), (u'prevent', 'VB')], [(u'of', 'IN'), (u'dental', 'JJ'), (u'arch', 'NN'), (u'that', 'WDT'), (u'would', 'MD'), (u'prevent', 'VB'), (u'the', 'DT')]), 
     (u'low-calorie+{NN}+that', u'effect', 0, 13, [(u'low-calorie', 'JJ'), (u'sweetener', 'NN'), (u'that', 'IN')], [(u'is', 'VBZ'), (u'a', 'DT'), (u'low-calorie', 'JJ'), (u'sweetener', 'NN'), (u'that', 'IN'), (u'reduces', 'VBZ'), (u'caries', 'NNS')]), 
     (u'{NN}+because+it', u'effect', 0, 13, [(u'unit', 'NN'), (u'because', 'IN'), (u'it', 'PRP')], [(u'healthy', 'JJ'), (u'gingival', 'NN'), (u'unit', 'NN'), (u'because', 'IN'), (u'it', 'PRP'), (u'enables', 'VBZ'), (u'the', 'DT')]), 
     (u'that+reduces', u'effect', 1, 15, [(u'that', 'IN'), (u'reduces', 'VBZ')], [(u'is', 'VBZ'), (u'a', 'DT'), (u'low-calorie', 'JJ'), (u'sweetener', 'NN'), (u'that', 'IN'), (u'reduces', 'VBZ'), (u'caries', 'NNS')]), 
     (u'because+it', u'effect', 0, 29, [(u'because', 'IN'), (u'it', 'PRP')], [(u'healthy', 'JJ'), (u'gingival', 'NN'), (u'unit', 'NN'), (u'because', 'IN'), (u'it', 'PRP'), (u'enables', 'VBZ'), (u'the', 'DT')]), 
     (u'arch+that+would', u'effect', 0, 13, [(u'arch', 'NN'), (u'that', 'WDT'), (u'would', 'MD')], [(u'of', 'IN'), (u'dental', 'JJ'), (u'arch', 'NN'), (u'that', 'WDT'), (u'would', 'MD'), (u'prevent', 'VB'), (u'the', 'DT')]), 
     (u'that+would', u'effect', 0, 29, [(u'that', 'WDT'), (u'would', 'MD')], [(u'of', 'IN'), (u'dental', 'JJ'), (u'arch', 'NN'), (u'that', 'WDT'), (u'would', 'MD'), (u'prevent', 'VB'), (u'the', 'DT')]), 
     (u'{NN}+that', u'effect', 0, 29, [(u'sweetener', 'NN'), (u'that', 'IN')], [(u'is', 'VBZ'), (u'a', 'DT'), (u'low-calorie', 'JJ'), (u'sweetener', 'NN'), (u'that', 'IN'), (u'reduces', 'VBZ'), (u'caries', 'NNS')]), 
     (u'it+enables', u'effect', 1, 15, [(u'it', 'PRP'), (u'enables', 'VBZ')], [(u'healthy', 'JJ'), (u'gingival', 'NN'), (u'unit', 'NN'), (u'because', 'IN'), (u'it', 'PRP'), (u'enables', 'VBZ'), (u'the', 'DT')])]
    
    for i in range(5):
        print 'i= '+str(i)
        get_final_tokens(PASFFWList)
#         for x in get_final_tokens(PASFFWList):
#             print x
        print '-------------------'

    for x in remove_dup(PASFFWList):
        print x

def remove_dup(PASFFWList):
    PASFFWList_RemoveDup=[]
    for PASFFW in PASFFWList:
        if contain_PASFFW(PASFFW,PASFFWList_RemoveDup)==False:
            PASFFWList_RemoveDup.append(PASFFW)
    return PASFFWList_RemoveDup

def contain_PASFFW(PASFFW1,PASFFWList):
    for PASFFW in PASFFWList:
        if PASFFW1[0]==PASFFW[0]:
            return True
    return False

if __name__=='__main__':
    start = datetime.datetime.now()
    logger.info(start)
    print start
#     main()
#     test()
#     test1()
#     test2()
#     test3()
    test_get_final_tokens()
    end = datetime.datetime.now()
    logger.info(end)
    print end
    logger.info("cost time: "+str((end - start).microseconds))
    print str((end - start).seconds)+' s'