#coding=utf-8
'''
Created on 2017��7��6��

@author: FeiFei
'''
import re
from matplotlib.pyplot import flag



def is_match_sent2pattern(word_sent_pos,word_pattern):
    flag=0
    if '|' in word_pattern:
        match_words=word_pattern.split("|")
        for match_word in match_words:
            if '{' in match_word:
                real_match_word=match_word[match_word.find('{')+1:match_word.find('}')]
                if real_match_word==word_sent_pos[1]:
                    if '^' in match_word:
                        #{RB}^[!not,]
                        negative_words=re.findall('\!(.*?),', match_word)
                        if word_sent_pos[0] not in negative_words:
                            flag=1
                            break
                    else:
                        flag=1
                        break
                if '?' in match_word:
                    if '^' in match_word:
                        #{?RB}^[!not,]
                        negative_words=re.findall('\!(.*?),', match_word)
                        if word_sent_pos[0] not in negative_words:
                            can_word=match_word[match_word.find('?')+1:match_word.find('}')]
                            if can_word==word_sent_pos[1]:
                                flag=1
                            else:
                                if flag==1:
                                    pass
                                else:
                                    flag=2
                        else:
                            flag=0
                    else:   
                        #{?RB}            
                        can_word=match_word[match_word.find('?')+1:match_word.find('}')]
                        if can_word==word_sent_pos[1]:
                            flag=1
                        else:
                            if flag==1:
                                pass
                            else:
                                flag=2
            elif match_word.startswith('^'):
                negative_words=re.findall('\!(.*?),', match_word)
                if word_sent_pos[0] not in negative_words:
                    flag=1
                    break
            elif match_word==word_sent_pos[0]:  
                flag=1
                break
    else:
        if '&' in word_pattern:
            pass
        if '{' in word_pattern:
            real_match_word=word_pattern[word_pattern.find('{')+1:word_pattern.find('}')]
            if real_match_word.startswith('^'):
                if real_match_word[1:]==word_sent_pos[1]:
                    flag=0
                else:
                    flag=1
            else:
                if real_match_word==word_sent_pos[1]:
                    if '^' in word_pattern:
                        #{RB}^[!not,]
                        negative_words=re.findall('\!(.*?),', word_pattern)
                        if word_sent_pos[0] not in negative_words:
                            flag=1
                    else:
                        flag=1
            if '?' in word_pattern:
                if '^' in word_pattern:
                    #{?RB}^[!not,]
                    negative_words=re.findall('\!(.*?),', word_pattern)
                    if word_sent_pos[0] not in negative_words: 
                        can_word=word_pattern[word_pattern.find('?')+1:word_pattern.find('}')]
                        if can_word==word_sent_pos[1]:
                            flag=1
                        else:
                            flag=2
                else: 
                    #{?RB}              
                    can_word=word_pattern[word_pattern.find('?')+1:word_pattern.find('}')]
                    if can_word==word_sent_pos[1]:
                        flag=1
                    else:
                        if flag==1:
                            pass
                        else:
                            flag=2
        elif word_pattern.startswith('^'):
            #are
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
    real_pattern=pattern[:pattern.index("$")]
    pattern_words=real_pattern.split("+")
#     start=datetime.datetime.now()
    table=caculate_partial_table(pattern_words)
#     end=datetime.datetime.now()
#     print (end-start).microseconds
    m=len(sent_pos)
    n=len(pattern_words)
    cur=0
    while cur<=m-n:
        i=0
        j=i
        while j<n:
            flag=is_match_sent2pattern(sent_pos[i+cur], pattern_words[j])
#             print flag,sent_pos[i+cur],pattern_words[j],cur
            if flag==0:
                cur += max(j - table[j-1], 1)#有了部分匹配表,我们不只是单纯的1位1位往右移,可以一次移动多位  
                break
            elif flag==1:
                i+=1
                j+=1
            elif flag==2:
                j=i+1
        else:  
            return  cur
    return -1


if __name__=="__main__":
    sent_pos=[(u'It', u'PRP'), (u'is', u'VBZ'), (u'usually', u'RB'), (u'a', u'DT'), (u'symptom', u'NN'), (u'of', u'IN')]
    pattern='is+!{RB}+a|an|A|An$0#2.17-2'
    print KMP_match(pattern,sent_pos)
    