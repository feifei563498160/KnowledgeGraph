#coding=utf-8
'''
Created on 2017Äê7ÔÂ6ÈÕ

@author: FeiFei
'''
import re
from kg.books.extractor.KMP_match import KMP_match
from kg.books.extractor.recorder import logger


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
        pattern2range[pattern]=(pattern_start,pattern_start+len(pattern[:pattern.index("$")].split('+')))
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
    logger.info('sorted_pattern:¡¡'+str(sort_pos2patterns))
    
    pattern2range=get_pattern_range(patterns, sent_pos)
    logger.info('pattern2range:¡¡'+str(pattern2range))
    
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