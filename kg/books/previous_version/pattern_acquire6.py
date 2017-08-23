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
import kg.books.regular_verify7
import datetime
from kg.util.string import cut_truple_list
from _collections import defaultdict

path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
path_log_output=path_project+os.sep+"output"+os.sep+"log_pattern_acquire_auto6_0.txt"
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


def rebulidPattern(tokens):
    pattern_final=''
    for i in range(len(tokens)):
        if i==0:
            #对后面token的限制
#             if tokens[i][1]=='DT' and tokens[i+1][1] in ['NN','NNS']:
#                 pattern_final+='{'+tokens[i][1]+'}'+'+'
            if tokens[i][1]=='JJ' and tokens[i+1][1] in ['IN']:
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
#             elif tokens[i][1]=='DT' and tokens[i+1][1] in ['NN','NNS']:
#                 pattern_final+='{'+tokens[i][1]+'}'+'+'
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

def get_final_pattern(PASFFW):
    fix_tokens=PASFFW[4]
    rules=['{NN}|{NNS}|{NNP}|{NNPS}+:',
           '{RB}+is+{JJ}',
           '{VBG}|{VBP}|{VBN}|{VBD}|{VBZ}|{VB}+{IN}',
           '{VBG}|{VBP}|{VBN}|{VBD}|{VBZ}|{VB}+{RB}+{IN}',
           '{PRP}+{VBZ}',
           '{MD}+{VB}',
           'to+{VB}',
           'is+not+a',
           'is+a',
           'is+the',
           'for+{VBG}',
           '{RB}+{IN}',
           'so+that'
           ]
    #最后一条规则是以大写字母开头
    pattern_final=''
    for rule in rules:
        #此处应使用pattern和def_tokens的比较方式
        start=kg.books.regular_verify7.KMP_match(rule+'$', fix_tokens)
        if start!=-1:
            matchTokens=fix_tokens[start:start+len(rule.split('+'))]
            pattern_final=rebulidPattern(matchTokens)
            break
    shift=PASFFW[2]
    freq=PASFFW[3]
    
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
    
    if pattern1_words[0] in pattern2_words:
        if is_near_string(pattern1_words,pattern2_words)==True:
            return 2
        else:
            return -1
    elif pattern2_words[0] in pattern1_words:
        if is_near_string(pattern2_words,pattern1_words)==True:
            return 3
        else:
            return -1
    else:
        return -1

def is_near_string(list1,list2):
    start=list2.index(list1[0])
    i=0
    range_=min(len(list2)-start,len(list1))
    while i<range_:
        if list2[start+i]!=list1[i]:
            return False
        i+=1
    return True
    
def get_final_tokens(PASFFWList):
    #如果跟任何一个都不相交  就保留下来
    if len(PASFFWList)==1:
        return PASFFWList
    PASFFWList_new=[]
    visit_ele=set([])
    for i in range(len(PASFFWList)):
#         logger.info('i=%d' % i)
        cmp_result=[]
        for j in range(i+1,len(PASFFWList),1):
#             logger.info(('i=%d' % i,'j=%d' % j))
            cmp_=is_intersectPASFFW(PASFFWList[i],PASFFWList[j])
            if cmp_>=0:
                visit_ele.add(i)
                visit_ele.add(j)
            cmp_result.append(cmp_)
            if cmp_==-1:
#                 logger.info((' have no intersect ',PASFFWList[i],PASFFWList[j]))
                continue
            elif cmp_==0:
#                 logger.info((' includes_ij ',PASFFWList[i],PASFFWList[j]))
#                 logger.info(('append: ',PASFFWList[i]))
                PASFFWList_new.append(PASFFWList[i])
            elif cmp_==1:
#                 logger.info((' includes_ji ',PASFFWList[j],PASFFWList[i]))
#                 logger.info(('append: ',PASFFWList[j]))
                PASFFWList_new.append(PASFFWList[j])
            elif cmp_==2:
#                 logger.info((' is before_ji ',PASFFWList[j],PASFFWList[i]))
                end=[x for x in PASFFWList[j][0].split('+')].index(PASFFWList[i][0].split('+')[0])
                fixtokens=PASFFWList[j][4][:end]+PASFFWList[i][4]
                shift=PASFFWList[i][2]
                freq=min(PASFFWList[i][3],PASFFWList[j][3])
                pattern='+'.join(PASFFWList[j][0].split('+')[:end]+PASFFWList[i][0].split('+'))
                PASFFWList_new.append((pattern,PASFFWList[i][1],shift,freq,fixtokens,PASFFWList[i][5]))
#                 logger.info(('append: ',(pattern,PASFFWList[i][1],shift,freq,fixtokens,PASFFWList[i][5])))
            elif cmp_==3:
#                 logger.info((' is before_ij ',PASFFWList[i],PASFFWList[j]))
                end=[x for x in PASFFWList[i][0].split('+')].index(PASFFWList[j][0].split('+')[0])
                fixtokens=PASFFWList[i][4][:end]+PASFFWList[j][4]
                shift=PASFFWList[j][2]
                freq=min(PASFFWList[i][3],PASFFWList[j][3])
                pattern='+'.join(PASFFWList[i][0].split('+')[:end]+PASFFWList[j][0].split('+'))
                PASFFWList_new.append((pattern,PASFFWList[j][1],shift,freq,fixtokens,PASFFWList[j][5]))   
#                 logger.info(('append: ',(pattern,PASFFWList[j][1],shift,freq,fixtokens,PASFFWList[j][5])))
        if len(cmp_result)==0 and (i not in visit_ele):
            PASFFWList_new.append(PASFFWList[i])
#             logger.info(('append: ',PASFFWList[i]))
        elif len(cmp_result)>0 and max(cmp_result)==-1 and (i not in visit_ele):
            PASFFWList_new.append(PASFFWList[i])
#             logger.info(('append: ',PASFFWList[i]))
    PASFFWList_new_RemoveDup=removeDupPASFFW(PASFFWList_new)  
#     logger.info('final merge result:')  
#     for x in PASFFWList_new_RemoveDup:
#         logger.info(x)
    del PASFFWList[:]
    PASFFWList.extend(PASFFWList_new_RemoveDup)

def removeDupPASFFW(PASFFWList):
    PASFFWList_RemoveDup=[]
    for PASFFW in PASFFWList:
        if containPASFFW(PASFFW,PASFFWList_RemoveDup)==False:
            PASFFWList_RemoveDup.append(PASFFW)
    return PASFFWList_RemoveDup

def containPASFFW(PASFFW1,PASFFWList):
    for PASFFW in PASFFWList:
        if PASFFW1[0]==PASFFW[0]:
            return True
    return False

def containPattern(pattern_cmp,patternList):
    for pattern in patternList:
        if pattern[:pattern.index('$')]==pattern_cmp[:pattern_cmp.index('$')]:
            return True
    return False

def remove_dup_pattern(patternList):
    pattern_new=[]
    for pattern in patternList:
        if containPattern(pattern,pattern_new)==False:
            pattern_new.append(pattern) 
    return pattern_new
    
def mergeNearPatterns(PASFFWList):
    #传入的PASFFWList是一个经过相同fix tokens合并的
    #迭代收敛的条件是  PASFFWList的大小不变
    
    PASFFWList_len=[]
    while True:
        PASFFWList_len.append(len(PASFFWList))
        get_final_tokens(PASFFWList)
        if len(PASFFWList_len)<3:
            continue
        else:
            if PASFFWList_len[-1]==PASFFWList_len[-2]==PASFFWList_len[-3]:
                break
        
        
    final_PASFFWList_print=''
    for PASFFW in PASFFWList:
        final_PASFFWList_print+=PASFFW[0]+', '+PASFFW[1]+', '+str(PASFFW[2])+', '+str(PASFFW[3])+', '+str(PASFFW[4])+'\n'  
    logger.info("get the final merged PASFFWList: \n"+final_PASFFWList_print)
    logger.info(str(PASFFWList))
       
    final_pattern_can=[]
    for PASFFW in PASFFWList:
        pattern=get_final_pattern(PASFFW)
        if pattern[:pattern.index('$')]=='':
#             final_pattern.extend([getWholePattern(x) for x in PASFFWList])
            final_pattern_can.append(getWholePattern(PASFFW))
        else:   
            final_pattern_can.append(pattern)
              
    final_pattern_print=''
    for pattern in final_pattern_can:
        final_pattern_print+=pattern+'\n'
    logger.info("get the final patterns can: \n"+final_pattern_print)
    
    
    final_pattern=remove_dup_pattern(final_pattern_can)
     
    return  final_pattern

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
        PASFFW_RDup_print+="same fix tokens: %s\n"%str(PASFFWList[0][4])
        for PASFFW in PASFFWList:
            PASFFW_RDup_print+=PASFFW[0]+', '+PASFFW[1]+', '+str(PASFFW[2])+', '+str(PASFFW[3])+'\n'
        PASFFW_RDup_print+='--------------------\n'
    logger.info("remove the dup PASFFW: \n"+PASFFW_RDup_print)
    
    final_PASFFWList=[]
    for PASFFWList_RemoveDup in PASFFWListList_RemoveDup:
        final_PASFFWList.append(get_final_PASFFW(PASFFWList_RemoveDup))
    
    final_PASFFWList_print=''
    for PASFFW in final_PASFFWList:
        final_PASFFWList_print+=PASFFW[0]+', '+PASFFW[1]+', '+str(PASFFW[2])+', '+str(PASFFW[3])+'\n'  
    logger.info("get the final PASFFWList: \n"+final_PASFFWList_print)
    
    logger.info("get the final PASFFWList: \n"+str(final_PASFFWList))
    final_pattern_list=mergeNearPatterns(final_PASFFWList)
    
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
    PASFFWList=filter_efficient(attribute2patterns_all)
    for PASFFW in PASFFWList:
        logger.info(PASFFW)
    return  PASFFWList

# def read_PASFFW(line):
#     eles=line.split(',')
    
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
    PASFFWList1=[(u'would+prevent', u'effect', 1, 15, [(u'would', 'MD'), (u'prevent', 'VB')], [(u'of', 'IN'), (u'dental', 'JJ'), (u'arch', 'NN'), (u'that', 'WDT'), (u'would', 'MD'), (u'prevent', 'VB'), (u'the', 'DT')]), 
     (u'low-calorie+{NN}+that', u'effect', 0, 13, [(u'low-calorie', 'JJ'), (u'sweetener', 'NN'), (u'that', 'IN')], [(u'is', 'VBZ'), (u'a', 'DT'), (u'low-calorie', 'JJ'), (u'sweetener', 'NN'), (u'that', 'IN'), (u'reduces', 'VBZ'), (u'caries', 'NNS')]), 
     (u'{NN}+because+it', u'effect', 0, 13, [(u'unit', 'NN'), (u'because', 'IN'), (u'it', 'PRP')], [(u'healthy', 'JJ'), (u'gingival', 'NN'), (u'unit', 'NN'), (u'because', 'IN'), (u'it', 'PRP'), (u'enables', 'VBZ'), (u'the', 'DT')]), 
     (u'that+reduces', u'effect', 1, 15, [(u'that', 'IN'), (u'reduces', 'VBZ')], [(u'is', 'VBZ'), (u'a', 'DT'), (u'low-calorie', 'JJ'), (u'sweetener', 'NN'), (u'that', 'IN'), (u'reduces', 'VBZ'), (u'caries', 'NNS')]), 
     (u'because+it', u'effect', 0, 29, [(u'because', 'IN'), (u'it', 'PRP')], [(u'healthy', 'JJ'), (u'gingival', 'NN'), (u'unit', 'NN'), (u'because', 'IN'), (u'it', 'PRP'), (u'enables', 'VBZ'), (u'the', 'DT')]), 
     (u'arch+that+would', u'effect', 0, 13, [(u'arch', 'NN'), (u'that', 'WDT'), (u'would', 'MD')], [(u'of', 'IN'), (u'dental', 'JJ'), (u'arch', 'NN'), (u'that', 'WDT'), (u'would', 'MD'), (u'prevent', 'VB'), (u'the', 'DT')]), 
     (u'that+would', u'effect', 0, 29, [(u'that', 'WDT'), (u'would', 'MD')], [(u'of', 'IN'), (u'dental', 'JJ'), (u'arch', 'NN'), (u'that', 'WDT'), (u'would', 'MD'), (u'prevent', 'VB'), (u'the', 'DT')]), 
     (u'{NN}+that', u'effect', 0, 29, [(u'sweetener', 'NN'), (u'that', 'IN')], [(u'is', 'VBZ'), (u'a', 'DT'), (u'low-calorie', 'JJ'), (u'sweetener', 'NN'), (u'that', 'IN'), (u'reduces', 'VBZ'), (u'caries', 'NNS')]), 
     (u'it+enables', u'effect', 1, 15, [(u'it', 'PRP'), (u'enables', 'VBZ')], [(u'healthy', 'JJ'), (u'gingival', 'NN'), (u'unit', 'NN'), (u'because', 'IN'), (u'it', 'PRP'), (u'enables', 'VBZ'), (u'the', 'DT')])]
    
    
    PASFFWList2=[(u'primarily+of', u'composed_of', 0, 29, [(u'primarily', 'RB'), (u'of', 'IN')], [(u'powders', 'NNS'), (u'are', 'VBP'), (u'composed', 'VBN'), (u'primarily', 'RB'), (u'of', 'IN'), (u'zinc', 'NNP'), (u'oxide', 'NN')]), (u'are+phosphoric', u'composed_of', 1, 15, [(u'are', 'VBP'), (u'phosphoric', 'JJ')], [(u'constituents', 'NNS'), (u'of', 'IN'), (u'the', 'DT'), (u'liquid', 'NN'), (u'are', 'VBP'), (u'phosphoric', 'JJ'), (u'acid', 'NN')]), (u'composed+of', u'composed_of', 0, 53, [(u'composed', 'VBN'), (u'of', 'IN')], [(u'a', 'DT'), (u'membrane', 'NN'), (u',', ','), (u'composed', 'VBN'), (u'of', 'IN'), (u'epithelium', 'NN'), (u'and', 'CC')]), ('{DT}+{NNS}', u'composed_of', 0, 29, [(u'the', 'DT'), (u'incorporates', 'NNS')], [(u'of', 'IN'), (u'arm', 'NN'), (u'are', 'VBP'), (u'the', 'DT'), (u'incorporates', 'NNS'), (u'proper', 'JJ'), (u'placement', 'NN')]), (u'made+of+metal', u'composed_of', 1, 22, [(u'made', 'VBN'), (u'of', 'IN'), (u'metal', 'NN')], [(u'a', 'DT'), (u'cone-shaped', 'JJ'), (u'base', 'NN'), (u'made', 'VBN'), (u'of', 'IN'), (u'metal', 'NN'), (u'or', 'CC')]), (u'{NN}+made+of', u'composed_of', 0, 26, [(u'base', 'NN'), (u'made', 'VBN'), (u'of', 'IN')], [(u'a', 'DT'), (u'cone-shaped', 'JJ'), (u'base', 'NN'), (u'made', 'VBN'), (u'of', 'IN'), (u'metal', 'NN'), (u'or', 'CC')]), (u'composed+{RB}+of', u'composed_of', 0, 13, [(u'composed', 'VBN'), (u'primarily', 'RB'), (u'of', 'IN')], [(u'powders', 'NNS'), (u'are', 'VBP'), (u'composed', 'VBN'), (u'primarily', 'RB'), (u'of', 'IN'), (u'zinc', 'NNP'), (u'oxide', 'NN')]), (u'cast+{NN}+of', u'composed_of', 0, 13, [(u'cast', 'NN'), (u'made', 'NN'), (u'of', 'IN')], [(u'is', 'VBZ'), (u'a', 'DT'), (u'cast', 'NN'), (u'made', 'NN'), (u'of', 'IN'), (u'materials', 'NNS'), (u'that', 'WDT')]), (u'of+calcium', u'composed_of', 1, 15, [(u'of', 'IN'), (u'calcium', 'NN')], [(u'.', '.'), (u'It', 'PRP'), (u'is', 'VBZ'), (u'composed', 'VBN'), (u'of', 'IN'), (u'calcium', 'NN'), (u'phosphate', 'NN')]), (u'are+{DT}+{NNS}', u'composed_of', 0, 13, [(u'are', 'VBP'), (u'the', 'DT'), (u'incorporates', 'NNS')], [(u'of', 'IN'), (u'arm', 'NN'), (u'are', 'VBP'), (u'the', 'DT'), (u'incorporates', 'NNS'), (u'proper', 'JJ'), (u'placement', 'NN')]), (u'composed+of+epithelium', u'composed_of', 1, 15, [(u'composed', 'VBN'), (u'of', 'IN'), (u'epithelium', 'NN')], [(u'a', 'DT'), (u'membrane', 'NN'), (u',', ','), (u'composed', 'VBN'), (u'of', 'IN'), (u'epithelium', 'NN'), (u'and', 'CC')]), (u'made+of', u'composed_of', 0, 82, [(u'made', 'VBN'), (u'of', 'IN')], [(u'a', 'DT'), (u'cone-shaped', 'JJ'), (u'base', 'NN'), (u'made', 'VBN'), (u'of', 'IN'), (u'metal', 'NN'), (u'or', 'CC')]), (u'of+zinc', u'composed_of', 1, 15, [(u'of', 'IN'), (u'zinc', 'NNP')], [(u'powders', 'NNS'), (u'are', 'VBP'), (u'composed', 'VBN'), (u'primarily', 'RB'), (u'of', 'IN'), (u'zinc', 'NNP'), (u'oxide', 'NN')]), (u'of+metal', u'composed_of', 1, 15, [(u'of', 'IN'), (u'metal', 'NN')], [(u'a', 'DT'), (u'cone-shaped', 'JJ'), (u'base', 'NN'), (u'made', 'VBN'), (u'of', 'IN'), (u'metal', 'NN'), (u'or', 'CC')]), (u'of+porcelain', u'composed_of', 1, 15, [(u'of', 'IN'), (u'porcelain', 'NN')], [(u'type', 'NN'), (u'of', 'IN'), (u'crown', 'NN'), (u'composed', 'VBN'), (u'of', 'IN'), (u'porcelain', 'NN'), (u'mixed', 'JJ')]), (u'of+materials', u'composed_of', 1, 15, [(u'of', 'IN'), (u'materials', 'NNS')], [(u'is', 'VBZ'), (u'a', 'DT'), (u'cast', 'NN'), (u'made', 'NN'), (u'of', 'IN'), (u'materials', 'NNS'), (u'that', 'WDT')]), (u'incorporates+proper', u'composed_of', 1, 15, [(u'incorporates', 'NNS'), (u'proper', 'JJ')], [(u'of', 'IN'), (u'arm', 'NN'), (u'are', 'VBP'), (u'the', 'DT'), (u'incorporates', 'NNS'), (u'proper', 'JJ'), (u'placement', 'NN')]), (u'{NN}+are', u'composed_of', 0, 29, [(u'liquid', 'NN'), (u'are', 'VBP')], [(u'constituents', 'NNS'), (u'of', 'IN'), (u'the', 'DT'), (u'liquid', 'NN'), (u'are', 'VBP'), (u'phosphoric', 'JJ'), (u'acid', 'NN')])]
    
    PASFFWList3=[(u'{NN}+made+of', u'composed_of', 0, 26, [(u'base', 'NN'), (u'made', 'VBN'), (u'of', 'IN')], [(u'a', 'DT'), (u'cone-shaped', 'JJ'), (u'base', 'NN'), (u'made', 'VBN'), (u'of', 'IN'), (u'metal', 'NN'), (u'or', 'CC')]),
                (u'cast+{NN}+of', u'composed_of', 0, 13, [(u'cast', 'NN'), (u'made', 'NN'), (u'of', 'IN')], [(u'is', 'VBZ'), (u'a', 'DT'), (u'cast', 'NN'), (u'made', 'NN'), (u'of', 'IN'), (u'materials', 'NNS'), (u'that', 'WDT')]),
                (u'of+calcium', u'composed_of', 1, 15, [(u'of', 'IN'), (u'calcium', 'NN')], [(u'.', '.'), (u'It', 'PRP'), (u'is', 'VBZ'), (u'composed', 'VBN'), (u'of', 'IN'), (u'calcium', 'NN'), (u'phosphate', 'NN')])]
    
    PASFFWList4=[(u'situated+on', u'located', 1, 15, [(u'situated', 'VBN'), (u'on', 'IN')], [(u'irregular', 'JJ'), (u'spaces', 'NNS'), (u'that', 'WDT'), (u'are', 'VBP'), (u'situated', 'VBN'), (u'on', 'IN'), (u'either', 'DT')]), (u'located+between', u'located', 1, 15, [(u'located', 'VBN'), (u'between', 'IN')], [(u'abutment', 'NN'), (u'is', 'VBZ'), (u'an', 'DT'), (u'abutment', 'NN'), (u'located', 'VBN'), (u'between', 'IN'), (u'the', 'DT')]), (u'pointed+{RB}+situated', u'located', 0, 13, [(u'pointed', 'VBD'), (u'teeth', 'RB'), (u'situated', 'VBN')], [(u'the', 'DT'), (u'four', 'CD'), (u'pointed', 'VBD'), (u'teeth', 'RB'), (u'situated', 'VBN'), (u'one', 'CD'), (u'on', 'IN')]), (u'{NN}+located', u'located', 0, 29, [(u'cavity', 'NN'), (u'located', 'VBN')], [(u'within', 'IN'), (u'the', 'DT'), (u'oral', 'JJ'), (u'cavity', 'NN'), (u'located', 'VBN'), (u'beneath', 'IN'), (u'the', 'DT')]), (u'teeth+situated', u'located', 0, 29, [(u'teeth', 'RB'), (u'situated', 'VBN')], [(u'the', 'DT'), (u'four', 'CD'), (u'pointed', 'VBD'), (u'teeth', 'RB'), (u'situated', 'VBN'), (u'one', 'CD'), (u'on', 'IN')]), (u'{NN}+located', u'located', 0, 29, [(u'abutment', 'NN'), (u'located', 'VBN')], [(u'abutment', 'NN'), (u'is', 'VBZ'), (u'an', 'DT'), (u'abutment', 'NN'), (u'located', 'VBN'), (u'between', 'IN'), (u'the', 'DT')]), (u'that+are+situated', u'located', 0, 13, [(u'that', 'WDT'), (u'are', 'VBP'), (u'situated', 'VBN')], [(u'irregular', 'JJ'), (u'spaces', 'NNS'), (u'that', 'WDT'), (u'are', 'VBP'), (u'situated', 'VBN'), (u'on', 'IN'), (u'either', 'DT')]), (u'located+beneath', u'located', 1, 30, [(u'located', 'VBN'), (u'beneath', 'IN')], [(u'within', 'IN'), (u'the', 'DT'), (u'oral', 'JJ'), (u'cavity', 'NN'), (u'located', 'VBN'), (u'beneath', 'IN'), (u'the', 'DT')]), (u'{DT}+{NN}+located', u'located', 0, 13, [(u'an', 'DT'), (u'abutment', 'NN'), (u'located', 'VBN')], [(u'abutment', 'NN'), (u'is', 'VBZ'), (u'an', 'DT'), (u'abutment', 'NN'), (u'located', 'VBN'), (u'between', 'IN'), (u'the', 'DT')]), (u'situated+one', u'located', 1, 15, [(u'situated', 'VBN'), (u'one', 'CD')], [(u'the', 'DT'), (u'four', 'CD'), (u'pointed', 'VBD'), (u'teeth', 'RB'), (u'situated', 'VBN'), (u'one', 'CD'), (u'on', 'IN')]), (u'are+situated', u'located', 0, 29, [(u'are', 'VBP'), (u'situated', 'VBN')], [(u'irregular', 'JJ'), (u'spaces', 'NNS'), (u'that', 'WDT'), (u'are', 'VBP'), (u'situated', 'VBN'), (u'on', 'IN'), (u'either', 'DT')]), (u'{NN}+located+beneath', u'located', 1, 14, [(u'cavity', 'NN'), (u'located', 'VBN'), (u'beneath', 'IN')], [(u'within', 'IN'), (u'the', 'DT'), (u'oral', 'JJ'), (u'cavity', 'NN'), (u'located', 'VBN'), (u'beneath', 'IN'), (u'the', 'DT')])]
    
    PASFFWList5=[(u'{DT}+{NN}+located', u'located', 0, 13, [(u'an', 'DT'), (u'abutment', 'NN'), (u'located', 'VBN')], [(u'abutment', 'NN'), (u'is', 'VBZ'), (u'an', 'DT'), (u'abutment', 'NN'), (u'located', 'VBN'), (u'between', 'IN'), (u'the', 'DT')]), 
                (u'situated+one', u'located', 1, 15, [(u'situated', 'VBN'), (u'one', 'CD')], [(u'the', 'DT'), (u'four', 'CD'), (u'pointed', 'VBD'), (u'teeth', 'RB'), (u'situated', 'VBN'), (u'one', 'CD'), (u'on', 'IN')]), 
                (u'are+situated', u'located', 0, 29, [(u'are', 'VBP'), (u'situated', 'VBN')], [(u'irregular', 'JJ'), (u'spaces', 'NNS'), (u'that', 'WDT'), (u'are', 'VBP'), (u'situated', 'VBN'), (u'on', 'IN'), (u'either', 'DT')]), 
                (u'{NN}+located+beneath', u'located', 1, 14, [(u'cavity', 'NN'), (u'located', 'VBN'), (u'beneath', 'IN')], [(u'within', 'IN'), (u'the', 'DT'), (u'oral', 'JJ'), (u'cavity', 'NN'), (u'located', 'VBN'), (u'beneath', 'IN'), (u'the', 'DT')])]

    PASFFWList6=[]
    PASFFWList=PASFFWList2 
    PASFFWList_len=[]
    i=0
    logger.info('merge begin')
    while True:
        if i>3:
            break
        print 'cycle: '+str(i)
        print 'PASFFWList length: '+str(len(PASFFWList))
        PASFFWList_len.append(len(PASFFWList))
        get_final_tokens(PASFFWList)
        i+=1
        if len(PASFFWList_len)<3:
            continue
        if PASFFWList_len[-1]==PASFFWList_len[-2]==PASFFWList_len[-3]:
            break
         
    for x in PASFFWList:
        print x

def test_get_final_pattern():
    PASFFWList=[(u'generated+by+functional', u'result_from', 1, 15, [(u'generated', 'VBN'), (u'by', 'IN'), (u'functional', 'JJ')], [(u'is', 'VBZ'), (u'the', 'DT'), (u'stresses', 'NNS'), (u'generated', 'VBN'), (u'by', 'IN'), (u'functional', 'JJ'), (u'or', 'CC')]), (u'{NN}+resulting+from+a', u'result_from', 1, 13, [(u'atrophy', 'NN'), (u'resulting', 'VBG'), (u'from', 'IN'), (u'a', 'DT')], [(u'is', 'VBZ'), (u'an', 'DT'), (u'atrophy', 'NN'), (u'resulting', 'VBG'), (u'from', 'IN'), (u'a', 'DT'), (u'reduction', 'NN')]), (u'{NN}+resulting+from+loss', u'result_from', 1, 13, [(u'atrophy', 'NN'), (u'resulting', 'VBG'), (u'from', 'IN'), (u'loss', 'NN')], [(u'of', 'IN'), (u'a', 'DT'), (u'tooth', 'JJ'), (u'resulting', 'VBG'), (u'from', 'IN'), (u'loss', 'NN'), (u'of', 'IN')]), (u'{NN}+resulting+from+the', u'result_from', 1, 13, [(u'atrophy', 'NN'), (u'resulting', 'VBG'), (u'from', 'IN'), (u'the', 'DT')], [(u'form', 'NN'), (u'of', 'IN'), (u'metal', 'NN'), (u'resulting', 'VBG'), (u'from', 'IN'), (u'the', 'DT'), (u'swaging', 'NN')])]
    for PASFFW in PASFFWList:
        print get_final_pattern(PASFFW)
    
    
if __name__=='__main__':
    start = datetime.datetime.now()
    logger.info(start)
    print start
    main()
#     test()
#     test1()
#     test2()
#     test3()
#     test_get_final_tokens()
#     test_get_final_pattern()
    end = datetime.datetime.now()
    logger.info(end)
    print end
    logger.info("cost time: "+str((end - start).microseconds))
    print str((end - start).seconds)+' s'