#encoding=utf-8
import codecs
import json
import os
from sklearn.tree import tree
import re

path_test="sources"+os.sep+"json_test.json"
data=json.load(codecs.open(path_test, encoding='UTF-8'))

def get_patterns(obj,patterns):
    if isinstance(obj, basestring)==True:
        return 
    elif isinstance(obj, list)==True:
        for ele in obj:
            get_patterns(ele,patterns)
    elif isinstance(obj, dict)==True:
#         print obj.keys()
        if "patterns" in obj.keys():
            patterns.extend(obj["patterns"])
            return
        else:
            for value in obj.values():
                if isinstance(value, basestring)==True:
                    return
                else:
                    get_patterns(value,patterns)   
        
pattern_all=[]    
get_patterns(data,pattern_all)

# for ele in pattern_all:
#     print ele
    

pattern2attribute={}
pattern2taxonomy={}
for key in data.keys():
    attributes=data[key]["attributes"]
    for name in attributes.keys():
        patterns=attributes[name]["patterns"]
        for pattern in patterns:
            pattern2attribute[pattern]=name
            pattern2taxonomy[pattern]=key

for key,value in  pattern2taxonomy.iteritems():
    print  key,value            
             
for key,value in  pattern2attribute.iteritems():
    print  key,value 




if __name__=="__main__":
    word_sent_pos=[(u'abatement', u'NN'), (u'is', u'VBZ'),(u'usually', u'RB') ,(u'a', u'DT'), (u'decrease', u'NN')]
    word_pattern=['{NN}','is','{?RB}','a']
