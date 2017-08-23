#coding=utf-8
'''
Created on 2016��12��29��

@author: feifei
'''
import re
import os
import json
from kg.util.file import load_json
from kg.books.analysis_items import extract_item_properties
import codecs
from kg.util.mylogger import log_console_and_file
from collections import Counter
import nltk
from nltk.corpus import treebank
import collections
from kg.util.string import cut_list
import traceback

path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
path_log_output=path_project+os.sep+"output"+os.sep+"log_data_modified2.txt"
logger=log_console_and_file(path_log_output)

def para_remove_empty(item,new_lines):
#     print item
    new_item=[] 
    for line in item:
#         print line.strip('\n')
        if len(line.strip())!=0:
            new_item.append(line.strip('\n+?')+" ")
    empty_line="\n\n"  
    new_item.append(empty_line)   
    new_lines.extend(new_item)
        

def split_items(path):
    
    with open(path) as f:
        lines=f.readlines()
        tag_line_num=[]
        new_lines=[]
        cnt=0
        for line in lines:
            pattern_tag_line=r',[\s]+?n[\s]+|,[\s]+?v[\s]+|,[\s]+?adj[\s]+|,[\s]+?adv[\s]+'
            if re.search(pattern_tag_line, line.strip()):
                if "." not in lines[cnt-1]:
                    tag_line_num.append(cnt-1)
                else:
                    tag_line_num.append(cnt)
            cnt+=1
        
        
        for i in range(len(tag_line_num)-1):
            num_start=tag_line_num[i]
            num_end=tag_line_num[i+1]
            item=lines[num_start:num_end]
            para_remove_empty(item,new_lines)
            
               
        num=len(tag_line_num)-1
        last_item=lines[num:-1] 
        para_remove_empty(last_item,new_lines)  
    return new_lines   
 
def output(path,new_lines):
    open(path,"w").writelines(new_lines)
 
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
    sub_strs=re.findall(pattern_tag, line)
    tag_pos=[]
    cnt=0
    prior_pos=line.find(sub_strs[cnt])
    cnt+=1
    tag_pos.append(prior_pos)
    find_tag_pos(line,sub_strs,cnt,prior_pos,tag_pos)
    return tag_pos


def divide_line(line):
    """
    we firstly split the line using the tag pattern,then we find all the ending position in every sub_line,
     lastly we find the all the ending position in the whole line
    """
#     print line
    pattern_tag=r',[\s]+?n(?=[\. /,])|,[\s]+?v(?=[ ])|,[\s]+?adj(?=[ /])|,[\s]+?adv(?=[ ])'
    tag_pos=find_pos(line, pattern_tag)
    end_pos=[]
    for i in range(len(tag_pos)-1):
        end_pos.append(line[tag_pos[i]:tag_pos[i+1]].rfind(".")+tag_pos[i])         
    new_lines=[]
    print end_pos
    new_lines.append(line[:end_pos[0]+1].strip()+"\n\n")
    for i in range(len(end_pos)-1):
        new_lines.append(line[end_pos[i]+1:end_pos[i+1]+1].strip()+"\n\n")
    new_lines.append(line[end_pos[-1]+1:-1].strip()+"\n")    
    return new_lines


def cut_multi_item(lines):
    pattern_tag=r',[\s]+?n(?=[\. /,])|,[\s]+?v(?=[ ])|,[\s]+?adj(?=[ /])|,[\s]+?adv(?=[ ])'
    new_lines=[]
    for line in lines:
        print line
        if len(re.findall(pattern_tag,line))>1:
            new_lines.extend(divide_line(line))
        else:
            new_lines.append(line) 
    return new_lines



def find_error(lines):
    pattern_tag=r',[\s]+?n(?=[\. /,])|,[\s]+?v(?=[ ])|,[\s]+?adj(?=[ /])|,[\s]+?adv(?=[ ])|,[\s]+?prep(?=[ ])'
    cnt=0
    for line in lines:
        if len(re.findall(pattern_tag, line))>1:
            cnt+=1
            print line
    print cnt 
      
def cut_test(): 
    path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
    path_book = path_project+os.sep+"input"+os.sep+"Mosby's Dental Dictionary Cut item3.txt"
    path_output=path_project+os.sep+"output"+os.sep+"Mosby's Dental Dictionary Cut item4.txt"
#     path_book = path_project+os.sep+"input"+os.sep+"cut_test2.txt"
#     path_output=path_project+os.sep+"output"+os.sep+"cut_test_result.txt"
    lines=open(path_book).readlines()
    new_lines=cut_multi_item(lines)
    output(path_output, new_lines)

def test_check_error_copy(): 
    path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
    path_book = path_project+os.sep+"input"+os.sep+"Mosby's Dental Dictionary Cut item3.txt"
    path_output=path_project+os.sep+"output"+os.sep+"Mosby's Dental Dictionary Cut item Prob error.txt"
#     path_book = path_project+os.sep+"input"+os.sep+"cut_test2.txt"
#     path_output=path_project+os.sep+"output"+os.sep+"cut_test_result.txt"
    lines=open(path_book).readlines()
    new_lines=check_error_copy(lines)
    output(path_output, new_lines)
    
    
def check_error_copy(lines):  
    prob_lines=[]
    for i in range(len(lines)-1):
        if len(lines[i].strip())==0:
            continue
        print lines[i]
        print lines[i].strip()[0],lines[i+2].strip()[0]
        dif0=abs(ord(lines[i].strip()[0].lower())-ord(lines[i+2].strip()[0].lower()))
        if dif0>=1:
            prob_lines.append(lines[i])
            prob_lines.append(lines[i+2])
            prob_lines.append("\n\n")
        else:
            print lines[i].strip()[:2],lines[i+2].strip()[:2]
            dif1=abs(ord(lines[i].strip()[1].lower())-ord(lines[i+2].strip()[1].lower()))
            if dif1>=2:
                prob_lines.append(lines[i])
                prob_lines.append(lines[i+2])  
                prob_lines.append("\n\n") 
    return prob_lines   

 
def test_error():   
    path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
    path_book = path_project+os.sep+"input"+os.sep+"Mosby's Dental Dictionary Cut item4.txt"
    lines=open(path_book).readlines()
    find_error(lines)
 
def extract_pronunciation(line):  
    pronunciation=""
    pronunciation_pattern="\(([\s\S]+?)\)"
    pronunciation_result=re.findall(pronunciation_pattern, line)
    if len(pronunciation_result)!=0:
        if "′" in pronunciation_result[0]:
            pronunciation=pronunciation_result[0]
    return pronunciation

def extract_concept(line):
    concept=""
    pos_pattern_single=r' n | n\.pl | n\.pr | adj | v | n/n\.pl | n,| n/adj | n/v | n\.pr/pl | n\.pr\.pl | adj/n | adj/adv | adj/comb | adv | prep '       
    result=re.findall(pos_pattern_single, line)
    head_pos=line.find(result[0])
    if "(" in line[:head_pos]:
        left_bracket_pos=line[:head_pos].find("(")
        if "′" in line[left_bracket_pos:head_pos]:
            concept=line[:left_bracket_pos]
        else:
            concept=line[:head_pos-1]
    else:
        concept=line[:head_pos]
    return concept

def extract_pos_and_definition(line):
    pos=[] 
    definition=[]  
    pos_pattern_single=r' n | n\.pl | n\.pr | adj | v | n/n\.pl | n,| n/adj | n/v | n\.pr/pl | n\.pr\.pl | adj/n | adj/adv | adj/comb | adv | prep '       
    pos_multi_mean=r' n \d\. | n/v \d\. | n/n.pl \d\. | n.pl \d\. | n.pr \d\. | adj \d\. | v \d\. '

    pos_result_multi=re.findall(pos_multi_mean, line)
    if len(pos_result_multi)>=2:
#         pos_result_multi=re.findall(pos_multi_mean, line)
#         pos_reslut_multi_mean_pos=re.findall(pos_multi_mean, line)
        pos_pos=find_pos(line, pos_multi_mean)
        for i in range(len(pos_pos)-1):
            definition.append(line[pos_pos[i]+len(pos_result_multi[i]):pos_pos[i+1]])
        last_defination=line[pos_pos[-1]+len(pos_result_multi[-1]):] 
        for pos_multi in pos_result_multi:
            pos.append(pos_multi.strip())
        definition.append(last_defination)
    elif len(pos_result_multi)==0:
        pos_result_single=re.findall(pos_pattern_single, line)
        pos.append(pos_result_single[0].strip())
        pos_end_pos_result=re.findall(pos_pattern_single, line)
        def_start=line.find(pos_end_pos_result[0])+len(pos_end_pos_result[0])
        definition.append(line[def_start:])
 
    return pos,definition

def txt2json(lines,json_path):
    dicts=[]
    cnt=0
    for line in lines:
        if len(line.strip())!=0:   
#             print line
            pronunciation=extract_pronunciation(line.strip())
            concept=extract_concept(line.strip())
            pos,definition=extract_pos_and_definition(line.strip())
            if len(pos)!=len(definition):
                print "Something wrong to check"
            if len(pos)>2:
                cnt+=1
                print line
            pos2definition=[]
            for i in range(len(pos)):
                pos2definition_single={
                    "pos":pos[i],
                    "definition":definition[i]
                    }
                pos2definition.append(pos2definition_single)
            dict={
                    "concept":concept,
                    "pronunciation":pronunciation,
                    "pos2definition":pos2definition
                }
            dicts.append(dict)
    json.dump(dicts, open(json_path, 'w'),ensure_ascii=False,indent=2)
    print "sum", cnt
            
def find_pattern(lines):
    pattern_set=set([])
    filters=["head, steeple","unstratified epithelium"]
    erro_line=[]
    for line in lines:
        if len(line.strip())==0:
            continue
#         print line
        if line.startswith(filters[0]) or line.startswith(filters[1]):
                continue
        pos_pattern=r',[\s]+?n(?=[\. /,])|,[\s]+?v(?=[ ])|,[\s]+?adj(?=[ /])|,[\s]+?adv(?=[ ])|,[\s]+?prep(?=[ ])'       
        pos=re.findall(pos_pattern, line)
        
#         if len(pos)!=0:
        pos_pos=line.find(pos[0])
#         print line[pos_pos]
        words=line[pos_pos:].split(" ")
#         pattern_set.add(words[0]+"\n")
        pattern_set.add(words[1]+"\n")
        pattern_set.add(words[2]+"\n")
#         else:
#             erro_line.append(line)
    print erro_line
    return pattern_set

def concept_restore(concept_new):
    c=Counter(concept_new)
    concept_real=''
    if c[',']<4:
        concept_new_result=concept_new.split(',')
        concept_new_result.reverse()
        for word in concept_new_result:
            concept_real+=word.strip()+" "
    else:
        concept_real=concept_new
    return concept_real.strip()

def concept_analysis(concept):
    '''
    the brackets has been preprocessed to only one pairs left, 
    the content between the brackets includes abbreviation, S|s, es, 
    pronunciation, modified word, synonym, expansion, other writing,
    so we make different methods to different situation
    '''
    concept_result=['','','']
    concept_new=''
    if concept.strip()[-1]==',':
        concept_new=concept.strip()[:-1]
    else:
        concept_new=concept
    if '(' in concept_new:
        bracket_content=concept[concept.index('(')+1:concept.index(')')]
        if bracket_content.isupper():
            #abbreviation will be returned as a synonym
            concept_result[1]=bracket_content
        concept_new=re.sub(r'\([\s\S]*\)', '', concept_new)
        concept_result[0]=concept_restore(concept_new)
    else:
        concept_result[0]=concept_restore(concept_new)
    return concept_result

def get_tokens_word(tokens):
    words=[]
    for token in tokens:
        words.append(token[0])
    return words

def definition_restore(concept_real, def_tokens):
    final_tokens=[]
    concept_real_tokens=nltk.pos_tag(concept_real)
    deifination_new=''
    if def_tokens[0]=='in':
        if ',' not in def_tokens:
            final_tokens.extend(definition_restore_process(concept_real_tokens,def_tokens))
        else:
            final_tokens.extend(def_tokens[0:def_tokens.index(',')+1])
            final_tokens.extend(definition_restore_process(concept_real_tokens,def_tokens[def_tokens.index(',')+1:]))
    elif def_tokens[0]==',':
        final_tokens.extend(definition_restore_process(concept_real_tokens,def_tokens[def_tokens.index(',')+1:]))
    elif def_tokens[0]=='brand':
        final_tokens.extend(def_tokens)
    else :
        seg_point=['.']
        sents=cut_list(def_tokens, seg_point)
        if ';' in sents[0]:
#             print def_tokens
            sents_new=[]
            chips=cut_list(sents[0], [';'])
            for i in range(len(chips)-1):
                sents_new.extend(definition_restore_process(concept_real_tokens,chips[i]))
                sents_new.append(';')
            sents_new.extend(definition_restore_process(concept_real_tokens,chips[-1]))
            sents_new.append('.')
            final_tokens.extend(sents_new)
        else:
            final_tokens.extend(definition_restore_process(concept_real_tokens,def_tokens))
    return  ' '.join(final_tokens)

def definition_restore_process(concept_real_tokens, def_tokens):
    final_tokens=[]
#     tokens=process_bracket(nltk.pos_tag(def_tokens))
    tokensPOS=nltk.pos_tag(def_tokens)
    
    if len(tokensPOS)<2:
        if tokensPOS[0][1] in ['NN']:
            final_tokens.extend(concept_real_tokens)
            final_tokens.append(('is','VBZ'))
            final_tokens.append(('a','DT'))
            final_tokens.extend(tokensPOS) 
            return [x[0] for x in final_tokens]
        elif tokensPOS[0][1] in ['NNS']:
            final_tokens.extend(concept_real_tokens)
            final_tokens.append(('are','VBZ'))
            final_tokens.append(('the','DT'))
            final_tokens.extend(tokensPOS) 
            return [x[0] for x in final_tokens]
        else:
            print tokensPOS
            return [x[0] for x in tokensPOS]
    try:
        if tokensPOS[0][1] in ['JJ'] and tokensPOS[1][1] in ['DT','IN']:
            final_tokens.extend(concept_real_tokens)
            final_tokens.append(('is','VBZ'))
            final_tokens.extend(tokensPOS)
        elif tokensPOS[0][1] in ['NN'] or (tokensPOS[1][1] in ['NN'] and tokensPOS[0][1] in ['JJ','JJR','RB','VBG'])\
            or tokensPOS[0][1] in ['JJ'] and tokensPOS[1][1] in ['CC','WDT']:
            final_tokens.extend(concept_real_tokens)
            final_tokens.append(('is','VBZ'))
            final_tokens.append(('a','DT'))
            final_tokens.extend(tokensPOS)
        elif  tokensPOS[0][1] in ['NNS'] or (tokensPOS[1][1] in ['NNS'] and tokensPOS[0][1] in ['JJ','JJR','RB','VBG','VBN']):
            final_tokens.extend(concept_real_tokens)
            final_tokens.append(('are','VBZ'))
            final_tokens.append(('the','DT'))
            final_tokens.extend(tokensPOS)
        elif tokensPOS[0][1] in ['CD','DT','RB','VBG'] or \
            (tokensPOS[0][1] in ['VBN'] and tokensPOS[1][1] not in ['JJ']) or\
            (tokensPOS[0][1] in ['TO'] and tokensPOS[1][1] not in ['VB']):
            final_tokens.extend(concept_real_tokens)
            final_tokens.append(('is','VBZ'))
            final_tokens.extend(tokensPOS)
        elif  tokensPOS[0][1] in ['JJS']:   
            final_tokens.extend(concept_real_tokens)
            final_tokens.append(('is','VBZ'))
            final_tokens.append(('the','DT'))
            final_tokens.extend(tokensPOS)
        elif tokensPOS[0][1] in ['MD','VBZ']:
            final_tokens.extend(concept_real_tokens)
            final_tokens.extend(tokensPOS)  
        elif tokensPOS[0][1] in ['PDT'] and tokensPOS[1][1] in ['DT']:
            final_tokens.extend(concept_real_tokens)
            final_tokens.append(('are','VBZ'))
            final_tokens.extend(tokensPOS)  
        elif (tokensPOS[2][1] in ['NN'] and tokensPOS[0][1] in ['JJ'])\
            or (tokensPOS[2][1] in ['NN'] and tokensPOS[1][1] in ['JJ']):
            final_tokens.extend(concept_real_tokens)
            final_tokens.append(('is','VBZ'))
            final_tokens.append(('a','DT'))
            final_tokens.extend(tokensPOS)
        elif (tokensPOS[2][1] in ['NNS'] and tokensPOS[0][1] in ['JJ'])\
            or (tokensPOS[2][1] in ['NNS'] and tokensPOS[1][1] in ['JJ']): 
            final_tokens.extend(concept_real_tokens)
            final_tokens.append(('are','VBZ'))
            final_tokens.append(('the','DT'))
            final_tokens.extend(tokensPOS)
        else:        
            final_tokens.extend(tokensPOS) 
    except Exception:
        print 'Exception tokenPOS: ',tokensPOS
        print traceback.format_exc()
        return [x[0] for x in tokensPOS]
    return [x[0] for x in final_tokens]    

# def process_bracket(def_tokens):
#     new_def_tokens=[]
#     if def_tokens[0][0] in ['(']:
#         if def_tokens[def_tokens.index((')', ')'))+1] in [(',', ','), ('.', '.')] or def_tokens[def_tokens.index((')', ')'))+2] in [(',', ','), ('.', '.')]:
#             new_def_tokens.extend(def_tokens[def_tokens.index((')',')'))+2:])
#         else:
#             new_def_tokens.extend(def_tokens[def_tokens.index((')',')'))+1:])
#     else:
#         new_def_tokens.extend(def_tokens)
#     return new_def_tokens 

def modify_data(data):
    logger.info("starting to transfer the data")
    data_new=[]
    cnt_item=0
    print "data size: %d" % len(data)
    while cnt_item<len(data):
        item=data[cnt_item]
#         print 'processing the %d item' % cnt_item
        logger.info('processing the %d item' % cnt_item)
        concept,pronunciation,pos2definition=extract_item_properties(item)
        concept_result=concept_analysis(concept)
        logger.info(concept+" : concept result is:  "+str(concept_result)+"\n")
        concept_real=concept_result[0]
        item['concept']=concept_real
        if len(concept_result[1])>0:
            item['abbr']=concept_result[1]
        for i in range(len(pos2definition)-1,-1,-1):
            pos2def=pos2definition[i]
            definition=pos2def["definition"]
            def_tokens=nltk.word_tokenize(re.sub(r'\([\s\S]*?\)', "", definition).strip())
            logger.info(def_tokens[0])
            if def_tokens[0] in ['See','see']:
                logger.info('concept: %s \n definition: %s \n is removed '%(concept,definition))
                logger.info('\n')
                pos2definition.remove(pos2def)
                continue
            
            pos=pos2def["pos"]
            if 'n' not in pos:
                logger.info('concept: %s \n definition: %s \n is removed '%(concept,definition))
                logger.info('\n')
                pos2definition.remove(pos2def)
                continue
            
            definition_new=definition_restore(nltk.word_tokenize(concept_real),def_tokens)
            pos2def["definition"]=definition_new
            logger.info("\n"+definition+"\n definition result is:  \n"+definition_new)
        if len(pos2definition)==0:
            data.remove(item)
            logger.info('concept: %s is removed '%concept)
            logger.info('\n')
            continue
        cnt_item+=1
        data_new.append(item)  
#         logger.info('\n')
    print "items left %d "% cnt_item
    return  data_new  

def analysis_data(data):
    cnt=0
    for item in data:
        concept,pronunciation,pos2definition=extract_item_properties(item)
        if len(pos2definition)>1:
            for pos2def in pos2definition:
                definition=pos2def["definition"]
                if definition[0:4] in ['See ', 'see ']:
                    print concept
                    cnt+=1
    print cnt


def main1():
    path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
    tag=1
    path_book=""
    if tag==1:
        path_book = path_project+os.sep+"input"+os.sep+"Mosby's Dental Dictionary Cut item4.txt"
    elif tag==1:
        path_book = path_project+os.sep+"input"+os.sep+"items_test.txt"
    path_output=path_project+os.sep+"output"+os.sep+"items.json"
    txt2json(open(path_book).readlines(), path_output)
  
def main():
    path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
    path_data= path_project+os.sep+"input"+os.sep+"items.json"
#     path_data= path_project+os.sep+"input"+os.sep+"items_test.json"
    path_new_data=path_project+os.sep+"output"+os.sep+"items_modified.json"
#     path_data= path_project+os.sep+"input"+os.sep+"items_tagged_modified1.json"
#     path_data= path_project+os.sep+"input"+os.sep+"items_tagged.json"
#     path_new_data=path_project+os.sep+"output"+os.sep+"items_tagged_modified.json"
#     path_data= path_project+os.sep+"input"+os.sep+"items_test2.json"
#     path_new_data=path_project+os.sep+"output"+os.sep+"items_modified_test.json"
    data=load_json(path_data)
#     analysis_data(data)
    data_new=modify_data(data)
    json.dump(data_new, codecs.open(path_new_data, 'w','utf-8'),ensure_ascii=False,indent=2)
  
def test():
    concept='palatine arch'
#     print concept_analysis(concept)

    definition="a twisting or deformation. A loss of accuracy in reproduction of cavity form."
    
    def_tokens=nltk.word_tokenize(re.sub(r'\([\s\S]*?\)', "", definition).strip())
#     def_tokens=[u'custom', u'abutment', u'is', u'a', u'custom-made', u'post', u'attached', u'to', u'the', u'superior', u'part', u'of', u'the', u'metal', u'dental', u'implant', u'that', u'protrudes', u'through', u'the', u'gingival', u'tissues', u'and', u'onto', u'which', u'the', u'restoration', u'is', u'fitted', u';', u'either', u'machined', u'or', u'cast', u',', u'and', u'used', u'in', u'situations', u'where', u'prefabricated', u'abutments', u'can', u'not', u'be', u'used', u'.']
#     def_tokens=[u'brand', u'name', u':', u'Basajel', u';', u'drug', u'class', u':', u'antacid', u';', u'actions', u':', u'neutralizes', u'gastric', u'acidity', u',', u'binds', u'phosphates', u'in', u'GI', u'tract', u';', u'uses', u':', u'antacid', u',', u'prevention', u'of', u'phosphate', u'stones', u',', u'phosphate', u'binder', u'in', u'chronic', u'renal', u'failure', u'.']
#     def_tokens=[u'zinc', u'phosphate', u'cement', u'is', u'a', u'material', u'used', u'for', u'cementation', u'of', u'inlays', u',', u'crowns', u',', u'bridges', u',', u'and', u'orthodontic', u'appliances', u';', u'occasionally', u'used', u'as', u'a', u'temporary', u'restoration', u'.', u'Prepared', u'by', u'mixing', u'a', u'powder', u'and', u'a', u'liquid', u'.', u'The', u'powders', u'are', u'composed', u'primarily', u'of', u'zinc', u'oxide', u'and', u'magnesium', u'oxides', u'.', u'The', u'principal', u'constituents', u'of', u'the', u'liquid', u'are', u'phosphoric', u'acid', u',', u'water', u',', u'and', u'buffer', u'agents', u'.']
#     
    print definition_restore(nltk.word_tokenize(concept),def_tokens)
#     print concept_restore(concept)
 
    
if __name__=="__main__":
#     test()
    main()
            