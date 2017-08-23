#coding=utf-8
'''
Created on 2017��7��4��

@author: FeiFei
'''
from kg.books.pattern_auto.KMP_match import KMP_match, get_match_pos_token
from _collections import defaultdict
import codecs
from kg.books.pattern_auto.record import logger


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
        start=KMP_match(rule+'$', fix_tokens)
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

