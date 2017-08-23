#coding=utf-8
'''
Created on 2016年12月10日

@author: feifei
'''
import os
import collections
import json
import traceback
from kg.util import db
from kg.util import mylogger

path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
log_path=path_project+os.sep+"tmp"+os.sep+"log.yago"
log_yago=mylogger.log_file(log_path)

def get_yago_medical_relation(path):
    """
    read it from the manual filtered file
    """
    return open(path,"r").readlines()
def get_medical_seed(path):
    return open(path,"r").readlines()

def output2json(dic,path):
    dict=collections.OrderedDict(sorted(dic.iteritems(), key=lambda d:d[0]))
    json.dump(dict, open(path, 'w'),indent=2)


def get_relation2fact(relation_path,seed_path,pairs2num_path):
    conn=db.get_conn()
    cursor=conn.cursor()
     
    relations=get_yago_medical_relation(relation_path)
    seeds=get_medical_seed(seed_path)
    pairs2num={}
    for seed in seeds:
#     for relation in relations:
#         for seed in seeds:
            try:
                """extract the first level fact"""
                seed=seed.replace("'","''").strip()
#                 sql_po="select * from yagofacts where lower(object)=\'\"%s\"@eng\' and predicate=\'%s\';" % (seed.strip().lower(),relation.strip())
#                 sql_sp="select * from yagofacts where lower(subject)=\'<%s>\' and predicate=\'%s\';" % (seed.strip().lower(),relation.strip())
                sql_po="select * from yagofacts where lower(object)=\'\"%s\"@eng\'" % (seed.lower())
                sql_sp="select * from yagofacts where lower(subject)=\'<%s>\'" % (seed.lower())
     
                print sql_po
                cursor.execute(sql_po)
#                 pairs2num[relation+"\t"+seed.lower()]=len(cursor.fetchall())
                rows=cursor.fetchall()
                pairs2num[seed.lower()]=len(rows)
#                 print rows
#                 print "object po: "+relation+"\t"+seed.lower()+" have num: "+str(len(cursor.fetchall()))
                print "object po: "+seed.lower()+" have num: "+str(len(rows))

                print sql_sp
                cursor.execute(sql_sp)
#                 pairs2num[seed.lower()+"\t"+relation]=len(cursor.fetchall())
#                 print "subject sp: "+seed.lower()+"\t"+relation+" have num: "+str(len(cursor.fetchall()))
                rows=cursor.fetchall()
                pairs2num[seed.lower()]=len(rows)
                print "subject sp: "+seed.lower()+" have num: "+str(len(rows))
                sql_insert_po="insert into extract_facts3(id,subject,predicate,object,value) "+sql_po
                sql_insert_sp="insert into extract_facts3(id,subject,predicate,object,value) "+sql_sp
                print "insert into extract_facts3"
                cursor.execute(sql_insert_po)
                cursor.execute(sql_insert_sp)
            except Exception:
                log_yago.info(traceback.print_exc())
                log_yago.info(sql_po)
                log_yago.info(sql_sp+"\n\n")
                pass
                 
    conn.commit()
    cursor.close()
    conn.close()
    sum=0
    for value in pairs2num.values():
        sum+=value
    print "pairs: "+str(sum)
    output2json(pairs2num,pairs2num_path)
   
   


def delete_wrong_facts(relation_right,relation_candicate):
# def delete_wrong_facts(countries):   
    conn=db.get_conn()
    cursor=conn.cursor()
    for relation in relation_candicate:
        if relation not in relation_right:
            sql_delete="delete from extract_facts3 where predicate='%s';" % (relation.strip())
#             sql_ob_del="delete from extract_facts where lower(object)=\'\"%s\"@eng\'" % (seed.lower())
#             sql_sub_del="delete from extract_facts where lower(subject)=\'<%s>\'" % (seed.lower())
 
#             sql_delete=""
            print sql_delete
            cursor.execute(sql_delete)
            
#     for country in countries:
# #             sql_delete="delete from extract_facts where predicate='%s';" % (relation.strip())
#             sql_ob_del="delete from extract_facts where lower(object)=\'\"%s\"@eng\'" % (country.strip().lower())
#             sql_sub_del="delete from extract_facts where lower(subject)=\'<%s>\'" % (country.strip().lower())
# 
#             print sql_ob_del
#             cursor.execute(sql_ob_del)
#             print sql_sub_del
#             cursor.execute(sql_sub_del)
    conn.commit()
    cursor.close()
    conn.close()

def filter_concept(concept_path,reduce_path):   
    concepts=open(concept_path).readlines()
    reduces=open(reduce_path).readlines()
    lower_reduces=[]
    for reduce in reduces:
        lower_reduces.append(reduce.lower().strip())
    new_concepts=[]
    for concept in concepts:
        if concept.lower().strip() not in lower_reduces:
            new_concepts.append(concept)
    return new_concepts

def main():
    path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
    relation_path=path_project+os.sep+"input"+os.sep+"yago_relation_medical"
    seed_path=path_project+os.sep+"input"+os.sep+"concept_filter_level3.txt"
    pairs2num_path=path_project+os.sep+"output"+os.sep+"pairs2num.json"
    get_relation2fact(relation_path,seed_path,pairs2num_path)
    
def delete():
    path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
    relation_path=path_project+os.sep+"input"+os.sep+"yago_relation_medical"
#     countries_path=path_project+os.sep+"input"+os.sep+"country"
#     concepts_path=path_project+os.sep+"input"+os.sep+"concept_filter_level3.txt"
#     concept_filter_path=path_project+os.sep+"output"+os.sep+"concept_filter"
#     filter_concept(concepts_path,countries_path)
#     open(concept_filter_path,'w').writelines(filter_concept(concepts_path,countries_path))
    relation_candicate_path=path_project+os.sep+"input"+os.sep+"relation_candicate"
    relations=get_yago_medical_relation(relation_path)
#     countries=get_yago_medical_relation(countries_path)
    relation_candicate=get_yago_medical_relation(relation_candicate_path)
#     print relations
#     print relation_candicate
#     delete_wrong_facts(countries)
    delete_wrong_facts(relations,relation_candicate)

if __name__=="__main__":
#     main()
    delete()
    
    