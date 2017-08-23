#coding=utf-8
'''
Created on 2017��7��13��

@author: FeiFei
'''
import re
from nltk.tree import Tree
from collections import Counter
import os
import traceback
import json
from kg.books.extractor.load_data import data_modified
from kg.util.string import cut_tuple_list, POSfromstring
from kg.books.extractor.recorder import logger

def getParseTree(lines):
    treeTmp=[]
    itemTmp=[]
    items=[]
    for i in range(len(lines)):
        if lines[i].strip()=='--------':
            itemTmp.append(treeTmp)
            treeTmp=[]
        elif lines[i].strip()=='~~~~~~~':
            items.append(itemTmp)
            itemTmp=[]
        else:
            r1=re.sub(r'Tree|\[|\]','',lines[i])
            r2=r1.replace('(\'','(').replace('\', (',' (').replace('\', \'',' ').replace('\')',')').replace('), (',') (').replace('\', "',' ').replace('")',')')
            sentTree = Tree.fromstring(r2)
#             sent=tagfromstring(lines[i])
            treeTmp.append(sentTree)
    return items

def getVPProd(trees):
    VPList=[]
    for tree in trees:
#         print tree
        productions=tree.productions()
        for production in productions:
            if str(production.lhs())=='VP':
                VPList.append(production.rhs())
    return VPList 

def index_all_VB(POSList):
    VB_pos=[]
    for i in range(len(POSList)):
        if POSList[i][1] in ['VB','VBD','VBG','VBN','VBP','VBZ']:
            VB_pos.append(i)
    return VB_pos

def index_VB(POSList):
    for i in range(len(POSList)):
        if POSList[i][1] in ['VB','VBD','VBG','VBN','VBP','VBZ']:
            return i
    return -1

def getVBContextPos(taggedSent,pos,pre_win,post_win):
    context=[]
    if pos+post_win+1<=len(taggedSent):
        if pre_win<=pos:
            context.extend(taggedSent[pos-pre_win:pos+post_win+1])
        else:
            context.extend(taggedSent[0:pos+post_win+1])   
    else:
        if pre_win<=pos:
            context.extend(taggedSent[pos-pre_win:len(taggedSent)])
        else:
            context.extend(taggedSent[0:len(taggedSent)])
    return context
      
def getVBContextSent(taggedSent):
    VBContextList=[]
    VBPos=index_all_VB(taggedSent)
    pre_win=0
    post_win=1
    for pos in VBPos:
        VBContextList.append('+'.join([x[0] for x in getVBContextPos(taggedSent,pos,pre_win,post_win)]))
    return VBContextList
 
def get_VB_IN(taggedSent):
    VB_IN=[]
    for i in range(len(taggedSent)):
        if i+1<len(taggedSent) and taggedSent[i][1] in ['VB','VBD','VBG','VBN','VBP','VBZ'] and taggedSent[i+1][1]=="IN":
            VB_IN.append(taggedSent[i][0]+"+"+taggedSent[i+1][0])
    return VB_IN

            
def test(fun):
    result=[]
    for item in data_modified:
        pos2defs=item["pos2definition"]
        for pos2def in pos2defs:
            def_tagged_str=pos2def["def_tagged"]
            def_tagged=POSfromstring(def_tagged_str)
            chunks=cut_tuple_list(def_tagged,[('.', '.')])
            for chunk in chunks:
                result.extend(fun(chunk))
    sorted_re=sorted(Counter(result).iteritems(),key=lambda asd:asd[1],reverse=True)
    
    cnt_1=0
    cnt_2=0
    cnt_3=0
    for item in sorted_re:
        logger.info(item)
        print item
        if item[1]>1:
            cnt_1+=1
        if item[1]>2:
            cnt_2+=1
        if item[1]>3:
            cnt_3+=1
            
    print len(sorted_re),cnt_1,cnt_2,cnt_3
    
def cnt_sent_len():
    chunk_len=[]
    VB_pos=[]
    for item in data_modified:
        pos2defs=item["pos2definition"]
        for pos2def in pos2defs:
            def_tagged_str=pos2def["def_tagged"]
            def_tagged=POSfromstring(def_tagged_str)
            chunks=cut_tuple_list(def_tagged,[('.', '.')])
            for chunk in chunks:
                chunk_len.append(len(chunk))
                if chunk[0][0] not in ['Also','See']:
                    VB_pos.append(index_VB(chunk))
#                     logger.info(chunk)
#                     print def_tagged_str
#                     print chunk
#                     logger.info(def_tagged)
#     sorted_c_chunk_len=sorted(Counter(chunk_len).iteritems(),key=lambda asd:asd[1],reverse=True)
    sorted_c_VB_pos=sorted(Counter(VB_pos).iteritems(),key=lambda asd:asd[1],reverse=True)

    for item in sorted_c_VB_pos:
        print item
        
    print len(sorted_c_VB_pos)
if __name__ == '__main__':
#     main()
#     cnt_sent_len()
#     taggedSent=[(u'apparatus', u'NN'), (u'is', u'VBZ'), (u'an', u'DT'), (u'arrangement', u'NN'), (u'of', u'IN')]
#     pos=2
#     pre_win=3
#     post_win=1
#     getVBContextPos(taggedSent,pos,pre_win,post_win)
#     test(getVBContextSent)
    test(get_VB_IN)
    
    