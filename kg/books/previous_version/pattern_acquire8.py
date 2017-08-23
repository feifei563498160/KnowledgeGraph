#coding=utf-8
'''
Created on 2017��4��10��

@author: FeiFei
'''
import os
from kg.util.mylogger import log_console_and_file
from kg.util.file import load_json
import codecs
import nltk
from itertools import product
import kg.books.regular_verify7
import datetime
from kg.util.string import cut_truple_list
from _collections import defaultdict
from collections import Counter
import json

path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
path_log_output=path_project+os.sep+"output"+os.sep+"log_pattern_acquire_auto8_1.txt"
logger=log_console_and_file(path_log_output)

prefix_window_size=5
TOP=10  #TOP means get the top 1/10 pattern candidate
CYCLE=2 #the max iter num used to shift
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
#     print attribute_value_tokens,definition_tokens
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

def getChunkPrefix(size,attribute_value_tokens,sentTokens):
    match_pos=get_match_pos(attribute_value_tokens,sentTokens)
    can_pos_set=[]
    start=match_pos[0]
    if start==-1:
        logger.info('this value cannot match')
#         logger.info('sent:'+str((sentTokens)))
#         logger.info('attribute_value:'+str((attribute_value_tokens)))
        return []
    
    window=[]
    prefixShiftSentList=[]
    '''
    when the start<size, we fetch the window util start from 0,
    when the start>=size, we fetch the window util start from start-size,
    '''
    
    for i in range(CYCLE):
#     for i in range(size):
        if start<size and start<len(sentTokens):
            can_pos_set=get_can_pos_set(start)
            window=sentTokens[:start]
        elif start>=size and start<len(sentTokens):
            can_pos_set=get_can_pos_set(size)
            window=sentTokens[start-size:start]
        else:
            continue
        
        for can_pos in can_pos_set:
            prefix=[]
            for pos in can_pos:
                prefix.append(window[pos])
            prefixShiftSentList.append((prefix,i,sentTokens))
        start=start+1
    
    return  prefixShiftSentList

def getPrefix(size,attribute_value_tokens,sentTokens): 
    chunks=cut_truple_list(attribute_value_tokens,[(';', ':')])
    prefixShiftSentList=[]
    for chunk in chunks:
        prefixShiftSentList.extend(getChunkPrefix(size,chunk,sentTokens))
    return prefixShiftSentList

def truple2list(truple):
    return [truple[0],'{'+truple[1]+'}']
        
def getPatternCan(prefixShiftSentList):
    patternShiftFixtokenSentList=[]
    for  (fixs_token,shift,sent) in prefixShiftSentList:
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
        else:
            continue
        
        for truple in truple_list:
            pattern_real='+'.join(truple)
            patternShiftFixtokenSentList.append((pattern_real,shift,fixs_token,sent))
            
    return patternShiftFixtokenSentList


'''
the flowing methods aim to filter patterns according to some rules
'''
def existSpecialToken(pattern):
    special_token=['.','{.}',',','{,}',';','{:}']
    for token in pattern.split('+'):
        if token in special_token:
            return True
    return False

def isAllPOS(pattern_real):
    pattern_words=pattern_real.split('+')
    for pattern_word in pattern_words:
        if '{' not in pattern_word:
            return False
    return True

def filterSpecialTokenAndFullPOS(pSFSList):
    filter1=[]
#     logger.info('----------------------------------------')
#     logger.info(pSFSList)
#     logger.info('......')
    for pSFS in pSFSList:
#         logger.info(pSFS)
        pattern=pSFS[0]
#         logger.info(pattern)
        if existSpecialToken(pattern)==False and len(pattern.split('+'))>=2 and isAllPOS(pattern)==False:
#         if len(pattern_can.split('+'))>=2:
            filter1.append(pSFS)
    return filter1

def filterWrongShift(pSFSList):
    filter2=[]       
    for pSFS in pSFSList:
        pattern=pSFS[0]
        shift=pSFS[1]
        if len(pattern[0].split('+'))>=shift:
            filter2.append(pSFS)
    return filter2

def containList(list1,list2):
    #list1 contain list2
    if len(list2)>len(list1):
        return -1
    for i in range(len(list2)):
        if list1[i]!=list2[i]:
            return -1
    return i
    
def getFreqAndSentList(pSFS_cmp,pSFSList): 
    '''
            这个计算方式将不同shift的pattern 只要patern相同  就认为是相同pattern
    '''   
    freq=0
    pattern_cmp=pSFS_cmp[0]
    shift_cmp=pSFS_cmp[1]
    fixTokens_cmp=pSFS_cmp[2]
    sentList=[]
    for pSFS in pSFSList:
        pattern=pSFS[0]
        shift=pSFS[1]
        pos=containList(pattern.split('+'),pattern_cmp.split('+'))
        if pos!=-1 and fixTokens_cmp==pSFS[2] and pos+(shift-shift_cmp)!=len(pattern.split('+'))-1:
                print 'shift is different'
                print pSFS_cmp,'\nAND\n',pSFS
        if pos!=-1 and pos+(shift-shift_cmp)==len(pattern.split('+'))-1:
#         if pattern.find(pattern_cmp)!=-1 and shift_cmp==shift:
            #'is+{DT}', 1, [(u'is', 'VBZ'), (u'any', 'DT')] 
            #'is+{DT}', 0, [(u'is', 'VBZ'), (u'the', 'DT')],
            #they have same pattern but the shift is different, because their fix token is different
            freq+=1
            if contain(sentList, pSFS[3])==False:
                sentList.append(pSFS[3])
    return (pattern_cmp,shift_cmp,freq,fixTokens_cmp,len(sentList),sentList)    

def contain(l1,ele_cmp):
    for ele in l1:
        if ele_cmp==ele:
            return True
    return False

def getFreqAndSentListAll(pSFSList):
    pSFFLSsList=[]
    for pSFS in pSFSList:
        pSFFLSsList.append(getFreqAndSentList(pSFS,pSFSList))
    return pSFFLSsList

def getTopEles(pattern_tuples,n):
    sorted_patterns=sorted(pattern_tuples,key=lambda asd:asd[2],reverse=True)
    return sorted_patterns[:n+1]

def filterGrammerWrong(pSFSList):
    filter1=filterSpecialTokenAndFullPOS(pSFSList)
    filter2=filterWrongShift(filter1)
    filter_pSFFLSsList=getTopEles(getFreqAndSentListAll(filter2),len(filter2)/TOP)
    return filter_pSFFLSsList

def valuelist2values(dict_can):   
    attribute2single_patttern=[]    
    for key,value_list in dict_can.iteritems():
        for value in value_list:
            attribute2single_patttern.append((key,)+value)
    return attribute2single_patttern
   
def filterPatternNotOnly(attribute2PSFFLSsList):
    '''
    This function filter the patterns that cann't only belong to one attribute, and return pASFFS
            这个函数是将不能唯一属于一个属性的pattern过滤掉 
    '''
    aPSFFLSsList=valuelist2values(attribute2PSFFLSsList)
    #pattern2attributes键为真实的pattern 值为该pattern映射的属性
    pattern2attributes=defaultdict(set)
    #pattern2whole_pattern键为真实的pattern 值为包含了后缀符号如$ # @的完整的pattern
    pattern2pattern_whole={}
    for aPSFFLSs in aPSFFLSsList: 
        attribute=aPSFFLSs[0]
        pattern=aPSFFLSs[1]
        pattern2attributes[pattern].add(attribute)
        pattern2pattern_whole[pattern]=aPSFFLSs
        
    pattern2single_attributes={}    
    for pattern in pattern2attributes.keys():
        if len(pattern2attributes[pattern])>=2:
            pattern2attributes.pop(pattern)
        else:
            #得到pattern和属性的唯一对应
            pattern2single_attributes[pattern]=list(pattern2attributes[pattern])[0]
            
    pASFFSsList_only=[]
    for pattern in pattern2single_attributes.keys():
        #aPSFWF=attributePatternShiftFixtokenWindowFreq
        aPSFFLSs=pattern2pattern_whole[pattern]
        pASFFSsList_only.append((aPSFFLSs[1],aPSFFLSs[0],aPSFFLSs[2],aPSFFLSs[3],aPSFFLSs[4],aPSFFLSs[5],aPSFFLSs[6],))
    return pASFFSsList_only

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

def get_final_pASFFLSs(pASFFLSsList):
    #这个list中的fix_tokens都是一样的  只需要根据fix_tokens 来决定最终的pattern形式
    tokens=pASFFLSsList[0][4]
    pattern_final=rebulidPattern(tokens)
    shift=pASFFLSsList[0][2]
    freq=pASFFLSsList[0][3]
#     for PASFFW in PASFFWList:
#         freq+=PASFFW[3]
    return (pattern_final,pASFFLSsList[0][1],shift,freq,pASFFLSsList[0][4],pASFFLSsList[0][5],pASFFLSsList[0][6])  

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

def get_final_pattern(pASFFLSs):
    fix_tokens=pASFFLSs[4]
    rules=['{NN}|{NNS}|{NNP}|{NNPS}+:',
           '{RB}+is+{JJ}',
           '{VBG}|{VBP}|{VBN}|{VBD}|{VBZ}|{VB}+{IN}',
           '{VBG}|{VBP}|{VBN}|{VBD}|{VBZ}|{VB}+{RB}+{IN}',
           '{PRP}+{VBZ}',
#            '{MD}+{VB}',
           'to+{VB}',
#            'is+not+a',
#            'is+a',
#            'is+the',
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
    shift=pASFFLSs[2]
    freq=pASFFLSs[3]
    
    return "%s$%d@%d" % (pattern_final,shift,freq)

def getWholePattern(pASFFLSs):
    return "%s$%d@%d" % (pASFFLSs[0],pASFFLSs[2],pASFFLSs[3])

def containIntersectPASFFW(PASFFW_cmp,PASFFWListList):
    for i in range(len(PASFFWListList)):
        for PASFFW in PASFFWListList[i]:
            if is_intersectPASFFW(PASFFW_cmp,PASFFW)>=0:
                return i
    return -1

def intersectList(listlist1,listlist2):
    result=[]
    for list1 in listlist1:
        flag=0
        for list2 in listlist2:
            if list1==list2:
                flag=1
        if flag==1:
            result.append(list1) 
    return []

def get_new_tuple(PASFFW1,PASFFW2,sent):
    fix_tokens1=PASFFW1[4]
    fix_tokens2=PASFFW2[4]
    match1=get_match_pos_token(fix_tokens2,sent)
    match2=get_match_pos_token(fix_tokens1,sent)
    if match1[0]!=-1 and match2[0]==-1: 
        if is_intersect(match1,match2):
            start=min(match1[0],match2[0])
            end=max(match1[1],match2[1])
            fix_tokens_final=sent[start:end]
            if match1[1]<match2[1]:
                shift=PASFFW2[2]
            else:
                shift=PASFFW1[2]
            freq=min(PASFFW1[3],PASFFW2[3])
            if match1[0]<match2[0]:
                pattern_final='+'.join(PASFFW1[0].split('+')[:match2[0]-match1[0]]+PASFFW2[0].split('+'))
            else:
                pattern_final='+'.join(PASFFW2[0].split('+')[:match1[0]-match2[0]]+PASFFW1[0].split('+'))
        else:
            return []
    else:
        return []
    return  (pattern_final,PASFFW1[1],shift,freq,fix_tokens_final) 
   
def is_intersectPASFFW(PASFFW1,PASFFW2):
    sents1=PASFFW1[6]
    sents2=PASFFW2[6]
    commonSents=intersectList(sents1,sents2)
    if len(commonSents)==0:
        return -1
    sents_final=[]
    aheadPartOfTupleList=[]
    for sent in commonSents:
        result=get_new_tuple(PASFFW1,PASFFW2,sent)
        if len(result)!=0:       
            sents_final.append(sent)
            aheadPartOfTupleList.append(result)
    if len(sents_final)!=0:
        PASFFW_new=aheadPartOfTupleList[0]+(sents_final,)
        return PASFFW_new
    else:
        return -1
    
#相交可以直接取最大边界  然后 从原sent中取tokens
def is_cover(range1,range2):
    '''whether range1 cover range2'''
    if range2[0]>=range1[0] or range2[1]<=range1[1]:   
        return True
    else:
        return False
    
def is_intersect(range1,range2):
    '''whether two ranges is intersected'''
    if not (range1[1]<=range2[0] or range2[1]<=range1[0] ):   
        return True
    else:
        return False
    
def get_final_tokens(pASFFLSsList):
    #合并所有可能的首尾有交叉的pattern 但是只有在同一个句子中出现才能被合并
    #如果跟任何一个都不相交  就保留下来
    if len(pASFFLSsList)==1:
        return pASFFLSsList
    pASFFLSsList_new=[]
    visit_ele=set([])
    for i in range(len(pASFFLSsList)):
#         logger.info('i=%d' % i)
        #用以判断第i个pASFFLSs和其后的pASFFLSs是否有相交 如果没有 且没有被别的pASFFLSs 比较过 ，则它自己就可以作为单独的pASFFLSs放入最终的结果
        cmp_result=[]
        for j in range(i+1,len(pASFFLSsList),1):
            cmp_=is_intersectPASFFW(pASFFLSsList[i],pASFFLSsList[j])
            if cmp_==-1:
#                 logger.info((' have no intersect ',PASFFWList[i],PASFFWList[j]))
                continue
            else:
                visit_ele.add(i)
                visit_ele.add(j)
                pASFFLSsList_new.append(cmp_)
            cmp_result.append(cmp_)
               
        if len(cmp_result)==0 and (i not in visit_ele):
            pASFFLSsList_new.append(pASFFLSsList[i])
#             logger.info(('append: ',PASFFWList[i]))
        elif len(cmp_result)>0 and max(cmp_result)==-1 and (i not in visit_ele):
            pASFFLSsList_new.append(pASFFLSsList[i]) 
            
    pASFFLSsList_new_RemoveDup=removeDupPASFFLSs(pASFFLSsList_new)  
    logger.info('final merge result:')  
    for x in pASFFLSsList_new_RemoveDup:
        logger.info(x)
    del pASFFLSsList[:]
    pASFFLSsList.extend(pASFFLSsList_new_RemoveDup)
              
def removeDupPASFFLSs(pASFFLSsList):
    pASFFLSsList_RemoveDup=[]
    for pASFFLSs in pASFFLSsList:
        if containPASFFLSs(pASFFLSs,pASFFLSsList_RemoveDup)==False:
            pASFFLSsList_RemoveDup.append(pASFFLSs)
    return pASFFLSsList_RemoveDup

def containPASFFLSs(pASFFLSs_cmp,pASFFLSsList):
    for pASFFLSs in pASFFLSsList:
        if pASFFLSs_cmp[0]==pASFFLSs[0]:
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
    
def mergeNearPatterns(pASFFLSsList):
    #传入的PASFFWList是一个经过相同fix tokens合并的
    #迭代收敛的条件是  PASFFWList的大小不变
    
    pASFFLSsList_len=[]
    while True:
        pASFFLSsList_len.append(len(pASFFLSsList))
        get_final_tokens(pASFFLSsList)
        if len(pASFFLSsList_len)<3:
            continue
        else:
            if pASFFLSsList_len[-1]==pASFFLSsList_len[-2]==pASFFLSsList_len[-3]:
                break
        
    final_pASFFLSsList_print=''
    for pASFFLSs in pASFFLSsList:
        final_pASFFLSsList_print+=pASFFLSs[0]+', '+pASFFLSs[1]+', '+str(pASFFLSs[2])+', '+str(pASFFLSs[3])+', '+str(pASFFLSs[4])+'\n'  
    logger.info("get the final merged pASFFLSsList: \n"+final_pASFFLSsList_print)
    logger.info(str(pASFFLSsList))
       
    final_pattern_can=[]
    for pASFFLSs in pASFFLSsList:
        pattern=get_final_pattern(pASFFLSs)
        if pattern[:pattern.index('$')]=='':
#             final_pattern.extend([getWholePattern(x) for x in pASFFLSsList])
            final_pattern_can.append(getWholePattern(pASFFLSs))
        else:   
            final_pattern_can.append(pattern)
              
    final_pattern_print=''
    for pattern in final_pattern_can:
        final_pattern_print+=pattern+'\n'
    logger.info("get the final patterns can: \n"+final_pattern_print)
    
    final_pattern=remove_dup_pattern(final_pattern_can)
     
    return  final_pattern

def merge_pattern(pASFFLSsList):
    print "----------------merge patterns of attribute: %s ----------------" % pASFFLSsList[0][1]
    logger.info("----------------merge patterns of attribute: %s ----------------" % pASFFLSsList[0][1])
    #PASFFW: patternAttributeShiftFreqFixtokenWindow
    #将来自同一fix_tokens的pattern合并到一个list中
    pASFFLSsList_print=''
    for pASFFLSs in pASFFLSsList:
        pASFFLSsList_print+=pASFFLSs[0]+', '+pASFFLSs[1]+', '+str(pASFFLSs[2])+', '+str(pASFFLSs[3])+'\n'
        
    logger.info("---------------patterns before merging :\n%s---------------" % pASFFLSsList_print)
    
    pASFFLSsListList=[] 
    pos_visit=[]
    for i in range(len(pASFFLSsList)):
        #如果i被访问过 则pASFFLSsList[i]就一定已经被添加到某个子list中
        if i in pos_visit:
                continue
        pos_i=contain_PASFFW_by_Fixtokens(pASFFLSsList[i],pASFFLSsListList)
        if pos_i==-1:
            pattern_can_i=[]
            pattern_can_i.append(pASFFLSsList[i])
            pos_visit.append(i)
            pASFFLSsListList.append(pattern_can_i)
        pos_i=contain_PASFFW_by_Fixtokens(pASFFLSsList[i],pASFFLSsListList)
        for j in range(i+1,len(pASFFLSsList),1):
            if j in pos_visit:
                continue
            pos_j=contain_PASFFW_by_Fixtokens(pASFFLSsList[j],pASFFLSsListList)
            if pos_j==pos_i:
                pASFFLSsListList[pos_i].append(pASFFLSsList[j])
                pos_visit.append(j)
    
    pASFFLSs_print=''                
    for pASFFLSsList in pASFFLSsListList:
        pASFFLSs_print+="same fix tokens: %s\n"%str(pASFFLSsList[0][4])
        for pASFFLSs in pASFFLSsList:
            pASFFLSs_print+=pASFFLSs[0]+', '+pASFFLSs[1]+', '+str(pASFFLSs[2])+', '+str(pASFFLSs[3])+'\n'
        pASFFLSs_print+='----------\n'
    logger.info("merge by the same fix tokens: \n"+pASFFLSs_print)
    
    final_pASFFLSsList=[]
    for pASFFLSsList in pASFFLSsListList:
        final_pASFFLSsList.append(get_final_pASFFLSs(pASFFLSsList))

    final_pASFFLSsList_print=''
    for pASFFLSs in final_pASFFLSsList:
        final_pASFFLSsList_print+=pASFFLSs[0]+', '+pASFFLSs[1]+', '+str(pASFFLSs[2])+', '+str(pASFFLSs[3])+'\n'  
    logger.info("get the final PASFFWList: \n"+final_pASFFLSsList_print)
    
#     logger.info("get the final PASFFWList: \n"+str(final_pASFFLSsList))
    final_pattern_list=mergeNearPatterns(final_pASFFLSsList)
    
    return final_pattern_list

def merge_pattern_all(PASFFLSsList):
    '''
             此方法用于合并pattern，并使用合并后的pattern 重新计算频率
    '''
    attribute2PASFFLSsList=defaultdict(list)
    for PASFFLSs in PASFFLSsList:
        attribute=PASFFLSs[1]
        attribute2PASFFLSsList[attribute].append(PASFFLSs)
    
    attribute2patterns_merge=[]
    for attribute,pASFFLSsList in attribute2PASFFLSsList.iteritems():
        attribute2patterns_merge.append((attribute,merge_pattern(pASFFLSsList)))
        
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
    attribute2PSFSList=defaultdict(list)
    attribute2prefix=defaultdict(list)
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
                attribute_value_text=nltk.word_tokenize(attribute_value)
                attribute_value_tokens=nltk.pos_tag(attribute_value_text)
                sentTokenList=cut_truple_list(definition_tokens,[('.', '.')])
                prefixShiftSentList=[]
                for sentToken in sentTokenList:
                    prefixTmp=getPrefix(prefix_window_size,attribute_value_tokens,sentToken)
                    if len(prefixTmp)!=0:
                        prefixShiftSentList.extend(prefixTmp)
                for prefixShiftSent in prefixShiftSentList:
                    prefix=prefixShiftSent[0]
                    if len(prefix)>=prefixShiftSent[1]:
                        attribute2prefix[attribute_name].append(('+'.join([x[1] for x in prefix]),prefixShiftSent[1],prefix))
                    
                pSFSList=getPatternCan(prefixShiftSentList)
                attribute2PSFSList[attribute_name].extend(pSFSList)
#             logger.info('\n')
    #PSFFS add the freq in tuple
#     for item in attribute2prefix.iteritems():
#         logger.info(item[0]+":")
#         logger.info(str(item[1]))
    return attribute2PSFSList
#     return attribute2prefix

def indexVB(POSList):
    for i in range(len(POSList)):
        if POSList[i] in ['VB','VBD','VBG','VBN','VBP','VBZ']:
            return i
    return -1

def getVBContext(attribute2prefixList):
    VBContextList=[]
#     for item in attribute2prefixList.iteritems():
#         for prefix in item[1]:
    prefixList=[]   
    for attribute,prefix in attribute2prefixList.iteritems():
        prefixList.extend(prefix)
    
    prefixListContext=[]
    
    for prefix in prefixList:
        POSList=prefix[0].split('+')
        VBPos=indexVB(POSList)
        if VBPos==-1:
            continue
        if VBPos>=len(POSList)-2:
            if len(POSList)<=3:
                context='+'.join(POSList[:])
                VBContextList.append(context)
                prefixListContext.append((context,prefix[0],prefix[1],prefix[2]))
            else:  
                context='+'.join(POSList[len(POSList)-3:])
                VBContextList.append(context)
                prefixListContext.append((context,prefix[0],prefix[1],prefix[2]))
        elif VBPos==len(POSList)-3:
            if len(POSList)<=4:
                context='+'.join(POSList[:-1])
                VBContextList.append(context)
                prefixListContext.append((context,prefix[0],prefix[1],prefix[2]))
            else:
                context='+'.join(POSList[len(POSList)-4:-1])
                VBContextList.append(context)
                prefixListContext.append((context,prefix[0],prefix[1],prefix[2]))
        elif VBPos==len(POSList)-4:
            if len(POSList)<=5:
                context='+'.join(POSList[:-2])
                VBContextList.append(context)
                prefixListContext.append((context,prefix[0],prefix[1],prefix[2]))
            else:
                context='+'.join(POSList[len(POSList)-5:-2])
                VBContextList.append(context)
                prefixListContext.append((context,prefix[0],prefix[1],prefix[2]))
                                  
    logger.info('\n----------------VBContext num: ------------------')
    c_VBContext=Counter(VBContextList) 
    for item in sorted(c_VBContext.iteritems(),key=lambda asd:asd[1],reverse=True):
        logger.info(item[0]+': '+str(item[1]))
    
    logger.info('\n----------------VBContext seq: ------------------')
    for tup in sorted(prefixListContext,key=lambda asd:asd[0],reverse=False):
        logger.info(tup)
     
def filterPatterns(attribute2PSFSList):
    logger.info('------------------filter the patterns--------------------')
    attribute2PSFFLSsList={}   
    for attribue,PSFSList in attribute2PSFSList.iteritems():
        print 'attribute: '+attribue,"attribute length:",len(PSFSList) 
        logger.info('final attribute: %s'%attribue)
        logger.info('patterns can original length: '+str(len(PSFSList)))
        filterPSFFLSsList=filterGrammerWrong(PSFSList)
        attribute2PSFFLSsList[attribue]=filterPSFFLSsList
        logger.info('final patterns length %d:' % len(filterPSFFLSsList))
        logger.info(str(filterPSFFLSsList)+'\n')
    PASFFLSsList=filterPatternNotOnly(attribute2PSFFLSsList)
    logger.info("final PASFFLSs: ")
    for PASFFLSs in PASFFLSsList:
        logger.info(PASFFLSs)
    return  PASFFLSsList   
        
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
    #acquire all the pattern candidates
    attribute2PSFSList=acquire_patterns(data)
#     getVBContext(attribute2PSFSList)
    #filter the pattern candidates
    PASFFLSsList=filterPatterns(attribute2PSFSList)
    #merge the pattern candidates
    patterns=merge_pattern_all(PASFFLSsList)
     
    patterns_priority=calculate_proprity2pattern(patterns)
    logger.info("has acquired all the patterns")
    json.dump(patterns_priority, codecs.open(path_pattern, 'w','utf-8'),ensure_ascii=False,indent=2)
#     json.dump(dict_reverse(patterns), codecs.open(path_pattern_reverse, 'w','utf-8'),ensure_ascii=False,indent=2)
#     dict_sorted_value(dict_reverse(patterns),path_pattern_reverse_sorted)
    sorted_by_attribute_pattern(patterns_priority,path_pattern_sorted)
    logger.info("output over")


def test_get_final_pattern():
    PASFFWList=[(u'generated+by+functional', u'result_from', 1, 15, [(u'generated', 'VBN'), (u'by', 'IN'), (u'functional', 'JJ')], [(u'is', 'VBZ'), (u'the', 'DT'), (u'stresses', 'NNS'), (u'generated', 'VBN'), (u'by', 'IN'), (u'functional', 'JJ'), (u'or', 'CC')]), (u'{NN}+resulting+from+a', u'result_from', 1, 13, [(u'atrophy', 'NN'), (u'resulting', 'VBG'), (u'from', 'IN'), (u'a', 'DT')], [(u'is', 'VBZ'), (u'an', 'DT'), (u'atrophy', 'NN'), (u'resulting', 'VBG'), (u'from', 'IN'), (u'a', 'DT'), (u'reduction', 'NN')]), (u'{NN}+resulting+from+loss', u'result_from', 1, 13, [(u'atrophy', 'NN'), (u'resulting', 'VBG'), (u'from', 'IN'), (u'loss', 'NN')], [(u'of', 'IN'), (u'a', 'DT'), (u'tooth', 'JJ'), (u'resulting', 'VBG'), (u'from', 'IN'), (u'loss', 'NN'), (u'of', 'IN')]), (u'{NN}+resulting+from+the', u'result_from', 1, 13, [(u'atrophy', 'NN'), (u'resulting', 'VBG'), (u'from', 'IN'), (u'the', 'DT')], [(u'form', 'NN'), (u'of', 'IN'), (u'metal', 'NN'), (u'resulting', 'VBG'), (u'from', 'IN'), (u'the', 'DT'), (u'swaging', 'NN')])]
    for PASFFW in PASFFWList:
        print get_final_pattern(PASFFW)
    
def test_getChunkPrefix():
    size=5
    attribute_value_tokens=[(u'age', 'NN'), (u'based', 'VBN'), (u'on', 'IN'), (u'skeletal', 'JJ'), (u'measurements', 'NNS'), (u'relative', 'VBP'), (u'to', 'TO'), (u'chronological', 'JJ'), (u'skeletal', 'NN'), (u'development', 'NN')]
    sentTokens=[(u'skeletal', 'JJ'), (u'age', 'NN'), (u'is', 'VBZ'), (u'the', 'DT'), (u'age', 'NN'), (u'based', 'VBN'), (u'on', 'IN'), (u'skeletal', 'JJ'), (u'measurements', 'NNS'), (u'relative', 'VBP'), (u'to', 'TO'), (u'chronological', 'JJ'), (u'skeletal', 'NN'), (u'development', 'NN')]
#     attribute_value_tokens=[(u'phagocytic', 'JJ'), (u'cell', 'NN'), (u'of', 'IN'), (u'the', 'DT'), (u'reticuloendothelial', 'JJ'), (u'system', 'NN'), (u'including', 'VBG'), (u'specialized', 'JJ'), (u'Kupffer\u9225\u6a9a', 'NNP'), (u'cells', 'NNS'), (u'in', 'IN'), (u'the', 'DT'), (u'liver', 'NN'), (u'and', 'CC'), (u'spleen', 'NN'), (u',', ','), (u'and', 'CC'), (u'histiocytes', 'NNS'), (u'in', 'IN'), (u'loose', 'JJ'), (u'connective', 'JJ'), (u'tissue', 'NN')]
#     sentTokens=[(u'macrophage', 'NN'), (u'is', 'VBZ'), (u'any', 'DT'), (u'phagocytic', 'JJ'), (u'cell', 'NN'), (u'of', 'IN'), (u'the', 'DT'), (u'reticuloendothelial', 'JJ'), (u'system', 'NN'), (u'including', 'VBG'), (u'specialized', 'JJ'), (u'Kupffer\u9225\u6a9a', 'NNP'), (u'cells', 'NNS'), (u'in', 'IN'), (u'the', 'DT'), (u'liver', 'NN'), (u'and', 'CC'), (u'spleen', 'NN'), (u',', ','), (u'and', 'CC'), (u'histiocytes', 'NNS'), (u'in', 'IN'), (u'loose', 'JJ'), (u'connective', 'JJ'), (u'tissue', 'NN')]
    for x in getChunkPrefix(size,attribute_value_tokens,sentTokens):
        print x

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
#     test_getChunkPrefix()
    end = datetime.datetime.now()
    logger.info(end)
    print end
    logger.info("cost time: "+str((end - start).microseconds))
    print str((end - start).seconds)+' s'