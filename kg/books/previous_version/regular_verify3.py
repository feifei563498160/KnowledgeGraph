#coding=utf-8
'''
Created on 2017��2��10��

@author: feifei
'''
'''
compare to the 2ed version we use KMP to match two strings
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
import nltk
from kg.util.mylogger import log_console_and_file
from multiprocessing import Pool
import multiprocessing
import threading

path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
path_log_output=path_project+os.sep+"output"+os.sep+"log_regular_verify.txt"
logger=log_console_and_file(path_log_output)
tag_time_all=0
find_candidate_time=0
def load_patterns(path):
    return load_json(path)

def compare_similar_pos(sent_pos1,sent_pos2):
    cnt_same_word=0
    cnt_same_pos=0
    i=0
    j=0
    while i<len(sent_pos1) and j<len(sent_pos2):
#         print sent_pos1[i][0],sent_pos2[j][0]
        if sent_pos1[i][0]==sent_pos2[j][0]:
            cnt_same_word+=1
            if sent_pos1[i][1]==sent_pos2[j][1]:
                cnt_same_pos+=1
            i+=1
            j+=1
            continue
        else:
            if len(sent_pos1[i:])<len(sent_pos2[j:]):
                j+=1
                continue
            if len(sent_pos1[i:])>len(sent_pos2[j:]):
                i+=1
                continue
        i+=1
        j+=1   
    return float(cnt_same_pos)/cnt_same_word,cnt_same_pos,cnt_same_word

def process_definition(definition,pattern2attrubute,tagger):
    attributes2value={}
    if definition.strip().startswith('See') or definition.strip().startswith('see'):
        return
    logger.info(definition)
#     type=sys.getfilesystemencoding()
    start=datetime.datetime.now()
    text = nltk.word_tokenize(definition)
    def_pos1=tagger.tag(text)
    logger.info(def_pos1)
    def_pos2=nltk.pos_tag(text)
    logger.info(def_pos2)
#     print definition
    logger.info("two tag methods similarity: "+str(compare_similar_pos(def_pos1,def_pos2)))
    print compare_similar_pos(def_pos1,def_pos2)
    end=datetime.datetime.now()
    global tag_time_all
    tag_time_all+=(end-start).microseconds
    logger.info('tagging time:%d ' % ((end-start).microseconds))
#     logger.info(def_pos)
    seg_point=[('.','.'),(';',':')]
    sents_pos=cut_list(def_pos2, seg_point)
    start=datetime.datetime.now()
    end=datetime.datetime.now()
    time_find_candidate_pattern=(end-start).microseconds
    time_choice_final_pattern=(end-start).microseconds
    time_get_match_result=(end-start).microseconds
    for sent_pos in sents_pos:
        logger.info("sent_pos: "+str(sent_pos))
        sent=produce_new_sent(sent_pos)
        logger.info("sent_cut: "+sent)
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
        attributes2value.update(get_match_result(choiced_patterns,pattern2attrubute, sent_pos))
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
        if '{' in word_pattern:
            real_match_word=word_pattern[word_pattern.find('{')+1:word_pattern.find('}')]
            if real_match_word==word_sent_pos[1]:
                flag=1
        elif word_pattern==word_sent_pos[0]:  
            flag=1
    return flag       

def is_match_pattern2pattern(word_pattern1,word_pattern2):
# whether two words are equal
    match_words1=word_pattern1.split("|")
    match_words2=word_pattern2.split("|")
    for match_word1 in match_words1:
        for match_word2 in  match_words2:
            if match_word1==match_word2:
                return True
    return False

def is_match_words2words(words1,words2):
    '''
    whether two strings are equal, 
    '''
    for i in range(len(words1)):
        if is_match_pattern2pattern(words1[i],words2[i]):
            continue
        else:
            return False
    return True
    
def caculate_partial_table(pattern_words):
    '''caculate the jump table to decide the step of a word when the word is not a match'''
    if len(pattern_words)==1:
        return [0]
    ret = [0] 
    for i in range(1,len(pattern_words)):
        prefix=find_prefix(pattern_words,i)
        postfix=find_postfix(pattern_words,i)
        prefix.sort(key=lambda x:len(x))
        postfix.sort(key=lambda x:len(x))
        common=[]
        for i in range(len(prefix)):
            if is_match_words2words(prefix[i],postfix[i]):
                common.append(len(prefix[i]))
        if len(common)==0:
            ret.append(0)
        else:
            ret.append(max(common))
    return ret  

def find_prefix(pattern_words,i):
    '''find the prefixs of a string'''
    prefix=[]
    for j in range(1,i+1):
        prefix.append(pattern_words[:j])
    return prefix

def find_postfix(pattern_words,i):
    '''find the postfixs of a string'''
    postfix=[]
    for j in range(1,i+1):
        postfix.append(pattern_words[j:i+1])
    return postfix

def KMP_match(pattern, sent_pos):
    real_pattern=get_real_pattern(pattern)
    pattern_words=real_pattern.split("+")
    table=caculate_partial_table(pattern_words)
    m=len(sent_pos)
    n=len(pattern_words)
    cur=0
    while cur<=m-n:  
        for i in range(n):
            if is_match_sent2pattern(sent_pos[i+cur], pattern_words[i])==False:
                cur += max(i - table[i-1], 1)#有了部分匹配表,我们不只是单纯的1位1位往右移,可以一次移动多位  
                break  
        else:  
            return  cur
    return -1

def is_candidate_pattern(pattern, sent_pos):
    pattern_start=KMP_match(pattern, sent_pos)
    if pattern_start==-1:
        return False
    elif "-0" in pattern:
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


def get_value_pos(patterns,sent_pos):
    '''
    patterns: all the final pattern ,the matched position is reversed,
    we regard the beginning position of a pattern as the beginning position of the value
    '''
    pos=[]
    if len(patterns)==1:
        pattern_start=KMP_match(patterns[0], sent_pos)
        start=pattern_start
        end=len(sent_pos)
        pos.append((start,end))
    elif len(patterns)>=2:
        for i in range(len(patterns)-1):
            pattern_start_i=KMP_match(patterns[i],sent_pos)
            pattern_start_i_1=KMP_match(patterns[i+1],sent_pos)
            start=pattern_start_i
            end=pattern_start_i_1
            pos.append((start,end))
        pattern_start1=KMP_match(patterns[-1],sent_pos)
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
        pattern_start=KMP_match(pattern, sent_pos)
        if pattern_start in pos2patterns.keys():
            pos2patterns[pattern_start].append(pattern)
            pattern2range[pattern]=(pattern_start,pattern_start+len(pattern))
        else:
            pattern_tmp=[]
            pattern_tmp.append(pattern)
            pos2patterns[pattern_start]=pattern_tmp
            pattern2range[pattern]=(pattern_start,pattern_start+len(pattern))
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
    '''whether two rang is intersected'''
    if not (range1[1]<=range2[0] or range2[1]<=range1[0] ):   
        return True
    else:
        return False

def get_prior_range(sorted_pattern,pattern2range):
    #     get a prioror range'''
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
    all_time=0
    for item in data:
        concept,pronunciation,pos2definition=extract_item_properties(item)
        for pos2def in pos2definition:
            definition=pos2def["definition"]
#             tagged_text=stanford_tagger.tag(definition.split())
            definition_pure=re.sub(r'\([\s\S]*?\)', "", definition)
#             cnt+=1
            start=datetime.datetime.now()
            attributes2value=process_definition(definition_pure,pattern2attrubute,tagger)
            end=datetime.datetime.now()
            all_time+=(end-start).seconds*1000+(end-start).microseconds
            logger.info('process_definition time: %ds: %dms ' % ((end-start).seconds,(end-start).microseconds))
            pos2def["attributes"]=attributes2value
        logger.info("\n\n")
        data_new.append(item)
    global tag_time_all
    logger.info("tag all time is: %d"%tag_time_all)
    global find_candidate_time
    logger.info("find candidate time is: %d"%find_candidate_time)
    logger.info("all time is: %d"%all_time)
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
    
def test2():
    path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
    path_data= path_project+os.sep+"input"+os.sep+"tagged_items.json"
    data=load_json(path_data)
    tagger=get_tagger()
    cnt_same_pos_all=0
    cnt_same_word_all=0
    for item in data:
        concept,pronunciation,pos2definition=extract_item_properties(item)
        for pos2def in pos2definition:
            definition=pos2def["definition"]
        text = nltk.word_tokenize(definition)
        def_pos1=tagger.tag(text)
        logger.info(def_pos1)
        def_pos2=nltk.pos_tag(text)
        logger.info(def_pos2)
        similar,cnt_same_pos,cnt_same_word=compare_similar_pos(def_pos1, def_pos2)
        cnt_same_pos_all+=cnt_same_pos
        cnt_same_word_all+=cnt_same_word
    print float(cnt_same_pos_all)/cnt_same_word_all
    

def test1():
    pattern="used+for"
    pattern_words=get_real_pattern(pattern).split('+')
    sent="a tooth, root, or implant used for support and retention of a fixed or removable prosthesis."
    stanford_tagger=get_tagger()
    sent_pos=stanford_tagger.tag(seg_sent(sent).strip().split())
    print sent_pos
#     print is_match_sent2pattern(sent_pos[0], pattern_words[0])
#     print is_match_pattern2pattern(pattern_words[0], pattern_words[1])
#     print calculate_next_arr(pattern_words)
    print caculate_partial_table(pattern_words)
    print KMP_match(pattern, sent_pos)
#     print match_position_KMP_index(pattern, sent_pos)
    
if __name__ == '__main__':
    start = datetime.datetime.now()
    logger.info(start)
    print start
#     main()
    test2()
    end = datetime.datetime.now()
    logger.info(end)
    print end
    logger.info("cost time"+str((end - start).seconds))
    
    