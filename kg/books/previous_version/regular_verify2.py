#coding=utf-8
'''
Created on 2017��2��10��

@author: feifei
'''
import chardet
import os
import sys
import json
import datetime
from nltk.tag.stanford import StanfordPOSTagger
from kg.util.file import load_json
from kg.util.string import cut_list
from kg.books.analysis_items import extract_item_properties
import codecs
import re
from kg.util.mylogger import log_console_and_file
from multiprocessing import Pool
import multiprocessing
import threading

path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
path_log_output=path_project+os.sep+"output"+os.sep+"log_regular_verify.txt"
logger=log_console_and_file(path_log_output)

def load_patterns(path):
    return load_json(path)

def process_definition(definition,pattern2attrubute,tagger):
    attributes2value={}
    type=sys.getfilesystemencoding()
    def_pos=tagger.tag(seg_sent(definition).strip().split())
    logger.info(def_pos)
    seg_point=[('.','.'),(';',':')]
    sents_pos=cut_list(def_pos, seg_point)
    for sent_pos in sents_pos:
        logger.info("sent_pos: "+str(sent_pos))
        sent=produce_new_sent(sent_pos)
        logger.info("sent_cut: "+sent)
        candidate_patterns=find_candidate_pattern(pattern2attrubute.keys(),sent_pos)
        logger.info("candidate_patterns: "+str(candidate_patterns))
        if len(candidate_patterns)==0:
            continue
        choiced_patterns=choice_final_pattern(candidate_patterns,sent_pos)
        logger.info("choiced_patterns: "+str(choiced_patterns))
        attributes2value.update(get_match_result(choiced_patterns,pattern2attrubute, sent_pos))
        logger.info("attributes2value:　"+str(attributes2value))
    logger.info("whole attributes2value: "+str(attributes2value))
    return attributes2value

# def judge_category(concept):
#     pass
def produce_new_sent(sent_pos):
    sent=""
    for word_pos in sent_pos:
        sent+=word_pos[0]+" "
    return sent

def find_candidate_pattern(patterns, sent_pos):
    candidate_patterns=[]
    for pattern in patterns:
        if is_candidate_pattern(pattern, sent_pos):
            logger.info(pattern+": is candidate")
            candidate_patterns.append(pattern)
    return candidate_patterns

def is_match_sent2pattern(word_sent_pos,word_pattern):
    flag=0
    if '|' in word_pattern:
        match_words=word_pattern.split("|")
        for match_word in match_words:
            if '{' in match_word:
                real_match_word=match_word[match_word.find('{')+1:match_word.find('}')]
                if real_match_word==word_sent_pos[1]:
                    flag=1
                    break
            elif match_word==word_sent_pos[0]:  
                flag=1
                break
    else:
        if  word_pattern==word_sent_pos[0]:
            flag=1
    return flag       

def is_match_pattern2pattern(word_pattern1,word_pattern2):
    match_words1=word_pattern1.split("|")
    match_words2=word_pattern2.split("|")
    for match_word1 in match_words1:
        for match_word2 in  match_words2:
            if match_word1==match_word2:
                return True
            else:
                continue
    return False

def calculate_next_arr(pattern_words):
    next=[0]*len(pattern_words)
    i=0
    j=-1
    while i<len(str)-1:
        if j==-1 or is_match_pattern2pattern(pattern_words[i],pattern_words[j]):
            i+=1
            j+=1
            if is_match_pattern2pattern(pattern_words[i],pattern_words[j])==False:
                next[i]=j
            else:
                next[i]=next[j]
        else:
            j=next[j]
    return next
    
def exsit_words(pattern,sent_pos):
    real_pattern=get_real_pattern(pattern)
    pattern_words=real_pattern.split("+")
    flag=0
    for i in range(len(sent_pos)):
        for j in range(len(pattern_words)):
            
            if '|' in pattern_words[j]:
                flag_multi_word=0
                match_words=pattern_words[j].split("|")
                for match_word in match_words:
                    if '{' in match_word:
                        real_match_word=match_word[match_word.find('{')+1:match_word.find('}')]
                        if i+j>=len(sent_pos):
                            flag=0
                            break
                        if real_match_word==sent_pos[i+j][1]:
                            flag=1
                            flag_multi_word=1
                            break
                    else:
                        if i+j>=len(sent_pos):
                            flag=0
                            break
                        if match_word==sent_pos[i+j][0]:  
                            flag=1
                            flag_multi_word=1
                            break
                if flag_multi_word==0:
                    flag=0
                    break      
            else:
                if i+j>=len(sent_pos):
                    flag=0
                    break
                if pattern_words[j]==sent_pos[i+j][0]:
                    flag=1
                    continue
                else:
                    flag=0
                    break
        if flag==1:
            return True
    return False
                    
def is_candidate_pattern(pattern, sent_pos):
    if exsit_words(pattern,sent_pos)==False:
        return False
    pattern_start,pattern_end=match_position(pattern, sent_pos)
    if "-0" in pattern:
        if pattern_start!=0:
            return False
        else:
            return True
    elif "-1" in pattern:
        if pattern_start>0:
            return True
        else:
            return False
    else:
        if pattern_start==-1:
            return False
        else:
            return True

def get_real_pattern(pattern):
    real_pattern=""
    if '-0' in pattern:
        real_pattern=pattern[:pattern.find('-0')-1]
    elif '-1' in pattern:
        real_pattern=pattern[:pattern.find('-1')-1]
    else:
        real_pattern=pattern
    return real_pattern

def match_position_KMP_index(pattern,sent_pos):
    real_pattern=get_real_pattern(pattern)
    pattern_words=real_pattern.split("+")
    next=calculate_next_arr(pattern_words)
    i = 0  
    j = 0 
    while i <len(sent_pos) and j <len(pattern_words): 
        if j == -1 or is_match_sent2pattern(sent_pos[i],pattern_words[j]):  
            i+=1  
            j+=1  
        else:    
            j = next[j] 
    if j <len(pattern_words): 
        return -1 
    else:  
    #  返回模式串在主串中的头下标 
        return i - len(pattern_words) 

def match_position(pattern,sent_pos): 
    '''
    use the flag to identify whether a pattern is matched,if '|' exists in a pattern, 
    we should cut the pattern, use the words in every position to match the sent 
    '''
    flag=0
    pattern_start=-1
    pattern_end=-1
#     value_end=-1
    real_pattern=get_real_pattern(pattern)
    pattern_words=real_pattern.split("+")
    for i in range(len(sent_pos)):
        for j in range(len(pattern_words)):
            if '|' in pattern_words[j]:
                flag_multi_word=0
                match_words=pattern_words[j].split("|")
                for match_word in match_words:
                    if '{' in match_word:
                        real_match_word=match_word[match_word.find('{')+1:match_word.find('}')]
                        if i+j>=len(sent_pos):
                            flag=0
                            break
                        if real_match_word==sent_pos[i+j][1]:
                            pattern_start=i
                            flag=1
                            flag_multi_word=1
                            break
                    else:
                        if i+j>=len(sent_pos):
                            flag=0
                            break
                        if match_word==sent_pos[i+j][0]:  
                            pattern_start=i
                            flag=1
                            flag_multi_word=1
                            break
                if flag_multi_word==0:
                    flag=0
                    pattern_start=-1
                    break      
            else:
                if i+j>=len(sent_pos):
                    flag=0
                    break
                if pattern_words[j]==sent_pos[i+j][0]:
                    pattern_start=i
                    flag=1
                    continue
                else:
                    flag=0
                    pattern_start=-1
                    break
        if flag==1:
            pattern_end=i+len(pattern_words)
            break
    return pattern_start,pattern_end

def get_value_pos(patterns,sent_pos):
    '''
    patterns: all the final pattern ,the matched position is reversed,
    we regard the beginning position of a pattern as the beginning position of the value
    '''
    pos=[]
    if len(patterns)==1:
        pattern_start,pattern_end=match_position(patterns[0],sent_pos)
#         start=pattern_end+1
        start=pattern_start
        end=len(sent_pos)
        pos.append((start,end))
    elif len(patterns)>=2:
        for i in range(len(patterns)-1):
            pattern_start_i,pattern_end_i=match_position(patterns[i],sent_pos)
            pattern_start_i_1,pattern_end_i_1=match_position(patterns[i+1],sent_pos)
            start=pattern_start_i
            end=pattern_start_i_1
            pos.append((start,end))
        pattern_start1,pattern_end1=match_position(patterns[-1],sent_pos)
        start1=pattern_start1
        end1=len(sent_pos)
        pos.append((start1,end1))
    return pos

def choice_final_pattern(patterns,sent_pos):
    '''
    we have two comparing principles: if two patterns occur in a same position, the bigger range 
    the prior higher; if two pattern have common part or common match in a sentence, 
    occur earlier prior higher
    '''
    pos2patterns,pattern2range=get_pos_patterns_range(patterns,sent_pos)
    sorted_pattern=sorted(pos2patterns.iteritems(),key=lambda d:d[0], reverse=False)
    logger.info('sorted_pattern:　'+str(sorted_pattern))
    patterns_range=get_prior_range(sorted_pattern,pattern2range)
    logger.info('patterns_range: '+str(patterns_range))
    patterns_final=get_prior_intersect(patterns_range,pattern2range)
    logger.info('patterns_final: '+str(patterns_final))
    return patterns_final

def get_pos_patterns_range(patterns,sent_pos):
    pos2patterns={}
    pattern2range={}
    for pattern in patterns:
        pattern_start,pattern_end=match_position(pattern, sent_pos)
        if pattern_start in pos2patterns.keys():
            pos2patterns[pattern_start].append(pattern)
            pattern2range[pattern]=(pattern_start,pattern_end)
        else:
            pattern_tmp=[]
            pattern_tmp.append(pattern)
            pos2patterns[pattern_start]=pattern_tmp
            pattern2range[pattern]=(pattern_start,pattern_end)
    return pos2patterns,pattern2range

def get_prior_intersect(patterns,pattern2range):
    if len(patterns) ==1: 
        return patterns
    # if a pattern has been proved that it have a intersect with the other pattern, it should be removed in next cycle
    pos=[]
    pattern_intersects=[]
    for i in range(len(patterns)):
        pattern_intersect=[]
        for j in range(i,len(patterns),1):
            if j in pos:
                continue
            else:
                if is_intersect(pattern2range[patterns[i]],pattern2range[patterns[j]]):
                    pattern_intersect.append(patterns[j])
                    pos.append(j)
        pattern_intersects.append(pattern_intersect)
    final_patterns=[]  
    for pattern_intersect in  pattern_intersects:
        if len(pattern_intersect)==0:
            continue
        elif len(pattern_intersect)==1:
            final_patterns.extend(pattern_intersect)
        else:
            final_patterns.append(get_min_pos_pattern(pattern_intersect,pattern2range))
    return  final_patterns
         
def is_intersect(range1,range2):
#     print range1,range2
    if not (range1[1]<=range2[0] or range2[1]<=range1[0] ):   
        return True
    else:
        return False

def get_prior_range(sorted_pattern,pattern2range):
    patterns_range=[]
    for pos2pattern in sorted_pattern:
        if len(pos2pattern[1])==0:
            continue
        elif len(pos2pattern[1])>1:
            patterns_range.append(get_max_range_pattern(pos2pattern[1],pattern2range))
        else:
            patterns_range.extend(pos2pattern[1])
    return patterns_range

def get_max_range_pattern(patterns,pattern2range): 
    #get the prior pattern, when multiple pattern occur in a same position, if the pattern have a bigger match range
    if len(patterns)==0:
        return []
    ranges=[]
    for pattern in patterns:
        range=pattern2range[pattern][1]-pattern2range[pattern][0]
        ranges.append(range)
    return patterns[ranges.index(max(ranges))] 

def get_min_pos_pattern(patterns,pattern2range):
    if len(patterns)==0:
        return []
    start_pos=[]
    for pattern in patterns:
        pos=pattern2range[pattern][0]
        start_pos.append(pos)
    return patterns[start_pos.index(min(start_pos))]

def get_match_result(patterns,pattern2attributes,sent_pos):
    '''
    use the final patterns to match the sent,if ';' exist in the sent, we cut the sent first, 
    otherwise we directly depend the pattern and value position to get the attributes and values
    patterns: the final patterns that used in sentence
    '''
    attributes2value={}
    if (';',':') in sent_pos:
        chips=cut_list(sent_pos, (';',':'))
        for chip in chips:
            value_pos=get_value_pos(patterns,chip)
            logger.info(str(patterns)+'value_pos'+str(value_pos))
            for i in range(len(patterns)-1,-1,-1):
                sent=""
                end=value_pos[i][1]
                slice_chip=chip[value_pos[i][0]:end]
                for word_tag in slice_chip:
                    if word_tag[0] in ['.',';',',']:
                        sent=sent.strip()+word_tag[0]+" "
                    else:
                        sent+=word_tag[0]+" "
                attributes2value[pattern2attributes[patterns[i]]]=sent
    else:  
        value_pos=get_value_pos(patterns,sent_pos)
#         print 'value_pos',value_pos
        for i in range(len(patterns)-1,-1,-1):
#             print i,patterns[i]
            sent=""
            end=value_pos[i][1]
#             print value_pos[i][0],end
            slice_sent_pos=sent_pos[value_pos[i][0]:end]
            for word_tag in slice_sent_pos:
                if word_tag[0] in ['.',';',',']:
                    sent=sent.strip()+word_tag[0]+" "
                else:
                    sent+=word_tag[0]+" "
            attributes2value[pattern2attributes[patterns[i]]]=sent
    return attributes2value

def seg_sent(sent):
    pattern=r'[A-Z]\.+|\$?\d+[\.\d+]?%?|\w+[′’]s|\w+s[′’]|\w+[-\w+]*|[\]\[\.,;\"“”\?\(\)\-\:_`\=<>⅓½×&′’±]'
    seg_result=re.findall(pattern, sent)
    sent_new=""
    for word in seg_result:
        sent_new+=word+" "
    return sent_new.strip()

def pre_processing(sent):
    sent.replace('”', '"').replace('“', '"')
    
def get_tagger():
    java_path = "C:/ProgramData/Oracle/Java/javapath"
    os.environ['JAVAHOME'] = java_path
    return StanfordPOSTagger('F:/eclipse_doctor/KnowledgeGraph/stanford-pos/english-bidirectional-distsim.tagger','F:/eclipse_doctor/KnowledgeGraph/stanford-pos/english-bidirectional-distsim.tagger')

def pattern_check(pattern,pattern_lib):
#     nltk.pos_tag(text)
    pass

def extract_items_single_thread(data,pattern2attrubute,tagger):
    data_new=[]
    for item in data:
        concept,pronunciation,pos2definition=extract_item_properties(item)
        for pos2def in pos2definition:
            definition=pos2def["definition"]
#             tagged_text=stanford_tagger.tag(definition.split())
            definition_pure=re.sub(r'\([\s\S]*?\)', "", definition)
#             cnt+=1
            attributes2value=process_definition(definition_pure,pattern2attrubute,tagger)
            pos2def["attributes"]=attributes2value
        logger.info("\n\n")
        data_new.append(item)
    return data_new

def extract_single_item(data,i,new_data,pattern2attrubute,stanford_tagger):
    print i,'start'
    concept,pronunciation,pos2definition=extract_item_properties(data[i])
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

def get_all_pattern(data):
    pattern2attribute={}
    pattern2attribute.update(data["disease"])
    pattern2attribute.update(data["therapy"])
    pattern2attribute.update(data["commonAttribute"])
    return pattern2attribute

def main():
    path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
    path_data= path_project+os.sep+"input"+os.sep+"tagged_items.json"
#     path_data= path_project+os.sep+"input"+os.sep+"tagged_item_test.json"
    path_pattern= path_project+os.sep+"input"+os.sep+"Patterns.json"
#     path_pattern= path_project+os.sep+"input"+os.sep+"PatternsTest.json"
#     path_data= path_project+os.sep+"input"+os.sep+"items.json"
#     path_data_output=path_project+os.sep+"output"+os.sep+"test_items.json"
    path_tagged_output=path_project+os.sep+"output"+os.sep+"items_tagged_auto.json"
    stanford_tagger=get_tagger()
    pattern2attrubute=get_all_pattern(load_patterns(path_pattern))
    logger.info("loaded all the patterns")
    data=load_json(path_data)
    logger.info("loaded all the data")
    data_new=extract_items_single_thread(data,pattern2attrubute,stanford_tagger)
#     data_new=extractor_multi_thread(data,pattern2attrubute,stanford_tagger)
    logger.info("has extracted all the attributes")
    json.dump(data_new, codecs.open(path_tagged_output, 'w','utf-8'),ensure_ascii=False,indent=2)
    logger.info("output over")
        
if __name__ == '__main__':
    start = datetime.datetime.now()
    logger.info(start)
    print start
    main()
#     sent='''age based on a person′s [] behavior, or “how old they feel.”'''
#     tagger=get_tagger()
# #     print chardet.detect('person′s')
# #     print tagger.tag(sent.split())
#     print tagger.tag(seg_sent(sent).split())
    end = datetime.datetime.now()
    logger.info(end)
    print end
    logger.info("cost time"+str((end - start).seconds))
    
    