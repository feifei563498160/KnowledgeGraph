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

from multiprocessing import Pool

from kg.util.mylogger import log_console_and_file
from kg.util.file import load_json
from kg.util.string import cut_list
from kg.books.analysis_items import extract_item_properties

path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))

path_log_output=path_project+os.sep+"output"+os.sep+"log_regular_verify_test_0_0.txt"
logger=log_console_and_file(path_log_output)
tag_time_all=0
find_candidate_time=0



def load_patterns(path):
    return load_json(path)

def process_definition(definition,pattern2attrubute):
    attributes2value={}
    logger.info('definition: %s'%definition)
    if definition.strip().startswith('See') or definition.strip().startswith('see'):
        process_vacant_definition(definition)
    start=datetime.datetime.now()
    text = nltk.word_tokenize(definition)
    def_pos=nltk.pos_tag(text)
    logger.info(def_pos)
    end=datetime.datetime.now()
    global tag_time_all
    tag_time_all+=(end-start).microseconds
    logger.info('tagging time:%d ' % ((end-start).microseconds))
#     logger.info(def_pos)
    seg_point=[('.','.')]
    sents_pos_period=cut_list(def_pos, seg_point)
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

def process_vacant_definition(definition):
    return 

def get_real_pattern(pattern):
    return pattern[:pattern.index("$")]

def is_match_sent2pattern(word_sent_pos,word_pattern):
    flag=0
    if '|' in word_pattern:
        match_words=word_pattern.split("|")
        for match_word in match_words:
            if '{' in match_word:
                real_match_word=match_word[match_word.find('{')+1:match_word.find('}')]
                if real_match_word==word_sent_pos[1]:
                    if '^' in match_word:
                        negative_words=re.findall('\!(.*?),', match_word)
                        if word_sent_pos[0] not in negative_words:
                            flag=1
                            break
                    else:
                        flag=1
                        break
            elif match_word.startswith('^'):
                negative_words=re.findall('\!(.*?),', match_word)
                if word_sent_pos[0] not in negative_words:
                    flag=1
                    break
            elif match_word==word_sent_pos[0]:  
                flag=1
                break
    else:
        if '{' in word_pattern:
            real_match_word=word_pattern[word_pattern.find('{')+1:word_pattern.find('}')]
            if real_match_word==word_sent_pos[1]:
                if '^' in word_pattern:
                    negative_words=re.findall('\!(.*?),', word_pattern)
                    if word_sent_pos[0] not in negative_words:
                        flag=1
                else:
                    flag=1
        elif word_pattern.startswith('^'):
            negative_words=re.findall('\!(.*?),', word_pattern)
            if word_sent_pos[0] not in negative_words:
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

def is_match_pos2pos(pos1,pos2):
    pass
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
#     start=datetime.datetime.now()
    table=caculate_partial_table(pattern_words)
#     end=datetime.datetime.now()
#     print (end-start).microseconds
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
    elif pattern_start+len(pattern.split('+'))>=len(sent_pos):
        return False
    elif "-0" in pattern:
        if pattern_start!=0:
            return False
        else:
            return True
    else:
        if pattern_start>0:
            return True
        else:
            return False
#     elif "-1" in pattern:
#         if pattern_start>0:
#             return True
#         else:
#             return False
#     elif "-2" in pattern:
#         if pattern_start>=0:
#             return True
#         else:
#             return False
    
    
def find_candidate_pattern(patterns, sent_pos):
    candidate_patterns=[]
    for pattern in patterns:
#         start=datetime.datetime.now()
        if is_candidate_pattern(pattern, sent_pos):
            logger.info(pattern+": is candidate")
            candidate_patterns.append(pattern)
#         end=datetime.datetime.now()
#         print (end-start).microseconds
    return candidate_patterns


def get_pattern_priority(patterns):
    pattern2priority={}
    for pattern in patterns:
        priority=re.findall('#(\d*\.*\d+)', pattern)[0]
        pattern2priority[pattern]=priority
    return pattern2priority

def get_prior_by_priority(patterns,pattern2range):
    pattern2priority=get_pattern_priority(patterns)
    if len(patterns) ==1: 
        return patterns
    remove_pos=[]
#     for i in range(len(patterns)-1,-1,-1):
#         if i in remove_pos:
#             break
#         for j in range(i-1,-1,-1):
#             if j in remove_pos:
#                 break
#             if is_near(pattern2range[patterns[i]],pattern2range[patterns[j]]):
#                 if pattern2priority[patterns[i]]<pattern2priority[patterns[j]]:
#                     remove_pos.append(i)
#                 else:
#                     remove_pos.append(j)
#             else:
#                 break
            
    for i in range(len(patterns)):
        if i in remove_pos:
            break
        for j in range(i+1,len(patterns),1):
            if j in remove_pos:
                break
            if is_near(pattern2range[patterns[i]],pattern2range[patterns[j]]):
                if pattern2priority[patterns[i]]<pattern2priority[patterns[j]]:
                    remove_pos.append(i)
                else:
                    remove_pos.append(j)
            else:
                break 
     
            
    final_patterns=[]
    for i in range(len(patterns)):
        if i not in remove_pos:
            final_patterns.append(patterns[i])
    return  final_patterns 

def is_near(range1,range2):
    '''whether two ranges is near'''
    if not (range1[1]<=range2[0]-1 or range2[1]<=range1[0]-1):   
        return True
    else:
        return False 

def get_pos2patterns(patterns,sent_pos):
    pos2patterns={}
    for pattern in patterns:
        pattern_start=KMP_match(pattern, sent_pos)
        if pattern_start in pos2patterns.keys():
            pos2patterns[pattern_start].append(pattern)
        else:
            pattern_tmp=[]
            pattern_tmp.append(pattern)
            pos2patterns[pattern_start]=pattern_tmp
    return pos2patterns

def get_pattern_range(patterns,sent_pos):
    pattern2range={}
    for pattern in patterns:
        pattern_start=KMP_match(pattern, sent_pos)
        pattern2range[pattern]=(pattern_start,pattern_start+len(get_real_pattern(pattern).split('+')))
    return pattern2range

def is_intersect(range1,range2):
    '''whether two ranges is intersected'''
    if not (range1[1]<=range2[0] or range2[1]<=range1[0] ):   
        return True
    else:
        return False

def get_prior_by_range(sorted_pattern,pattern2range):
    #     get a prioror range'''
    patterns_range=[]
    for pos2pattern in sorted_pattern:
        if len(pos2pattern[1])==0:
            continue
        elif len(pos2pattern[1])>1:
            patterns_range.append(get_max_range_priority_pattern(pos2pattern[1],pattern2range))
        else:
            patterns_range.extend(pos2pattern[1])
    return patterns_range

def get_max_range_priority_pattern(patterns,pattern2range): 
    #get the prior pattern, when multiple pattern occur in a same position, if the pattern have a bigger match range
    if len(patterns)==0:
        return []
    pattern2priority=get_pattern_priority(patterns)
    pattern2priority_sorted=sorted(pattern2priority.iteritems(),key=lambda asd:asd[1],reverse=True)
    top_priority=pattern2priority_sorted[0]
    patterns_top=[]
    patterns_top.append(pattern2priority_sorted[0][0])
    for i in range(1,len(pattern2priority_sorted),1):
        if pattern2priority_sorted[i][1]!=top_priority[1]:
            break
        else:
            patterns_top.append(pattern2priority_sorted[i][0])
            
    pattern2ranges={}
    for pattern in patterns_top:
        pattern2ranges[pattern]=pattern2range[pattern][1]-pattern2range[pattern][0]
#     print max(pattern2ranges.items(), key=lambda x: x[1])[0]
    return max(pattern2ranges.items(), key=lambda x: x[1])[0]

def get_min_pos_pattern(patterns,pattern2range):
    if len(patterns)==0:
        return []
    start_pos=[]
    for pattern in patterns:
        pos=pattern2range[pattern][0]
        start_pos.append(pos)
    return patterns[start_pos.index(min(start_pos))]

def choice_final_pattern(patterns,sent_pos):
    '''
    we have two comparing principles: if two patterns occur in a same position, the bigger range 
    the prior higher; if two pattern have common part or common match in a sentence, 
    occur earlier prior higher
    '''
#     pos2patterns,pattern2range=get_pos_patterns_range(patterns,sent_pos)
    pos2patterns=get_pos2patterns(patterns, sent_pos)
    sort_pos2patterns=sorted(pos2patterns.iteritems(),key=lambda d:d[0], reverse=False)
    logger.info('sorted_pattern:　'+str(sort_pos2patterns))
    
    pattern2range=get_pattern_range(patterns, sent_pos)
    logger.info('pattern2range:　'+str(pattern2range))
    
    patterns_sort_by_range=get_prior_by_range(sort_pos2patterns,pattern2range)
    logger.info('patterns_range: '+str(patterns_sort_by_range))
    
    
    patterns_final=get_prior_by_priority(patterns_sort_by_range,pattern2range)
    logger.info('patterns_final: '+str(patterns_final))
#     patterns_by_priority=get_prior_by_priority(patterns_sort_by_range,pattern2range)
#     logger.info('patterns_by_priority: '+str(patterns_by_priority))
#     
#     patterns_final=get_prior_by_pos(patterns_sort_by_range,pattern2range)
#     logger.info('patterns_final: '+str(patterns_final))
    
    return patterns_final

def get_start_pos(pattern, sent_pos):
    pattern_start=KMP_match(pattern, sent_pos)
    pattern_words=get_real_pattern(pattern).split('+')
    cur=int(re.findall('\$(\d+)',pattern)[0])
    if cur>0:
        logger.info("start move right %d"%cur)
    start_tmp=pattern_start+len(pattern_words)-cur
    start=0
    if sent_pos[start_tmp][0] in [',']:
        start=start_tmp+1
    else:
        start=start_tmp
    return start

def is_not_close(range1,range2):
    '''whether two ranges is near'''
    if not (range1[1]==range2[0] or range2[1]==range1[0]):   
        return True
    else:
        return False 

def get_end_pos(end_current,sent_pos):
    cur=0
    for i in range(end_current-1,0,-1):
        if sent_pos[i][1] not in ['DT','CC','TO','WDT','IN','RB'] and sent_pos[i][0] not in ['be','is','are','that','may','can','performed',',']:
            break
        else:
            cur+=1
    if cur>0:
        logger.info("end move left %d"%cur)
    return end_current-cur

def get_value_pos(patterns,sent_pos):
    '''
    patterns: all the final pattern ,the matched position is reversed,
    we regard the beginning position of a pattern as the beginning position of the value
    '''
    pos_matchs=[]
    if len(patterns)==1:
        start=get_start_pos(patterns[0], sent_pos)
        end=len(sent_pos)
        pos_matchs.append((start,end))
        return pos_matchs
    elif len(patterns)>=2:
        for i in range(len(patterns)-1):
            start_i_1=KMP_match(patterns[i+1],sent_pos)
            start=get_start_pos(patterns[i], sent_pos)
            end=get_end_pos(start_i_1,sent_pos)
            pos_matchs.append((start,end))
        start1=get_start_pos(patterns[-1], sent_pos)
        end1=len(sent_pos)
        pos_matchs.append((start1,end1))
    
    pos_matchs_new=[]
    for i in range(len(pos_matchs)-1):
        if is_not_close(pos_matchs[i],pos_matchs[i+1]) and sent_pos[pos_matchs[i+1][0]-1][1] in ['NN','NNS']:
            pos_matchs_new.append((pos_matchs[i][0],pos_matchs[i+1][0]))
        else:
            pos_matchs_new.append(pos_matchs[i])
    pos_matchs_new.append(pos_matchs[-1])
    return pos_matchs_new


def get_match_result(patterns,pattern2attributes,sent_pos):
    '''
    use the final patterns to match the sent,if ';' exist in the sent, we cut the sent first, 
    otherwise we directly depend the pattern and value position to get the attributes and values
    patterns: the final patterns that used in sentence
    '''
    attributes2value={}
    if (';',':') in sent_pos and not (sent_pos[0][0]=='See' and sent_pos[1][0]=='also'):
        chips=cut_list(sent_pos, [(';',':')])
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
            attributes2value[pattern2attributes[patterns[i]]]=sent.strip()       
            if len(sent.strip())>0 and sent.strip()[-1] in [';',',','.']:
                attributes2value[pattern2attributes[patterns[i]]]=sent.strip()[:-1]
    else:  
        value_pos=get_value_pos(patterns,sent_pos)
        logger.info(str(patterns)+' value_pos: '+str(value_pos))
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
                    
            attributes2value[pattern2attributes[patterns[i]]]=sent.strip()       
            if len(sent.strip())>0 and sent.strip()[-1] in [';',',','.']:
                attributes2value[pattern2attributes[patterns[i]]]=sent.strip()[:-1]
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

def pattern_check(pattern,pattern_lib):
#     nltk.pos_tag(text)
    pass

def extract_items_single_thread(data,pattern2attrubute):
    data_new=[]
    all_time=0
    attributes=set([])
    for item in data:
        concept,pronunciation,pos2definition=extract_item_properties(item)
        for pos2def in pos2definition:
            definition=pos2def["definition"]
#             tagged_text=stanford_tagger.tag(definition.split())
            definition_pure=re.sub(r'\([\s\S]*?\)', "", definition)
#             cnt+=1
            start=datetime.datetime.now()
            for key in pos2def["attributes"]:
                attributes.add(key)
            attributes2value=process_definition(definition_pure,pattern2attrubute)
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

def extract_items_all(data,pattern2attrubute):
    data_new=[]
    all_time=0
#     attributes=set([])
    cnt=0
    for item in data:
#         print 'processing %d item'%cnt
        concept,pronunciation,pos2definition=extract_item_properties(item)
        for pos2def in pos2definition:
            definition=pos2def["definition"]
#             tagged_text=stanford_tagger.tag(definition.split())
            definition_pure=re.sub(r'\([\s\S]*?\)', "", definition)
#             cnt+=1
            start=datetime.datetime.now()
#             for key in pos2def["attributes"]:
#                 attributes.add(key)
            attributes2value=process_definition(definition_pure,pattern2attrubute)
            end=datetime.datetime.now()
            all_time+=(end-start).seconds*1000+(end-start).microseconds
            logger.info('process_definition time: %ds: %dms ' % ((end-start).seconds,(end-start).microseconds))
            pos2def["attributes"]=attributes2value
        cnt+=1
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

def sorted_pattern(data,path_pattern_new):
    sorted_data=sorted(data.iteritems(), key=lambda asd:asd[1],reverse=False)
    with open(path_pattern_new,'w') as fp:
        fp.write("{\n")
        for item in sorted_data:
            fp.write("  \""+item[0]+"\": \""+item[1]+"\",\n")
        fp.write("}")
        
def calculate_proprity2pattern(patterns):
    '''
    pos weigh 0.5, word weigh 1.0,
    '''
    data_new={}
    max_pattern_len=0
    for pattern in patterns.keys():
        if len(pattern.split("+"))>max_pattern_len:
            max_pattern_len=len(pattern.split("+"))
    print max_pattern_len       
    for pattern,attribute in patterns.iteritems():
#         print pattern
        pattern_words=get_real_pattern(pattern).split('+')
        prority=0.0
        for word in pattern_words:
            weigh_word=0.0
            if '|' in word:
                can_words=word.split('|')
                for can_word in can_words:
                    if '{' in can_word:
                        weigh_word+=1.0/(max_pattern_len+1)
                    else:
                        weigh_word+=1.0
                weigh_word=weigh_word/len(can_words)
            else:
                if '{' in word:
                    weigh_word=1.0/(max_pattern_len+1)
                else:
                    weigh_word=1.0
            prority+=weigh_word
#         prority=round(prority/len(pattern_words),2)
        prority=round(prority,2)
        pattern_new=re.sub('#(\d*\.*\d+)', '#'+str(prority), pattern)
        data_new[pattern_new]=attribute
    return data_new    
        
def IE():
    path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
    path_data= path_project+os.sep+"input"+os.sep+"items_tagged_modified.json"
    path_pattern= path_project+os.sep+"input"+os.sep+"patterns.json"
#     path_data= path_project+os.sep+"input"+os.sep+"items.json"
#     path_data_output=path_project+os.sep+"output"+os.sep+"test_items.json"
    path_tagged_output=path_project+os.sep+"output"+os.sep+"items_tagged_auto.json"
    pattern2attrubute=load_patterns(path_pattern)
    logger.info("loaded all the patterns")
    data=load_json(path_data)
    logger.info("loaded all the data")
    data_new=extract_items_single_thread(data,pattern2attrubute)
#     data_new=extractor_multi_thread(data,pattern2attrubute,stanford_tagger)
    logger.info("has extracted all the attributes")
    json.dump(data_new, codecs.open(path_tagged_output, 'w','utf-8'),ensure_ascii=False,indent=2)
    logger.info("output over")

def IE_auto_pattern():
    path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
    path_data= path_project+os.sep+"input"+os.sep+"test"+os.sep+"items_tagged_modified_test.json"
    path_pattern= path_project+os.sep+"input"+os.sep+"test"+os.sep+"PatternsTest.json"
#     path_data= path_project+os.sep+"input"+os.sep+"items.json"
#     path_data_output=path_project+os.sep+"output"+os.sep+"test_items.json"
    path_tagged_output=path_project+os.sep+"output"+os.sep+"items_tagged_auto.json"
    pattern2attrubute=load_patterns(path_pattern)
    logger.info("loaded all the patterns")
    data=load_json(path_data)
    logger.info("loaded all the data")
    data_new=extract_items_single_thread(data,pattern2attrubute)
#     data_new=extractor_multi_thread(data,pattern2attrubute,stanford_tagger)
    logger.info("has extracted all the attributes")
    json.dump(data_new, codecs.open(path_tagged_output, 'w','utf-8'),ensure_ascii=False,indent=2)
    logger.info("output over")


def test():
    pattern="the|one of+-0"
    pattern_words=get_real_pattern(pattern).split('+')
    sent="a tooth, root, or implant used for support and retention of a fixed or removable prosthesis."
    sent='substance abuse is the misuse of legal or illegal substances with the intent to alter some aspect of the user experience .'
    tokens=nltk.word_tokenize(sent)
    sent_pos=nltk.pos_tag(tokens)
    
    range1=(1,2)
    range2=(3,5)
    print is_near(range1,range2)

def test2():
    path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
    path_pattern= path_project+os.sep+"input"+os.sep+"patterns.json"
#     path_tagged_output= path_project+os.sep+"output"+os.sep+"patterns_priority.json"
    path_pattern_new= path_project+os.sep+"output"+os.sep+"patterns_priority_sorted.json"
    data=load_json(path_pattern)
    data_new=calculate_proprity2pattern(data)
#     json.dump(data_new, codecs.open(path_tagged_output, 'w','utf-8'),ensure_ascii=False,indent=2)
    sorted_pattern(data_new,path_pattern_new)

def test3():
    path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
    path_data= path_project+os.sep+"input"+os.sep+"items_tagged_modified_test.json"
    path_pattern= path_project+os.sep+"input"+os.sep+"PatternsTest.json"
#     path_data= path_project+os.sep+"input"+os.sep+"items.json"
#     path_data_output=path_project+os.sep+"output"+os.sep+"test_items.json"
    path_tagged_output=path_project+os.sep+"output"+os.sep+"items_tagged_auto.json"
    pattern2attrubute=load_patterns(path_pattern)
    logger.info("loaded all the patterns")
    data=load_json(path_data)
    logger.info("loaded all the data")
    data_new=extract_items_single_thread(data,pattern2attrubute)
#     data_new=extractor_multi_thread(data,pattern2attrubute,stanford_tagger)
    logger.info("has extracted all the attributes")
    json.dump(data_new, codecs.open(path_tagged_output, 'w','utf-8'),ensure_ascii=False,indent=2)
    logger.info("output over")
    
def test4():
    path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
    path_data= path_project+os.sep+"input"+os.sep+"items_modified.json"
    path_pattern= path_project+os.sep+"input"+os.sep+"patterns.json"
#     path_data= path_project+os.sep+"input"+os.sep+"items.json"
#     path_data_output=path_project+os.sep+"output"+os.sep+"test_items.json"
    path_tagged_output=path_project+os.sep+"output"+os.sep+"items_modified_auto.json"
    pattern2attrubute=load_patterns(path_pattern)
    logger.info("loaded all the patterns")
    data=load_json(path_data)
    logger.info("loaded all the data")
    data_new=extract_items_all(data,pattern2attrubute)
#     data_new=extractor_multi_thread(data,pattern2attrubute,stanford_tagger)
    logger.info("has extracted all the attributes")
    json.dump(data_new, codecs.open(path_tagged_output, 'w','utf-8'),ensure_ascii=False,indent=2)
    logger.info("output over")  
     
def test5():
    path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
    path_source= path_project+os.sep+"input"+os.sep
#     get_log_path(path_source)

def test6():
    path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
    path_data= path_project+os.sep+"input"+os.sep+"items_tagged_modified.json"
    data=load_json(path_data)
    attributes=set([])
    for item in data:
        concept,pronunciation,pos2definition=extract_item_properties(item)
        for pos2def in pos2definition:
            for attribute in pos2def['attributes'].keys():
                attributes.add(attribute)
                
    for x in sorted(list(attributes)):
        print x
 
def test7():
    path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
    path_data= path_project+os.sep+"input"+os.sep+"items_tagged_modified.json"
    data=load_json(path_data)
    attributes=set([])
    for item in data:
        concept,pronunciation,pos2definition=extract_item_properties(item)
        for pos2def in pos2definition:
            definition=pos2def['definition']
            grammar = "NP: {<DT>?<JJ>*<NN>}"
            tokens=nltk.word_tokenize(definition)
            tagged=nltk.pos_tag(tokens)
            print nltk.RegexpParser(grammar).parse(tagged)
            
if __name__ == '__main__':
    start = datetime.datetime.now()
    logger.info(start)
    print start
#     main()
#     test()
#     IE()
    test7()
#     test5()

#     IE_auto_pattern()
    end = datetime.datetime.now()
    logger.info(end)
    print end
    print (end - start).seconds,(end - start).microseconds
    logger.info("cost time: "+str((end - start).seconds))
    
    