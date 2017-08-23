#encoding=utf-8
'''
Created on 2017��8��23��

@author: FeiFei
'''


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
                    
                    
def pattern2obj(data):                 
    pattern2attribute={}
    pattern2taxonomy={}
    for key in data.keys():
        attributes=data[key]["attributes"]
        for name in attributes.keys():
            patterns=attributes[name]["patterns"]
            for pattern in patterns:
                pattern2attribute[pattern]=name
                pattern2taxonomy[pattern]=key
            
    return pattern2attribute,pattern2taxonomy
        
            