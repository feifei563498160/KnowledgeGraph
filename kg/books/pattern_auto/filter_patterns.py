#coding=utf-8
'''
Created on 2017��7��4��

@author: FeiFei
'''
from _collections import defaultdict
from kg.books.pattern_auto.record import logger

TOP=10  #TOP means get the top 1/10 pattern candidate

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

