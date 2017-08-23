#coding=utf-8
'''
Created on 2016年11月1日

@author: feifei
'''
import os
import chardet
def write_word_frequency(dict_raw,dict_freq):
    f = open(dict_raw,"r")
    words = f.readlines()
#     print words

    userdict = open(dict_freq, 'w')
    for word in words:
#         print chardet.detect(word)
        userdict.write(str(word).strip()+ '\t3'+'\n')
    userdict.close()
    


   
if __name__=="__main__":
    path_project = os.path.abspath(os.path.join(os.getcwd()))
    print path_project
    path=path_project+"/tooth_name_ICD10.txt"
    path_dict_freq=path_project+"/toothICD10_freq"
    write_word_frequency(path,path_dict_freq)
