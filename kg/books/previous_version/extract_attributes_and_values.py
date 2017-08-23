#coding=utf-8
'''
Created on 2017年1月19日

@author: feifei
'''
import os
import json
from kg.books.analysis_items import load_json_data, extract_item_properties
import codecs

    
def upload(data):
    from py2neo import Node, Relationship
    from py2neo import Graph
    graph=Graph("http://localhost:7474", username="neo4j", password="19920201")
    graph.delete_all()
    nodes=[]
    for item in data:
        concept,pronunciation,pos2definition=extract_item_properties(item)
        node_tmp=Node("Prosthodontics",name=concept)
        node_tmp.properties["pronunciation"]=pronunciation
        cnt=1
        for pos2def in pos2definition:
            node_tmp.properties["pos "+str(cnt)]=pos2def["pos"]
#             node_tmp.properties["definition "+str(cnt)]=pos2def["definition"]
            for attribute,value in pos2def["attributes"].iteritems():
                node_tmp["def "+str(cnt)+" : "+attribute]=value
        graph.create(node_tmp)
        nodes.append(node_tmp)
    print "nodes create over , relation start to create"   
    
    for node1 in nodes:
        properties=node1.properties.keys()
        for property in properties:
            if property[8:]=="cross_reference":
                for node2 in nodes:
                    if node2.properties["name"]==node1[property]:
                        graph.create(Relationship(node1,"cross_reference",node2))
    print "graph create over"
    
def main():    
    path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
    path_posthodontic_items = path_project+os.sep+"input"+os.sep+"prosthodontic_items_tagged_attributes.json"
    path_attribute_and_value = path_project+os.sep+"output"+os.sep+"attribute_and_value.txt"
#     fp_out=codecs.open(path_attribute_and_value, 'w','utf-8')
    data=load_json_data(path_posthodontic_items)
    upload(data)
#     attributes_all={}
#     for item in data:
#         concept,pronunciation,pos2definition=extract_item_properties(item)
# #         print concept
#         for pos2def in pos2definition:
#             if len(pos2def["attributes"])==0:
#                 print concept
#             for attribute,value in pos2def["attributes"].iteritems():
# #                 if attributes_all.has_key(attribute):
# #                     print attribute
#                     attributes_all.setdefault(attribute,[]).append(concept+" : "+value)
# #                 else:
# #                     attributes_all.setdefault(attribute,[]).append(value)
#     attribute_tuple=sorted(attributes_all.iteritems(), key=lambda d:d[0], reverse = False)
#     for attribute_and_value in attribute_tuple:
#         fp_out.write(attribute_and_value[0]+" : \n")
#         for value in attribute_and_value[1]:
#             fp_out.write("\t"+value+"\n")
#         fp_out.write("\n")
#         
if __name__=="__main__":
    main()