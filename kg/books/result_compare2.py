#coding=utf-8
'''
Created on 2017��2��20��

@author: feifei
'''
import os
import Levenshtein
import codecs
from kg.util.file import load_json
from kg.books.analysis_items import extract_item_properties
import datetime
from kg.kg.books.previous_version.regular_verify7port IE, IE_auto_pattern

def attribute_compare(attributes_munual,attributes_auto):
    same_attribute,key_similarity=attribute_key_similarity(attributes_auto.keys(),attributes_munual.keys())
    if len(same_attribute)==0:
        return 0.0,{}
    attribute2value_similarity={}
    for attribute in same_attribute:
        value_similarity=Levenshtein.ratio(attributes_auto[attribute].replace(' ',''),attributes_munual[attribute].replace(' ',''))
#         print 'attribute',attribute
        attribute2value_similarity[attribute]=value_similarity 
    return key_similarity,attribute2value_similarity


def attribute_key_similarity(list1,list2):
    same_element=list(set(list1) & set(list2))
    return same_element,float(len(same_element))/len(list2)

def attribute_different(list1,list2):
    same_element=list(set(list1) & set(list2))
    return [x for x in list1 if x not in same_element],[x for x in list2 if x not in same_element]

def compare_all_different(data_manual,data_auto):
    path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
    path_diff=path_project+os.sep+"output"+os.sep+"attribute_diff.txt"
    fp_diff=codecs.open(path_diff,'w','utf-8')
    for i in range(len(data_manual)):
        concept_manual,pronunciation_manual,pos2definition_manual=extract_item_properties(data_manual[i])
        concept_auto,pronunciation_auto,pos2definition_auto=extract_item_properties(data_auto[i])
        for j in range(len(pos2definition_manual)):
            attributes_manual=pos2definition_manual[j]["attributes"]
            attributes_auto=pos2definition_auto[j]["attributes"]
            manual_diff,auto_diff=attribute_different(attributes_manual,attributes_auto)
            if len(manual_diff)!=0 or len(auto_diff)!=0:
                write_error((i,j),data_manual,data_auto,fp_diff)
            
            
def compare_all(data_manual,data_auto):
    def2result={}
    for i in range(len(data_manual)):
        concept_manual,pronunciation_manual,pos2definition_manual=extract_item_properties(data_manual[i])
        concept_auto,pronunciation_auto,pos2definition_auto=extract_item_properties(data_auto[i])
        for j in range(len(pos2definition_manual)):
            attributes_manual=pos2definition_manual[j]["attributes"]
            attributes_auto=pos2definition_auto[j]["attributes"]
            key_similarity,attribute2value_similarity=attribute_compare(attributes_manual,attributes_auto)
            #locate the position item and definition
            position=(i,j)
            def2result[position]=(key_similarity,attribute2value_similarity)
    return def2result

def write_error(position,data_manual,data_auto,fp):
    data_manual_attributes=''
    data_auto_attributes=''
     
    data_manual_attributes_dict=data_manual[position[0]]["pos2definition"][position[1]]['attributes']
    sorted_data_manual_attributes_dict=sorted(data_manual_attributes_dict.iteritems(),key=lambda asd:asd[0],reverse=False)
    for attribute_item in sorted_data_manual_attributes_dict:
        data_manual_attributes+='%s: %s\n' % (attribute_item[0],attribute_item[1])
       
    data_auto_attributes_dict=data_auto[position[0]]["pos2definition"][position[1]]['attributes']
    sorted_data_auto_attributes_dict=sorted(data_auto_attributes_dict.iteritems(),key=lambda asd:asd[0],reverse=False)
    for attribute_item in sorted_data_auto_attributes_dict:
        data_auto_attributes+='%s: %s\n' % (attribute_item[0],attribute_item[1])
                 
    definition=data_manual[position[0]]["pos2definition"][position[1]]['definition']
    
    fp.write('definition: \n%s'%definition)
    fp.write("\nManual: \n")
    fp.write(data_manual_attributes)
    fp.write("Auto: \n")
    fp.write(data_auto_attributes)
    fp.write("\n\n")
    
def count_result(def2result,data_manual,data_auto):
#     正确率 = 提取出的正确信息条数 /  提取出的信息条数     
#     召回率 = 提取出的正确信息条数 /  样本中的信息条数
    #correct attribute number of automatic extraction
    cnt_attribute_correct_auto=0
    #attribute number of automatic extraction
    cnt_attribute_auto=0
    #attribute number of manual extraction
    cnt_attribute_manual=0
    #correct attribute value number of automatic extraction
    cnt_attribute_value_correct_auto=0
    #attribute value number of automatic extraction
    cnt_attribute_value_auto=0
    #attribute value number of manual extraction
    cnt_attribute_value_manual=0
    #similar attribute value number of automatic extraction
    cnt_attribute_value_similar_auto=0
    
    path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
    path_high=path_project+os.sep+"output"+os.sep+"precision_high.txt"
    path_low=path_project+os.sep+"output"+os.sep+"precision_low.txt"
    path_key_error=path_project+os.sep+"output"+os.sep+"key_error.txt"
    fp_high=codecs.open(path_high,'w','utf-8')
    fp_low=codecs.open(path_low,'w','utf-8')
    fp_key_error=codecs.open(path_key_error,'w','utf-8')
     
    for position,result in def2result.iteritems():
#         print result
        if result[0]==0.0:
            write_error(position,data_manual,data_auto,fp_key_error)
        for attribute,value_similarity in result[1].iteritems():
            cnt_attribute_correct_auto+=1
            if value_similarity==1:
                cnt_attribute_value_similar_auto+=1
                cnt_attribute_value_correct_auto+=1
            elif value_similarity>=0.9 and value_similarity<1.0:
                cnt_attribute_value_similar_auto+=1
                write_error(position,data_manual,data_auto,fp_high)
            else:
                write_error(position,data_manual,data_auto,fp_low)
                
    for item in data_manual:
        for pos2def in item["pos2definition"]:
            attributes2value=pos2def["attributes"]
            cnt_attribute_manual+=len(attributes2value)
            cnt_attribute_value_manual+=len(attributes2value)

    for item in data_auto:
        for pos2def in item["pos2definition"]:
            attributes2value=pos2def["attributes"]
            cnt_attribute_auto+=len(attributes2value)
            cnt_attribute_value_auto+=len(attributes2value)
            
    print cnt_attribute_correct_auto, cnt_attribute_auto,cnt_attribute_manual,cnt_attribute_value_correct_auto,\
    cnt_attribute_value_auto,cnt_attribute_value_manual,cnt_attribute_value_similar_auto     
    print "cnt_attribute_correct_auto: %d\n cnt_attribute_auto: %d\n cnt_attribute_manual: %d\n \
    cnt_attribute_value_correct_auto: %d\n cnt_attribute_value_auto: %d\n \
    cnt_attribute_value_manual: %d\n cnt_attribute_value_similar_auto: %d\n"\
    %(cnt_attribute_correct_auto, cnt_attribute_auto,cnt_attribute_manual,cnt_attribute_value_correct_auto,\
      cnt_attribute_value_auto,cnt_attribute_value_manual,cnt_attribute_value_similar_auto)     

    attribute_correct_ratio=float(cnt_attribute_correct_auto)/cnt_attribute_auto
    attribute_recall_ratio=float(cnt_attribute_correct_auto)/cnt_attribute_manual
    
    attribute_value_correct_ratio=float(cnt_attribute_value_correct_auto)/cnt_attribute_value_auto
    attribute_value_recall_ratio=float(cnt_attribute_value_correct_auto)/cnt_attribute_value_manual
    
    attribute_value_similarity_ratio=float(cnt_attribute_value_similar_auto)/cnt_attribute_value_auto
    attribute_value_similarity_recall_ratio=float(cnt_attribute_value_similar_auto)/cnt_attribute_value_manual
    
    print "attribute_correct_ratio: %f" %attribute_correct_ratio
    print "attribute_recall_ratio: %f" %attribute_recall_ratio
    print "attribute_value_correct_ratio: %f" %attribute_value_correct_ratio
    print "attribute_value_recall_ratio: %f" %attribute_value_recall_ratio
    print "attribute_value_similarity_ratio: %f" %attribute_value_similarity_ratio
    print "attribute_value_similarity_recall_ratio: %f" %attribute_value_similarity_recall_ratio
    
     
def main():
#     IE()
    IE_auto_pattern()
    path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
    path_data_manual= path_project+os.sep+"input"+os.sep+"items_tagged_modified.json"
    path_data_auto= path_project+os.sep+"output"+os.sep+"items_tagged_auto.json"
    data_manual=load_json(path_data_manual)
    data_auto=load_json(path_data_auto)
    def2result=compare_all(data_manual,data_auto)
    count_result(def2result,data_manual,data_auto)
    compare_all_different(data_manual,data_auto)
    
if __name__ == '__main__':
    start = datetime.datetime.now()
    print start
#     logger.info(start)
    main()
#     test()
    end = datetime.datetime.now()
    print end
#     logger.info(end)
    
#     logger.info("cost time"+str((end - start).seconds))
    print "cost time seconds: %s, microseconds: %s"%(str((end - start).seconds),str((end - start).microseconds))
            
            
            