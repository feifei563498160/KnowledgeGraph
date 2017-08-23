#coding=utf-8
'''
Created on 2017��2��10��

@author: feifei
'''
import os
import json
import datetime
import codecs
import re
import nltk
import multiprocessing
import threading
import chardet
import traceback

from multiprocessing import Pool

from kg.util.string import cut_list
from kg.books.extractor.recorder import logger
from kg.books.extractor.choice_final_patterns import choice_final_pattern
from kg.books.extractor.get_attribute2value import get_match_result
from kg.books.extractor.find_can_patterns import find_candidate_pattern
from nltk.tag.stanford import StanfordPOSTagger
from kg.books.extractor.load_data import tagfromstring, data_tagged_modified,\
    pattern2attrubute, path_data_tagged_modified_extract, data_modified


tag_time_all=0
find_candidate_time=0

def process_definition(pattern2attrubute,def_tagged):
    attributes2value={}
    definition=' '.join([x[0] for x in def_tagged])
    logger.info('definition: %s'% definition)
    if definition.strip().startswith('See') or definition.strip().startswith('see'):
        return
    start=datetime.datetime.now()
#     text = nltk.word_tokenize(definition)
#     def_pos=nltk.pos_tag(text)
    logger.info(def_tagged)
    end=datetime.datetime.now()
    global tag_time_all
    tag_time_all+=(end-start).microseconds
    logger.info('tagging time:%d ' % ((end-start).microseconds))
#     logger.info(def_pos)
    seg_point=[('.','.')]
    sents_pos_period=cut_list(def_tagged, seg_point)
    sents_pos=[]
    for sent_pos_period in sents_pos_period:
        if sent_pos_period[0][0]=='See' and sent_pos_period[1][0]=='also':
            sents_pos.append(sent_pos_period)
        else:
            sents_pos.extend(cut_list(sent_pos_period,[(';',':')]))
            
    start=datetime.datetime.now()
    end=datetime.datetime.now()
    time_find_candidate_pattern=(end-start).microseconds
    time_choice_final_pattern=(end-start).microseconds
    time_get_match_result=(end-start).microseconds
    for sent_pos in sents_pos:
        logger.info("sent_pos: "+str(sent_pos))
        start=datetime.datetime.now()
        candidate_patterns=find_candidate_pattern(pattern2attrubute.keys(),sent_pos)
        end=datetime.datetime.now()
        time_find_candidate_pattern+=(end-start).microseconds
        logger.info('find candidate pattern time:　'+str((end-start).microseconds))
        logger.info("candidate_patterns: "+str(candidate_patterns))
        
        if len(candidate_patterns)==0:
            continue
        start=datetime.datetime.now()
        choiced_patterns=choice_final_pattern(candidate_patterns,sent_pos)
        end=datetime.datetime.now()
        time_choice_final_pattern+=(end-start).microseconds
        logger.info('choice final pattern　time:　'+str((end-start).microseconds))
        logger.info("choiced_patterns: "+str(choiced_patterns))
        
        start=datetime.datetime.now()
        attributes2value_part=get_match_result(choiced_patterns,pattern2attrubute, sent_pos)
        for attribute, value in attributes2value_part.iteritems():
            if attribute in attributes2value.keys():
                part1=attributes2value[attribute]
                attributes2value[attribute]=part1+'; '+value
            else:
                attributes2value[attribute]=value
        end=datetime.datetime.now()
        time_get_match_result+=(end-start).microseconds
        logger.info('get match result time:　'+str((end-start).microseconds))
        logger.info("attributes2value:　"+str(attributes2value))
    global find_candidate_time
    find_candidate_time+=time_find_candidate_pattern
    logger.info('time_find_candidate_pattern: '+str(time_find_candidate_pattern))
    logger.info('time_choice_final_pattern: '+str(time_choice_final_pattern))
    logger.info('time_get_match_result: '+str(time_get_match_result))
    logger.info("whole attributes2value: "+str(attributes2value))
    return attributes2value

def extract_items_single_thread(data,pattern2attrubute):
    data_new=[]
    all_time=0
#     attributes=set([])
    for item in data:
        pos2definition=item["pos2definition"]
        for pos2def in pos2definition:
            def_tagged=tagfromstring(pos2def["def_tagged"])
#             definition=pos2def["definition"]
#             tagged_text=stanford_tagger.tag(definition.split())
#             definition_pure=re.sub(r'\([\s\S]*?\)', "", definition)
#             cnt+=1
            
            start=datetime.datetime.now()
#             for key in pos2def["attributes"]:
#                 attributes.add(key)
            attributes2value=process_definition(pattern2attrubute,def_tagged)
            end=datetime.datetime.now()
            all_time+=(end-start).seconds*1000+(end-start).microseconds
            logger.info('process_definition time: %ds: %dms ' % ((end-start).seconds,(end-start).microseconds))
            pos2def["attributes"]=attributes2value
        logger.info("\n\n")
        data_new.append(item)
#     for attribue in sorted(list(attributes)):
#         print attribue
    global tag_time_all
    logger.info("tag all time is: %d"%tag_time_all)
    global find_candidate_time
    logger.info("find candidate time is: %d"%find_candidate_time)
    logger.info("all time is: %d"%all_time)
    return data_new

def extract_single_item(data,i,new_data,pattern2attrubute,stanford_tagger):
    print i,'start'
    pos2definition=data[i]["pos2definition"]
    for pos2def in pos2definition:
        definition=pos2def["definition"]
        definition_pure=re.sub(r'\([\s\S]*?\)', "", definition)
        attributes2value=process_definition(definition_pure,pattern2attrubute,stanford_tagger)
        pos2def["attributes"]=attributes2value
    logger.info("\n\n")
    print i,' over'
    new_data.append(data[i])

def extractor_multi_thread(data,pattern2attrubute,stanford_tagger):
    p=Pool()
    multiprocessing.freeze_support() 
    cpus = multiprocessing.cpu_count()
    new_data=[]
    lock =threading.Lock() 
    j=1
    while(j):
        if j<len(data)/cpus:
            if lock.acquire():
                for i in range(cpus):
                    print 'thread: ',j*cpus+i
                    p.apply_async(extract_single_item,args=(data,j*cpus+i,new_data,pattern2attrubute,stanford_tagger,))
                 
                j+=1
                lock.release() 
        else:
            break
    p.close()
    p.join()
    return new_data

def IE():
#     path_data="data"+os.sep+"items_tagged_modified.json"
#     path_pattern="patterns.json"
#     path_data= path_project+os.sep+"input"+os.sep+"items.json"
#     path_data_output=path_project+os.sep+"output"+os.sep+"test_items.json"
#     path_tagged_output="items_tagged_auto.json"
#     pattern2attrubute=json.load(codecs.open(path_pattern, encoding='UTF-8'))
    logger.info("loaded all the patterns")
#     data=json.load(codecs.open(path_data, encoding='UTF-8'))
    logger.info("loaded all the data")
    data_new=extract_items_single_thread(data_tagged_modified,pattern2attrubute)
#     data_new=extractor_multi_thread(data,pattern2attrubute,stanford_tagger)
    logger.info("has extracted all the attributes")
    json.dump(data_new, codecs.open(path_data_tagged_modified_extract, 'w','utf-8'),ensure_ascii=False,indent=2)
    logger.info("output over")

def IE_auto_pattern():
    path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
    path_data= path_project+os.sep+"input"+os.sep+"items_tagged_modified.json"
    path_pattern= path_project+os.sep+"output"+os.sep+"Patterns_auto.json"
#     path_pattern= path_project+os.sep+"output"+os.sep+"pattern_auto_test.json"
#     path_pattern= path_project+os.sep+"input"+os.sep+"patterns_target.json"
#     path_pattern= path_project+os.sep+"input"+os.sep+"patterns_merge.json"

#     path_data= path_project+os.sep+"input"+os.sep+"items.json"
#     path_data_output=path_project+os.sep+"output"+os.sep+"test_items.json"
    path_tagged_output=path_project+os.sep+"output"+os.sep+"items_tagged_auto.json"
    pattern2attrubute=json.load(codecs.open(path_pattern, encoding='UTF-8'))
    logger.info("loaded all the patterns")
    data=json.load(codecs.open(path_data, encoding='UTF-8'))
    logger.info("loaded all the data")
    data_new=extract_items_single_thread(data,pattern2attrubute)
#     data_new=extractor_multi_thread(data,pattern2attrubute,stanford_tagger)
    logger.info("has extracted all the attributes")
    json.dump(data_new, codecs.open(path_tagged_output, 'w','utf-8'),ensure_ascii=False,indent=2)
    logger.info("output over")

def IE_multi_thread():
    path_data="data"+os.sep+"items_tagged_modified.json"
    path_pattern="patterns.json"
#     path_data= path_project+os.sep+"input"+os.sep+"items.json"
#     path_data_output=path_project+os.sep+"output"+os.sep+"test_items.json"
    path_tagged_output="items_tagged_auto.json"
    pattern2attrubute=json.load(codecs.open(path_pattern, encoding='UTF-8'))
    logger.info("loaded all the patterns")
    data=json.load(codecs.open(path_data, encoding='UTF-8'))
    logger.info("loaded all the data")
    data_new=extractor_multi_thread(data,pattern2attrubute)
#     data_new=extractor_multi_thread(data,pattern2attrubute,stanford_tagger)
    logger.info("has extracted all the attributes")
    json.dump(data_new, codecs.open(path_tagged_output, 'w','utf-8'),ensure_ascii=False,indent=2)
    logger.info("output over")

def tagged_def():
    java_path = "C:/ProgramData/Oracle/Java/javapath"
    os.environ['JAVAHOME'] = java_path
    tagger=StanfordPOSTagger('F:/eclipse_doctor/KnowledgeGraph/stanford-pos/english-bidirectional-distsim.tagger','F:/eclipse_doctor/KnowledgeGraph/stanford-pos/english-bidirectional-distsim.tagger')
    
    
    path_data="data"+os.sep+"items_tagged_modified.json"
    data=json.load(codecs.open(path_data, encoding='UTF-8'))
    for item in data:
        pos2definition=item["pos2definition"]
        for pos2def in pos2definition:
            definition=pos2def["definition"]
#             print chardet.detect(definition)
            print definition.encode('gbk')
            definition_pure=re.sub(r'\([\s\S]*?\)', "", definition)
            tokens=nltk.word_tokenize(definition_pure)
#             print tokens
            for token in tokens:
                print chardet.detect(token)
            tagged_tokens=tagger.tag(definition_pure.encode('utf-8').split())
            pos2def['tagged_def']=tagged_tokens
    
    path_tagged_output="items_tagged_auto.json"
    json.dump(data, codecs.open(path_tagged_output, 'w','utf-8'),ensure_ascii=False,indent=2)   

def pre_process():
    cnt_exp=0
    for item in data_tagged_modified:
#     for item in data_modified_test:
#     for item in data_modified:
        pos2definition=item["pos2definition"]
        for pos2def in pos2definition:
            try:
                definition=pos2def["definition"]
                definition_pure=re.sub(r'\([\s\S]*?\)', "", definition)
                tokens=nltk.word_tokenize(definition_pure.encode('utf-8'))
                for token in tokens:
#                     try:
                        if chardet.detect(token)['encoding']!='ascii':
    #                         print token,chardet.detect(token)['encoding'],token.decode('utf-8').encode('gbk')
                            logger.info("%s\t%s\t%s"%(token,chardet.detect(token)['encoding'],token.decode("utf-8").encode("gbk")))
#                     except Exception:
#                         traceback.print_exc()
#                         print token
            except Exception:
                cnt_exp+=1
                traceback.print_exc()
#                 print traceback.format_exc()
                print definition
#                 print definition.encode('gbk')
#                 
# #             print definition_pure.encode('gbk')
#             try:
#                 pos2def["definition"]=pos2def["definition"].decode("utf-8").encode("gbk")
#             except Exception:
#                 cnt_exp+=1
#                 traceback.print_exc()
#                 print pos2def["definition"]
    print  cnt_exp       
    path_tagged_output="items_tagged_modified_pre.json"    
    json.dump(data_tagged_modified, codecs.open(path_tagged_output, 'w','utf-8'),ensure_ascii=False,indent=2)   
       
if __name__ == '__main__':
    start = datetime.datetime.now()
    logger.info(start)
    print start
#     IE_auto_pattern()
#     tagged_def()
#     IE()
    pre_process()
    end = datetime.datetime.now()
    logger.info(end)
    print end
    print (end - start).seconds,(end - start).microseconds
    logger.info("cost time: "+str((end - start).seconds))
    
    