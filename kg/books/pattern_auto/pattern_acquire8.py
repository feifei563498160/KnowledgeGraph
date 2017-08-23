#coding=utf-8
'''
Created on 2017��4��10��

@author: FeiFei
'''
import os
from kg.util.file import load_json
import json
import datetime
from collections import Counter
from kg.books.pattern_auto.get_can_patterns import acquire_patterns
from kg.books.pattern_auto.filter_patterns import filterPatterns
from kg.books.pattern_auto.merge_patterns import merge_pattern_all,\
    sorted_by_attribute_pattern
import codecs
from kg.books.pattern_auto.record import logger

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
    path_data= "items_tagged_modified.json"
#     path_data= path_project+os.sep+"input"+os.sep+"items_tagged_modified_test.json"
    path_pattern= path_project+os.sep+"output"+os.sep+"Patterns_auto.json"
    path_pattern_sorted= path_project+os.sep+"output"+os.sep+"pattern_auto_sorted_by_attribute_pattern.json"
    path_pattern= "Patterns_auto.json"
    path_pattern_sorted= "pattern_auto_sorted_by_attribute_pattern.json"

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



if __name__=='__main__':
    start = datetime.datetime.now()
    logger.info(start)
    print start
    main()
#     test_get_final_tokens()
#     test_get_final_pattern()
#     test_getChunkPrefix()
    end = datetime.datetime.now()
    logger.info(end)
    print end
    logger.info("cost time: "+str((end - start).microseconds))
    print str((end - start).seconds)+' s'