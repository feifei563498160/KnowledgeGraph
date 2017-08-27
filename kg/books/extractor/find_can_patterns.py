#coding=utf-8
'''
Created on 2017��7��6��

@author: FeiFei
'''
from kg.books.extractor.KMP_match import KMP_match
from kg.books.pattern_auto.record import logger

def is_candidate_pattern(pattern, sent_pos):
    pattern_start,match_len=KMP_match(pattern, sent_pos)
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


