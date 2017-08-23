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

def attribute_compare(attributes_munual,attributes_auto):
    same_attribute,similarity=attribute_key_similarity(attributes_auto.keys(),attributes_munual.keys())
    if len(same_attribute)==0:
        return 0,{}
    attribute2value_similarity={}
    for attribute in same_attribute:
        value_similarity=Levenshtein.ratio(attributes_auto[attribute],attributes_munual[attribute])
#         print 'attribute',attribute
        attribute2value_similarity[attribute]=value_similarity 
    return similarity,attribute2value_similarity


def attribute_key_similarity(list1,list2):
    cnt=0
    same_element=[]
    for element in list1:
        if element in list2:
            same_element.append(element)
            cnt+=1
    return same_element,float(cnt)/len(list2)

def compare_all(data_manual,data_auto):
    def2result={}
    for i in range(len(data_manual)):
        concept_manual,pronunciation_manual,pos2definition_manual=extract_item_properties(data_manual[i])
        concept_auto,pronunciation_auto,pos2definition_auto=extract_item_properties(data_auto[i])
#         print 'concept_manual',concept_manual,'concept_auto',concept_auto
        for j in range(len(pos2definition_manual)):
            attributes_manual=pos2definition_manual[j]["attributes"]
            attributes_auto=pos2definition_auto[j]["attributes"]
#             print 'attributes_manual',attributes_manual,'\nattributes_auto',attributes_auto
            similarity,attribute2value_similarity=attribute_compare(attributes_manual,attributes_auto)
#             print similarity,attribute2value_similarity
            def2result[pos2definition_manual[j]["definition"]]=(similarity,attribute2value_similarity)
    return def2result

def count_result(def2result,data_manual,data_auto):
    cnt_similarity=0
    cnt_correct=0
    cnt_high_precision=0
    cnt_low_precision=0
    cnt_middle_precision=0
    cnt_value=0
    path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
    path_high=path_project+os.sep+"output"+os.sep+"high_precision.txt"
    path_middle=path_project+os.sep+"output"+os.sep+"middle_precision.txt"
    path_low=path_project+os.sep+"output"+os.sep+"low_precision.txt"
    fp_high=codecs.open(path_high,'w','utf-8')
    fp_middle=codecs.open(path_middle,'w','utf-8')
    fp_low=codecs.open(path_low,'w','utf-8')
    cnt=0
    for result in def2result.values():
        if result[0]>0:
            cnt_similarity+=1
            for attribute,similarity in result[1].iteritems():
                if similarity>0.6:
                    cnt_high_precision+=1
                    cnt_value+=1
                    fp_high.write(data_manual[])
                    fp_high.write(data_auto[])
                    fp_high.write("\n\n")
                elif similarity<0.1:
                    cnt_low_precision+=1
                    cnt_value+=1
                    fp_middle.write(data_manual)
                    fp_middle.write(data_auto)
                    fp_middle.write("\n\n")
                else:
                    cnt_middle_precision+=1
                    cnt_value+=1
                    fp_low.write(data_manual)
                    fp_low.write(data_auto)
                    fp_low.write("\n\n")
        if result[0]==1:
            cnt_correct+=1
        
    no_reslut_ratio=float(len(def2result)-cnt_similarity)/len(def2result)
    correct_ratio=float(cnt_correct)/len(def2result)
    high_precision_ratio=float(cnt_high_precision)/cnt_value
    low_precision_ratio=float(cnt_low_precision)/cnt_value
    middle_precision_ratio=float(cnt_middle_precision)/cnt_value
    print no_reslut_ratio, correct_ratio,high_precision_ratio,low_precision_ratio,middle_precision_ratio
    return  no_reslut_ratio, correct_ratio,high_precision_ratio,low_precision_ratio,middle_precision_ratio

     
def main():
    path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
    path_data_manual= path_project+os.sep+"input"+os.sep+"tagged_items.json"
    path_data_auto= path_project+os.sep+"input"+os.sep+"items_tagged_auto.json"
    data_manual=load_json(path_data_manual)
    data_auto=load_json(path_data_auto)
    def2result=compare_all(data_manual,data_auto)
    count_result(def2result,data_manual,data_auto)
    
if __name__ == '__main__':
    main()
            
            
            