#coding=utf-8
'''
Created on 2017��1��12��

@author: feifei
'''
import os
import nltk.stem  
import chardet
def filter_Captital(lines):
    new_lines=[]
    for line in lines:
        
        if len(line.strip())!=0 and isCapitalStart(line.strip()):
                new_lines.append(line.strip())
    return new_lines

def isCapitalStart(line):
    if line[0]>="A" and line[0]<="Z":
        return True
    
def filter_comma(lines):
    newlines=[]
    for line in lines:
#         if line.find(",")!=-1:
#             newlines.append(line[:line.find(",")])
#         else:
            if filter_multi_words_line(line) or filter_single_alpha_and_empty(line):
#             if filter_single_alpha_and_empty(line) and filter_multi_words_line(line):
                continue
            else:
                if is_one_word(line):
                    s = nltk.stem.SnowballStemmer('english')
    #                 print line
    #                 print chardet.detect(line.lower())
                    newlines.append(s.stem(line.lower()))
    return list(set(newlines))

def is_one_word(line):
    if len(line.split(" "))==3:
        return True
    
def filter_multi_words_line(line):
    if len(line.strip().split(" "))>3:
        return True

def filter_single_alpha_and_empty(line):   
    if len(line.strip())==0 or len(line.strip())==1:
        return True
    
def main():
    path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
#     path_book = path_project+os.sep+"input"+os.sep+"prosthodontics.txt"
#     path_out = path_project+os.sep+"output"+os.sep+"prosthodontics_filter_captital.txt"
#     newlines=filter_Captital(open(path_book,"r").readlines())
#     
    path_book = path_project+os.sep+"input"+os.sep+"prosthodontics_filter_comma_2-3words.txt"
    path_out = path_project+os.sep+"output"+os.sep+"prosthodontics_filter_comma_3-words.txt"
    newlines=filter_comma(open(path_book,"r").readlines())
    fp=open(path_out,"w")
    for line in newlines:
        fp.write(line.strip()+"\n")  
        

    
if __name__=="__main__":
    main()