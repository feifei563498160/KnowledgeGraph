#coding=utf-8
'''
Created on 2017��2��10��

@author: feifei
'''
import os
import json
import datetime
from nltk.tag.stanford import StanfordPOSTagger
from kg.util.file import load_json
from kg.util.string import divide_line
from kg.books.analysis_items import extract_item_properties
import codecs
import re

def load_patterns(path):
    return load_json(path)

def process_definition(definition,patterns,tagger):
    attributes2value={}
#     tagger=get_tagger()
    pattern_tag='\.'
    sents=divide_line(definition, pattern_tag)
    for sent in sents:
        print "sent: ", sent
        candidate_patterns=find_candidate_pattern(patterns,sent,tagger)
        print "candidate_patterns: ",candidate_patterns
        choiced_patterns=choice_final_pattern(candidate_patterns,sent)
        print "choiced_patterns: ",choiced_patterns
        attributes2value=get_match_result(choiced_patterns, sent)
        print "attributes2value:　", attributes2value
    return attributes2value

def judge_category(concept):
    pass

def find_candidate_pattern(patterns, sent,tagger):
    candidate_patterns=[]
    for pattern in patterns:
        if is_candidate_pattern(pattern, sent,tagger):
            candidate_patterns.append(pattern)
    return candidate_patterns

def is_candidate_pattern(pattern, sent,tagger):
    sent_pos=tagger.tag(sent)
    real_pattern=""
    if '-0' in pattern:
        real_pattern="^"+pattern[:pattern.find('-0')]
    elif '-1' in pattern: 
        real_pattern=pattern[:pattern.find('-1')]
    else:
        real_pattern=pattern  
    return is_match(real_pattern,sent_pos)

def is_match(real_pattern,sent_pos):
    words_pattern=real_pattern.split(" ")
    match,cnt=is_pattern_match(words_pattern,sent_pos)
    if match:
        return True
    return False

def is_pattern_match(words_pattern,sent_pos):
    cnt=0
    for word_tag in sent_pos:
        flag=1
        for i in range(len(words_pattern)):
            if "|" in words_pattern[i]:
                words_candidate=words_pattern[i].split("|")
                if is_word_match(words_candidate,word_tag)!=True:
                    flag=0
                    break
            else:
                if words_pattern[i]!=word_tag[0]:
                    flag=0
                    break
        if flag==1:
            return True,cnt
        cnt+=1
    return False,cnt
              
def is_word_match(words_candidate,word_tag):
    for word in words_candidate:
        if word==word_tag[0] or word==word_tag[1]:
            return True
    return False

def is_contain_POS_tag(pattern,tags):
    for tag in tags:
        if tag in pattern:
            return True
    return False

def get_real_pattern(pattern):
    real_pattern=""
    if '-0' in pattern:
        real_pattern="^"+pattern[:pattern.find('-0')]
    elif '-1' in pattern:
        real_pattern=pattern[:pattern.find('-1')]
    else:
        real_pattern=pattern
    return real_pattern
     
def choice_final_pattern(patterns,sent_pos):
    pos2patterns={}
    for pattern in patterns:
        real_pattern=get_real_pattern(pattern)
        words_pattern=real_pattern.split(" ")
        match,pos=is_pattern_match(words_pattern,sent_pos)
        if pos in pos2patterns.keys():
            pos2patterns[pos].append(pattern)
        else:
            pos2patterns[pos]=[].append(pattern)
    
    sorted_pattern=sorted(pos2patterns.iteritems(),key=lambda d:d[0], reverse=False)
    patterns_final=[]
    for pos2pattern in sorted_pattern:
        if len(pos2pattern[1])>1:
            patterns_final.append(get_prior_pattern(pos2pattern[1]))
        else:
            patterns_final.append(pos2pattern[1])
    return patterns_final

def get_prior_pattern(patterns):
    #get the prior pattern, when multiple pattern occur in a same position, if the pattern have a bigger match range
    lens=[]
    for pattern in patterns:
        real_pattern=get_real_pattern(pattern)
        words_pattern=real_pattern.split(" ")
        lens.append(len(words_pattern))
    return patterns[lens.index(min(lens))]


def get_match_result(patterns,pattern2attributes,sent):
    attributes2value={}
    if ';' in sent:
        semi_sents=divide_line(sent, ';')
        for semi_sent in semi_sents:
            for i in range(len(patterns),-1,-1):
                value_pos=get_value_pos(patterns,sent)
                attributes2value[pattern2attributes[patterns[i]]]=sent[value_pos[len(patterns)-i-1][0]:value_pos[len(patterns)-i-1][1]]
    else:  
        for i in range(len(patterns),-1,-1):
            value_pos=get_value_pos(patterns,sent)
            attributes2value[pattern2attributes[patterns[i]]]=sent[value_pos[len(patterns)-i-1][0]:value_pos[len(patterns)-i-1][1]]
    return attributes2value  
      

def get_value_pos(patterns,sent):
    pos=[]
    if len(patterns)==1:
        start=sent.find(re.findall(patterns[0], sent)[0])+len(patterns[0])
        end=-1
        pos.append((start,end))
    elif len(patterns)>=2:
        start1=sent.find(re.findall(patterns[1], sent)[0])+len(patterns[1])
        end1=-1
        pos.append((start1,end1))
        for i in range(len(patterns)-1,-1,-1):
            start=sent.find(re.findall(patterns[i], sent)[0])+len(patterns[i])
            end=sent.find(re.findall(patterns[i+1], sent)[0])+len(patterns[i+1])
            pos.append((start,end))
    return pos    
        
def get_tagger():
    java_path = "C:/ProgramData/Oracle/Java/javapath"
    os.environ['JAVAHOME'] = java_path
    return StanfordPOSTagger('F:/eclipse_doctor/KnowledgeGraph/stanford-pos/english-bidirectional-distsim.tagger','F:/eclipse_doctor/KnowledgeGraph/stanford-pos/english-bidirectional-distsim.tagger')

def pattern_check(pattern,pattern_lib):
#     nltk.pos_tag(text)
    pass

def extract_all_items(data,patterns):
    data_new=[]
    stanford_tagger=get_tagger()
    cnt=0
    for item in data:
        cnt+=1
        concept,pronunciation,pos2definition=extract_item_properties(item)
        for pos2def in pos2definition:
            definition=pos2def["definition"]
#             tagged_text=stanford_tagger.tag(definition.split())
            definition_pure=re.sub(r'\([\s\S]*?\)', "", definition)
            cnt+=1
            attributes2value=process_definition(definition_pure,patterns,stanford_tagger)
            pos2def["attributes"]=attributes2value
        data_new.append(item)
    return data_new

def get_all_pattern(data):
    pattern2attribute={}
    pattern2attribute.update(data["disease"])
    pattern2attribute.update(data["therapy"])
    pattern2attribute.update(data["commonAttribute"])
    return pattern2attribute

def main():
    path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
    path_data= path_project+os.sep+"input"+os.sep+"tagged_items.json"
    path_pattern= path_project+os.sep+"input"+os.sep+"Patterns.json"
#     path_data= path_project+os.sep+"input"+os.sep+"items.json"
#     path_data_output=path_project+os.sep+"output"+os.sep+"test_items.json"
    path_tagged_output=path_project+os.sep+"output"+os.sep+"test_items_tagged.txt"
    pattern2attrubute=get_all_pattern(load_patterns(path_pattern))
    data=load_json(path_data)
    data_new=extract_all_items(data,pattern2attrubute.keys())
    json.dump(data_new, codecs.open(path_tagged_output, 'w','utf-8'),ensure_ascii=False,indent=2)
    
        
if __name__ == '__main__':
    start = datetime.datetime.now()
    print start
    main()
    end = datetime.datetime.now()
    print end
    print str((end - start).seconds)