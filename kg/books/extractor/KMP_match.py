#coding=utf-8
'''
Created on 2017��7��6��

@author: FeiFei
'''

def match_mini_unit(word_pos,word_pattern_sec):
    #匹配最小的单元 词性{RB}或者词not
    if '{' in word_pattern_sec:
        pos=word_pattern_sec[word_pattern_sec.find('{')+1:word_pattern_sec.find('}')]
        if word_pos[1]==pos:
            return True
    else:
        if word_pos[0]==word_pattern_sec:
            return True
    return False    
    
def match_token_sec(word_pos,word_pattern_sec):
    #!not ?{RB} {RB}
    flag=0
    if word_pattern_sec.startswith('!'):
        if match_mini_unit(word_pos,word_pattern_sec[1:])==True:
            flag=0
        else:
            flag=1
    elif word_pattern_sec.startswith('?'):
        if match_mini_unit(word_pos,word_pattern_sec[1:])==True:
            flag=1
        else:
            flag=2
    else:
        if match_mini_unit(word_pos,word_pattern_sec)==True:
            flag=1
        else:
            flag=0
    return flag

def match_token_unit(word_pos,word_pattern_sec):
    #匹配最小的划分如 {RB},?{RB},!not,[?{RB},?not]
    flag=0
    if word_pattern_sec=='*':
        flag=1
    elif '[' in word_pattern_sec:
        token_secs=word_pattern_sec[1:-1].split(',')
        flag=op_list(match_token_sec,word_pos,token_secs,'|')
    else:
        flag=match_token_sec(word_pos,word_pattern_sec)
    
    return flag

def match_or_unit(word_pos,or_unit):
    flag=0
    if '&' in or_unit:
        and_units=or_unit.split('&')
        flag=op_list(match_token_unit, word_pos, and_units, '&')
    else:
        flag=match_token_unit(word_pos,or_unit)
    return flag
    
def match_compound_token(word_pos,word_pattern): 
    #匹配复合token 如 {VB}|{RB}&[!not,] 
    flag=0
    if '|' in word_pattern:
        or_units=word_pattern.split('|')
        flag=op_list(match_or_unit, word_pos,or_units ,'|')
#         for or_unit in or_units:
#             if '&' in or_unit:
#                 and_units=or_unit.split('&')
#                 flag=op_list(match_single_token, word_pos, and_units, '&')
#             else:
#                 flag=match_single_token(word_pos,or_unit)
    else:
        if '&' in word_pattern:
            and_units=word_pattern.split('&')
            flag=op_list(match_token_unit, word_pos, and_units, '&')
        else:
            flag=match_token_unit(word_pos,word_pattern)
#             result=match_single_token(and_units[0])
#             for i in range(1,len(and_units)):
#                 result_i=match_single_token(word_pos, and_units[i])
#                 result+=op(result,result_i,'&')
#             flag=result
    return flag


def op_list(fun,word_pos,l1,op_):
    if len(l1)<2:
        return
    result=fun(word_pos,l1[0])
    for i in range(1,len(l1)):
        result=op(result,fun(word_pos,l1[i]),op_)
    return result
           
def op(n1,n2,op):
    if n1==1 and n2==1 and op=='&':
        return 1
    elif n1==1 and n2==0 and op=='&':
        return 0
    elif n1==0 and n2==1 and op=='&':
        return 0
    elif n1==0 and n2==0 and op=='&':
        return 0
    elif n1==2 and n2==1 and op=='&':
        return 2
    elif n1==2 and n2==0 and op=='&':
        return 2
    elif n1==1 and n2==2 and op=='&':
        return 2
    elif n1==0 and n2==2 and op=='&':
        return 2
    elif n1==2 and n2==2 and op=='|':
        return 2
    elif n1==2 and n2==1 and op=='|':
        return 1
    elif n1==2 and n2==0 and op=='|':
        return 0
    elif n1==1 and n2==2 and op=='|':
        return 1
    elif n1==0 and n2==2 and op=='|':
        return 0
    elif n1==0 and n2==1 and op=='|':
        return 1
    elif n1==1 and n2==0 and op=='|':
        return 1
    elif n1==1 and n2==1 and op=='|':
        return 1
    elif n1==0 and n2==0 and op=='|':
        return 0
         
def match_pt2pt(pw1,pw2):
#pt --> pattern token
# whether two pattern token are equal
    match_words1=pw1.split("|")
    match_words2=pw2.split("|")
    for match_word1 in match_words1:
        for match_word2 in  match_words2:
            if match_word1==match_word2:
                return True
    return False

def match_pts2pts(pts1,pts2):
    '''
    whether two strings are equal, the string was composed of pattern tokens used for partial_table
    '''
    for i in range(len(pts1)):
        if match_pt2pt(pts1[i],pts2[i]):
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
            if match_pts2pts(prefix[i],postfix[i]):
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
    table=caculate_partial_table(pattern_words)
    m=len(sent_pos)
    n=len(pattern_words)
    cur=0
    while cur<=m-n:
        i=0
        j=i
        while j<n:
            flag=match_compound_token(sent_pos[i+cur], pattern_words[j])
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
    pattern='is+?{RB}&!not&!usually+a|an|A|An$0#2.17-2'
    print KMP_match(pattern,sent_pos)
    