#coding=utf-8
'''
Created on 2017��5��10��

@author: FeiFei
'''
import re
import os
import nltk
import codecs
import json

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

def extract_item_properties(item):
    return item["concept"],item["pronunciation"],item["pos2definition"]    

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
   
def count_match(pattern,data,pattern2attrubute):
    cnt=0
    for item in data:
        concept,pronunciation,pos2definition=extract_item_properties(item)
        for pos2def in pos2definition:
            definition=pos2def["definition"]
            definition_pure=re.sub(r'\([\s\S]*?\)', "", definition)
            text = nltk.word_tokenize(definition_pure)
            def_pos=nltk.pos_tag(text)
            seg_point=[('.','.')]
            sents_pos_period=cut_list(def_pos, seg_point)
            sents_pos=[]
            for sent_pos_period in sents_pos_period:
                if sent_pos_period[0][0]=='See' and sent_pos_period[1][0]=='also':
                    sents_pos.append(sent_pos_period)
                else:
                    sents_pos.extend(cut_list(sent_pos_period,[(';',':')]))
            for sent_pos in sents_pos:
                if KMP_match(pattern, sent_pos)!=-1:
                    print 'match the concept: \n\t%s' % concept
                    print 'match the definition: \n\t%s' % definition
                    print 'match the sent: \n\t%s' % str(sent_pos)
                    print 'match definition attributes are: \n\t%s' % str(pos2def["attributes"])
                    cnt+=1
                    arg=contain(pattern,pattern2attrubute)
                    if arg:
                        print 'match pattern is: \n\t%s' % pattern2attrubute[arg]
                    else:
                        print 'there is no match attribute'
    return cnt

def contain(pattern_prefix,pattern2attrubute):
    for pattern in pattern2attrubute.keys():
        if pattern.startswith(pattern_prefix):
            return pattern
    return False

def check_pattern(pattern):
    if '+' not in pattern or '$' not in pattern:
        return False
    return True

if __name__ == '__main__':
    path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
    path_data= path_project+os.sep+"input"+os.sep+"items_tagged_modified.json"
    path_pattern=path_project+os.sep+"input"+os.sep+"patterns.json"
    data=json.load(codecs.open(path_data, encoding='UTF-8'))
    pattern2attrubute=json.load(codecs.open(path_pattern, encoding='UTF-8'))
    while True:
        pattern=raw_input('input a pattern:')
        if check_pattern(pattern)==False:
            print 'this is a wrong pattern, input again'
            continue
        match_num=count_match(pattern,data,pattern2attrubute)
        print "count match num: %d\n" % match_num
    
