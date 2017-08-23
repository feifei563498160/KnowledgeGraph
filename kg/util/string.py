#coding=utf-8
'''
Created on 2016��12��5��

@author: feifei
'''
import re
import os
from kg.util.file import load_json


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


def divide_line(line, pattern_tag):
    """
    we firstly split the line using the tag pattern,then we find all the ending position in every sub_line,
     lastly we find the all the ending position in the whole line
    """
#     print line
#     pattern_tag=r',[\s]+?n(?=[\. /,])|,[\s]+?v(?=[ ])|,[\s]+?adj(?=[ /])|,[\s]+?adv(?=[ ])'
    tag_pos=find_pos(line, pattern_tag)
    end_pos=[]
    for i in range(len(tag_pos)-1):
        end_pos.append(line[tag_pos[i]:tag_pos[i+1]].rfind(".")+tag_pos[i])         
    new_lines=[]
#     print end_pos
    new_lines.append(line[:end_pos[0]+1].strip()+"\n\n")
    for i in range(len(end_pos)-1):
        new_lines.append(line[end_pos[i]+1:end_pos[i+1]+1].strip()+"\n\n")
    new_lines.append(line[end_pos[-1]+1:-1].strip()+"\n")    
    return new_lines

def find_all_index(arr,items):
    return [i for i,a in enumerate(arr) if a in items]

def cut_list(arr,items):
    pos=find_all_index(arr,items)
    if len(pos)==0:
#         print "can't find cut tag"
#         print "arr"+str(arr)
        return [arr]
    chips=[]
    if pos[0]!=0:
        first_chip=arr[:pos[0]]
        chips.append(first_chip)
    for i in range(len(pos)-1):
        chips.append(arr[pos[i]+1:pos[i+1]])
    if pos[-1] != len(arr)-1:
        last_chip=arr[pos[-1]+1:]
        chips.append(last_chip)
    return chips

def contain_token(token_cmp,tokens):
    for token in tokens:
        if token_cmp.word==token.word and token_cmp.pos==token.pos:
            return True
    return False

def contain_tuple(tuple_cmp,tuples):
    for tuple_ele in tuples:
        if tuple_cmp[0]==tuple_ele[0] and tuple_cmp[1]==tuple_ele[1]:
            return True
    return False

def find_all_token_index(arr,items):
    return [i for i,a in enumerate(arr) if contain_token(a,items)]

def find_all_truple_index(arr,items):
    return [i for i,a in enumerate(arr) if contain_tuple(a,items)]

def cut_token_list(arr,items):
    pos=find_all_token_index(arr,items)
    if len(pos)==0:
#         print "can't find cut tag"
#         print "arr"+str(arr)
        return [arr]
    chips=[]
    if pos[0]!=0:
        first_chip=arr[:pos[0]]
        chips.append(first_chip)
    for i in range(len(pos)-1):
        chips.append(arr[pos[i]+1:pos[i+1]])
    if pos[-1] != len(arr)-1:
        last_chip=arr[pos[-1]+1:]
        chips.append(last_chip)
    return chips
 
def cut_tuple_list(arr,items):
    pos=find_all_truple_index(arr,items)
    if len(pos)==0:
#         print "can't find cut tag"
#         print "arr"+str(arr)
        return [arr]
    chips=[]
    if pos[0]!=0:
        first_chip=arr[:pos[0]]
        chips.append(first_chip)
    for i in range(len(pos)-1):
        chips.append(arr[pos[i]+1:pos[i+1]])
    if pos[-1] != len(arr)-1:
        last_chip=arr[pos[-1]+1:]
        chips.append(last_chip)
    return chips 

def POSfromstring(POSListString):
    POSList=[]
    tupleList=re.findall(r'\((.*?)\)', POSListString)
    for tup in tupleList:
        tup=tup.replace('", u\'', ' ').replace('u"','').replace("', u'", ' ').replace("u'",'')[:-1]
        word=tup.split(' ')[0]
        POS=tup.split(' ')[1]
        POSList.append((word,POS))
    return POSList 
          
if __name__=="__main__":
    l1=[(u'a', u'DT'), (u'tooth,', u'FW'), (u'root,', u'FW'), (u'or', u'CC'), (u'implant', u'VB'), (u'used', u'VBN'), (u'for', u'IN'), (u'support', u'NN'), (u'and', u'CC'), (u'retention', u'NN'), (u'of', u'IN'), (u'a', u'DT'), (u'fixed', u'JJ'), (u'or', u'CC'), (u'removable', u'JJ'), (u'prosthesis.', u'NN'), (u'See', u'NNP'), (u'also', u'RB'), (u'pontic.', u'VBP')]
    l2=[(u'substance', 'NN'), (u'abuse', 'NN'), (u'is', 'VBZ'), (u'the', 'DT'), (u'misuse', 'NN'), (u'of', 'IN'), (u'legal', 'JJ'), (u'or', 'CC'), (u'illegal', 'JJ'), (u'substances', 'NNS'), (u'with', 'IN'), (u'the', 'DT'), (u'intent', 'NN'), (u'to', 'TO'), (u'alter', 'VB'), (u'some', 'DT'), (u'aspect', 'NN'), (u'of', 'IN'), (u'the', 'DT'), (u'user\u9225\u6a9a', 'JJ'), (u'experience', 'NN'), (u'.', '.'), (u'May', 'NNP'), (u'include', 'NN'), (u'medications', 'NNS'), (u',', ','), (u'illicit', 'NN'), (u'drugs', 'NNS'), (u',', ','), (u'legal', 'JJ'), (u'substances', 'NNS'), (u'with', 'IN'), (u'potential', 'JJ'), (u'mood-altering', 'JJ'), (u'effects', 'NNS'), (u',', ','), (u'or', 'CC'), (u'substances', 'NNS'), (u'whose', 'WP$'), (u'primary', 'JJ'), (u'use', 'NN'), (u'may', 'MD'), (u'not', 'RB'), (u'be', 'VB'), (u'for', 'IN'), (u'human', 'JJ'), (u'consumption', 'NN'), (u'.', '.')]
    
    print cut_tuple_list(l2, [('of', 'IN')])
    
    