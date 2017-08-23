#coding=utf-8
'''
Created on 2017年1月9日

@author: feifei
'''
import json
import os
from nltk.parse import stanford
import nltk
from nltk.tree import Tree
import re
import codecs
from nltk.tag.stanford import StanfordPOSTagger

def extract_all_attributions(data):
#     data=json.load(fp, encoding, cls, object_hook, parse_float, parse_int, parse_constant, object_pairs_hook)
    attributions=[]
    cnt=0
    for item in data:
       concept,pronunciation,pos2definition=extract_item_properties(item)
       for pos2def in pos2definition:
           definition=pos2def["definition"]
#            print definition
           attribution=extract_attribution(definition)
           if len(attribution)!=0:
               print definition
               cnt+=1
               print attribution
           attributions.extend(attribution)
    return list(set(attributions))
 
def load_json_data(path):
    return json.load(open(path,"r"), encoding="utf-8") 

   
def extract_item_properties(item):
    return item["concept"],item["pronunciation"],item["pos2definition"]

def load_stanford_parser():
    os.environ['STANFORD_PARSER'] = 'F:/eclipse_doctor/KnowledgeGraph/stanford-parser/stanford-parser.jar'
    os.environ['STANFORD_MODELS'] = 'F:/eclipse_doctor/KnowledgeGraph/stanford-parser/stanford-parser-3.7.0-models.jar'
    java_path = "C:/ProgramData/Oracle/Java/javapath"
    os.environ['JAVAHOME'] = java_path
    parser = stanford.StanfordParser(model_path="F:/eclipse_doctor/KnowledgeGraph/stanford-parser/englishPCFG.ser.gz")
#     parser = stanford.StanfordDependencyParser(model_path="F:/eclipse_doctor/KnowledgeGraph/stanford-parser/englishPCFG.ser.gz")
    return parser

def load_stanford_tagger():
#     os.environ['STANFORD_TAGGER'] = 'F:/eclipse_doctor/KnowledgeGraph/stanford-pos/stanford-postagger-3.7.0.jar'
#     os.environ['STANFORD_MODELS'] = 'F:/eclipse_doctor/KnowledgeGraph/stanford-pos/english-bidirectional-distsim.tagger'
    java_path = "C:/ProgramData/Oracle/Java/javapath"
    os.environ['JAVAHOME'] = java_path
    return StanfordPOSTagger('F:/eclipse_doctor/KnowledgeGraph/stanford-pos/english-bidirectional-distsim.tagger','F:/eclipse_doctor/KnowledgeGraph/stanford-pos/english-bidirectional-distsim.tagger')

def stanford_parser(dep_parser,sub_definition):

    Tree=list(dep_parser.raw_parse(sub_definition))[0]
    print Tree
    Tree.draw()
    
#     tree_list=[parse.tree() for parse in dep_parser.raw_parse(sub_definition)]
    
#     print tree_list
#     print tree_list[0].draw()
#     print tree_list[-1][-1]
#     print tree_list[0][0][0]
#     print tree_list[0][0][0][0]
#     find_endpoint(tree_list)
#     print list(parser.raw_parse(line))[0]
#     print list(parser.raw_parse(line))[0][0][0]
#     print type(list(parser.raw_parse(line))[0][0][0])

def cut_definition(definition):
    pattern=r';|\. '
    cut_pos=find_pos(definition, pattern)
    if len(cut_pos)==0:
        return []
    cut_definitions=[]
    cut_definitions_no_braket=[]
    for i in range(len(cut_pos)-1):
        cut_definitions.append(definition[cut_pos[i]+1:cut_pos[i+1]])
    cut_definitions.append(definition[cut_pos[-1]+1:])
    for cut_definition in cut_definitions:
        result,num=re.subn(r'\([\s\S]*?\)','',cut_definition)
        cut_definitions_no_braket.append(result)
    return cut_definitions_no_braket

    
def find_tag_pos(str,sub_strs,cnt,prior_pos,tag_pos):
    if cnt>len(sub_strs)-1:
        return
    pos=str.find(sub_strs[cnt],prior_pos+2)
    tag_pos.append(pos)
    prior_pos=pos
    cnt+=1
    find_tag_pos(str,sub_strs,cnt,prior_pos,tag_pos)
    
def find_pos(line, pattern_tag):
#     pattern_tag=r',[\s]+?n(?=[\. /,])|,[\s]+?v(?=[ ])|,[\s]+?adj(?=[ /])|,[\s]+?adv(?=[ ])'
    if re.search(pattern_tag, line)==None:
        return []
    sub_strs=re.findall(pattern_tag, line)
    tag_pos=[]
    cnt=0
    prior_pos=line.find(sub_strs[cnt])
    cnt+=1
    tag_pos.append(prior_pos)
    find_tag_pos(line,sub_strs,cnt,prior_pos,tag_pos)
    return tag_pos
    
def find_endpoint(Tree):
    first_node=[]
    last_node=[]
    extract_first_node(Tree,first_node)
    extract_last_node(Tree,last_node)
    print first_node,last_node
    return first_node,last_node

def extract_first_node(Tree,first_node):
    if isinstance(Tree,nltk.tree.Tree)==False:
        first_node.append(Tree)
#         first_node=Tree
        return
    else:
        Tree=Tree[0]
        extract_first_node(Tree,first_node)
        
  
def extract_last_node(Tree,last_node):
    if isinstance(Tree,nltk.tree.Tree)==False:
        last_node.append(Tree)
#         last_node=Tree
        return
    else:
        Tree=Tree[-1]
        extract_last_node(Tree,last_node)
     
def extract_attribution(definition):
    sub_definitions=cut_definition(definition)
    attribution2value={}
    attibution=[]
    if len(sub_definitions)==0:
        return []
    for sub_definition in sub_definitions:
        pos=sub_definition.find(":")
        if pos!=-1:
            result=sub_definition.split(":")
#             attribution2value[result[0]]=result[1]
            attibution.append(result[0])
#         else:
    return  attibution     
        

def test():
#     path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
#     path_book = path_project+os.sep+"input"+os.sep+"items.json"
#     extract_json(path_book)
    line="referring to either of two chemical compounds"
    line="the sum of chemical changes involved in the function of nutrition"
    line="a restoration that reproduces the entire surface anatomy of the clinical crown and fits over a prepared tooth stump."
    line="a tooth, root, or implant used for support and retention of a fixed or removable prosthesis."
    line="an implant placed in the anterior part of an edentulous mandible and designed to supply abutments in the two canine regions."
    line="Acute or chronic localized inflammation, probably with a collection of pus, associated with tissue destruction and, frequently, swelling; usually secondary to infection."
#     line="drug class: mixed-acting sympathomimetic"
#     line="mixed-acting sympathomimetic"
#     line="Antonym"
    print line
    parser=load_stanford_parser()
    stanford_parser(parser,line)

def extract_prosthodontics(data_dental,path_prosthodontic):
    prosthodontics=load_prosthodontic(path_prosthodontic)
    prosthodontic_items=[]
    cnt=0
    cnt_see=0
    for item in data_dental:
        concept,pronunciation,pos2definition=extract_item_properties(item)
        for prosthodontic in prosthodontics:
#             print concept,";",prosthodontic
            if is_similar(concept,prosthodontic):
                print concept,";",prosthodontic
                prosthodontic_items.append(item)
                for pos2def in pos2definition:
                    definition=pos2def["definition"] 
                    if  definition.strip().startswith("See") or definition.strip().startswith("see"):
                        cnt_see+=1
                cnt+=1
                break
    print "count: ",cnt,cnt_see
    return  prosthodontic_items  

def load_prosthodontic(path_prosthodontic):
    return list(set(open(path_prosthodontic,"r").readlines()))

def is_similar(str1,str2):
    reslut_str1=re.split("[ ,]", str1.strip())
    reslut_str2=re.split(" ", str2.strip())
    new_reslut_str1=remove_empty_element(reslut_str1)
    new_reslut_str2=remove_empty_element(reslut_str2)
    if len(new_reslut_str1)==1 and len(new_reslut_str2)==1 and new_reslut_str1[0]==new_reslut_str2[0]:
        return True
    if len(new_reslut_str1)>1 and len(set(new_reslut_str1) & set(new_reslut_str2))/len(set(new_reslut_str1) | set(new_reslut_str2))>0.6:
        return True
#     if len(new_reslut_str1)>1 and len(new_reslut_str2)==1 and new_reslut_str1[0]==new_reslut_str2[0]:
#         return True
    return False

def remove_empty_element(list_): 
    new_list=[]
    for i in range(len(list_)):
        if len(list_[i])!=0:
            new_list.append(list_[i])
    return new_list
            
def main():
    path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
    path_book = path_project+os.sep+"input"+os.sep+"items.json"
    path_prosthodontic = path_project+os.sep+"input"+os.sep+"prosthodontics_filter_single.txt"
    path_out = path_project+os.sep+"output"+os.sep+"prosthodontic_items.json"
    data=load_json_data(path_book)
    
#     lines=extract_all_attributions(data)
#     with open(path_out,"w") as f:
#         for line in lines:
#             f.write(line.encode('utf-8')+"\n")
    prosthodontic_items=extract_prosthodontics(data,path_prosthodontic)
    json.dump(prosthodontic_items, codecs.open(path_out, 'w','utf-8'),ensure_ascii=False,indent=2)
#     json.dump(data[:10], codecs.open(path_out, 'w','utf-8'),ensure_ascii=False,indent=2)
    
def test1():
    str1="abrasion, dentifrice, "
    str2="oral hygiene"
    print is_similar(str1, str2)
if __name__=="__main__":
#     main()
#     test()
#     test1()
    sent1='May include medications, illicit drugs, legal substances with potential mood-altering effects (such as alcohol or tobacco), or substances whose primary use may not be for human consumption (such as inhalants).'
    sent2='This is a desk'
    sent3='a metallic oxide that includes alpha single crystal (an inert, biocompatible strong ceramic material used in the fabrication of some endosseous implants) and polycrystal (a constituent of dental porcelain that increases viscosity and strength).'
    tagger=load_stanford_tagger()
    print tagger.tag(sent1.split())
    print tagger.tag(sent2.split())
    print tagger.tag(sent3.split())
    
    
    