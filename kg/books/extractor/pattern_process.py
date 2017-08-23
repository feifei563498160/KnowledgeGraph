'''
Created on 2017Äê7ÔÂ6ÈÕ

@author: FeiFei
'''
import re

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
        pattern_words=pattern[:pattern.index("$")].split('+')
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

def sorted_pattern(data,path_pattern_new):
    sorted_data=sorted(data.iteritems(), key=lambda asd:asd[1],reverse=False)
    with open(path_pattern_new,'w') as fp:
        fp.write("{\n")
        for item in sorted_data:
            fp.write("  \""+item[0]+"\": \""+item[1]+"\",\n")
        fp.write("}")
        
        