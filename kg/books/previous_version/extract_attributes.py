#coding=utf-8
'''
Created on 2017��1��16��

@author: feifei
'''
import re
import os
import json
import codecs
from collections import Counter
from  kg.books.analysis_items import extract_item_properties

def get_unigram(sent):
    words=re.split(" |,|\.", sent)
    if len(words)<1:
        print "This sentence is empty"
        return []
    return words


def get_bigram(sent):
    words=re.split(" |,|\.", sent)
    if len(words)<2:
        return []
    bigrams=[]
    for i in range(len(words)-1):
        if len(words[i].strip())==0 or len(words[i+1].strip())==0:
            continue
        bigrams.append(words[i]+" "+words[i+1])
    return bigrams


def get_trigram(sent):
    words=re.split(" |,|\.", sent)
    if len(words)<3:
        return []
    trigrams=[]
    for i in range(len(words)-2):
        if len(words[i].strip())==0 or len(words[i+1].strip())==0 or len(words[i+2].strip())==0:
            continue
        trigrams.append(words[i]+" "+words[i+1]+" "+words[i+2])
    return trigrams

def get_sent_ngram(line):
    sents=re.split("\. |; ", line)
    unigrams_sent=[]
    bigrams_sent=[]
    trigrams_sent=[]
    for sent in sents:
        unigrams=get_unigram(sent)
        bigrams=get_bigram(sent)
        trigrams=get_trigram(sent)
        unigrams_sent.extend(unigrams)
        bigrams_sent.extend(bigrams)
        trigrams_sent.extend(trigrams)
    return unigrams_sent,bigrams_sent,trigrams_sent   

def get_all_ngram(lines):
# ,one_thre,two_thre,three_thre
    unigrams_all=[]
    bigrams_all=[]
    trigrams_all=[]
    for line in lines:
        unigrams_sent,bigrams_sent,trigrams_sent=get_sent_ngram(line)
        unigrams_all.extend(unigrams_sent)
        bigrams_all.extend(bigrams_sent)
        trigrams_all.extend(trigrams_sent)
    return unigrams_all,bigrams_all,trigrams_all

def filter_ngram(lines,uni_thre,bi_thre,tri_thre):
    unigrams_all,bigrams_all,trigrams_all=get_all_ngram(lines)
    uni_counter=Counter(unigrams_all)
    bi_counter=Counter(bigrams_all)
    tri_counter=Counter(trigrams_all)
    uni_sort= sorted(uni_counter.iteritems(), key=lambda d:d[1], reverse = True) 
    bi_sort=sorted(bi_counter.iteritems(), key=lambda d:d[1], reverse = True)
    tri_sort=sorted(tri_counter.iteritems(), key=lambda d:d[1], reverse = True)
#     return uni_filter,bi_filter,tri_filter
    return uni_sort,bi_sort,tri_sort

def get_sent_high_freq_word(line,ngrams_filter_words,ngrams_filter_freqs):
    unigrams_sent,bigrams_sent,trigrams_sent=get_sent_ngram(line)
    ngrams_sent=unigrams_sent
    ngrams_sent.extend(bigrams_sent)
    ngrams_sent.extend(trigrams_sent)
    line_result=[]
    for ngram in ngrams_sent:
        if ngram in  ngrams_filter_words:
#             print ngrams_filter_words.index(ngram)
            line_result.append(ngram+" : "+str(ngrams_filter_freqs[ngrams_filter_words.index(ngram)]))
    return line_result   

def get_ngram_filter(new_stop_words,uni_filter,bi_filter,tri_filter,uni_thre,bi_thre,tri_thre):
#     fp=open(path_out,"w")
    ngrams_filter=[]
    for uni in uni_filter:
        if uni[0].lower() in new_stop_words:
            continue
        if uni[1]<uni_thre:
            continue
        ngrams_filter.append(uni)
    for bi in  bi_filter:
#         if bi[0].lower() in new_stop_words:
        if bi[0].lower().split(" ")[0] in new_stop_words and bi[0].lower().split(" ")[1] in new_stop_words:
            continue
        if bi[1]<bi_thre:
            continue
        ngrams_filter.append(bi)
    for tri in tri_filter:
#         if tri[0].lower() in new_stop_words:
        if tri[0].lower().split(" ")[0] in new_stop_words and tri[0].lower().split(" ")[1] in new_stop_words and tri[0].lower().split(" ")[2] in new_stop_words:
            continue
        if tri[1]<tri_thre:
            continue
        ngrams_filter.append(tri)
    return ngrams_filter

def main():
    path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
    path_book = path_project+os.sep+"input"+os.sep+"prosthodontic_items_full.json"
    path_stop_words = path_project+os.sep+"input"+os.sep+"stop_words"
#     path_out = path_project+os.sep+"output"+os.sep+"sorted_result.txt"
    path_sent_words_freq=path_project+os.sep+"output"+os.sep+"sent_words_freq.txt"
    data=json.load(open(path_book,"r"), encoding="utf-8")
    definaitons=[]
    for item in data:
        concept,pronunciation,pos2definition=extract_item_properties(item)
        for pos2def in pos2definition:
            definaitons.append(pos2def["definition"])
    uni_thre=5
    bi_thre=5
    tri_thre=3    
    uni_filter,bi_filter,tri_filter=filter_ngram(definaitons,uni_thre,bi_thre,tri_thre)       
    fp=codecs.open(path_sent_words_freq, 'w','utf-8')
    
    stop_words=open(path_stop_words,"r").readlines()
    new_stop_words=[]
    for stop_word in stop_words:
        new_stop_words.append(stop_word.strip())
        
    ngrams_filter=get_ngram_filter(new_stop_words,uni_filter,bi_filter,tri_filter,uni_thre,bi_thre,tri_thre) 
    del ngrams_filter[0]
    ngrams_filter_words=[]
    ngrams_filter_freqs=[]
    for ngram_filter in ngrams_filter:
        ngrams_filter_words.append(ngram_filter[0])
        ngrams_filter_freqs.append(ngram_filter[1])
        
    for defination in  definaitons:
        line_candidate=get_sent_high_freq_word(defination,ngrams_filter_words,ngrams_filter_freqs)
        fp.write(defination+"\n")
        fp.write(str(line_candidate)+"\n\n")

#     for uni in uni_filter:
#         if uni[0].lower() in new_stop_words:
#             continue
#         if uni[1]<uni_thre:
#             continue
#         fp.write(str(uni)+"\n")
#     fp.write("!!!!!!!!!!!!!!"+"\n")   
#     for bi in  bi_filter:
#         if bi[0].lower().split(" ")[0] in new_stop_words and bi[0].lower().split(" ")[1] in new_stop_words:
#             continue
#         if bi[1]<uni_thre:
#             continue
#         fp.write(str(bi)+"\n")
#     fp.write("!!!!!!!!!!!!!!"+"\n") 
#     for tri in tri_filter:
#         if tri[0].lower() in new_stop_words:
# #         if tri[0].lower().split(" ")[0] in new_stop_words and tri[0].lower().split(" ")[1] in new_stop_words:
#             continue
#         if tri[1]<uni_thre:
#             continue
#         fp.write(str(tri)+"\n")
        
        
if __name__=="__main__":
    main()
        
        
        
            