#coding=utf-8
'''
Created on 2017��7��6��

@author: FeiFei
'''
from kg.books.extractor.KMP_match import KMP_match
import re
from kg.books.extractor.recorder import logger
from kg.util.string import cut_list

def get_start_pos(pattern, sent_pos):
    pattern_start=KMP_match(pattern, sent_pos)
    pattern_words=pattern[:pattern.index("$")].split('+')
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