#coding=utf-8
'''
Created on 2017��7��6��

@author: FeiFei
'''
import re
import os
import codecs
import json
from kg.books.extractor.recorder import logger

def tagfromstring(POSListString):
    POSList=[]
    tupleList=re.findall(r'\((.*?)\)', POSListString)
    for tup in tupleList:
        tup=tup.replace('", u\'', ' ').replace('u"','').replace("', u'", ' ').replace("u'",'')[:-1]
        word=tup.split(' ')[0]
        POS=tup.split(' ')[1]
        POSList.append((word,POS))
    return POSList

def getTaggedSent(lines):
    defTmp=[]
    itemTmp=[]
    items=[]
    for i in range(len(lines)):
        if lines[i].strip()=='--------':
            itemTmp.append(defTmp)
            defTmp=[]
        elif lines[i].strip()=='~~~~~~~':
            items.append(itemTmp)
            itemTmp=[]
        else:
            sent=tagfromstring(lines[i])
            defTmp.append(sent)
    return items 

# path_data="data"+os.sep+"items_tagged_modified.json"

path_data_tagged_modified="data"+os.sep+"items_tagged_modified_POS.json"
path_data_tagged_modified_extract="out"+os.sep+"items_tagged_modified_extract.json"
data_tagged_modified=json.load(codecs.open(path_data_tagged_modified, encoding='UTF-8'))
logger.info("loaded all the data")

path_data_modified="data"+os.sep+"items_modified_POS.json"
path_data_tagged_modified_extract="out"+os.sep+"items_modified_extract.json"
data_modified=json.load(codecs.open(path_data_modified, encoding='UTF-8'))

path_data_tagged_modified_test="data"+os.sep+"items_tagged_modified_test.json"
path_data_tagged_modified_extract_test="out"+os.sep+"items_tagged_modified_extract_test.json"
data_tagged_modified_test=json.load(codecs.open(path_data_tagged_modified_test, encoding='UTF-8'))

# path_data_modified_test="data"+os.sep+"items_modified_test.json"
# path_data_tagged_modified_extract_test="out"+os.sep+"items_modified_extract_test.json"
# data_modified_test=json.load(codecs.open(path_data_modified_test, encoding='UTF-8'))

logger.info("loaded all the patterns")
path_pattern="sources/patterns.json"
pattern2attrubute=json.load(codecs.open(path_pattern, encoding='UTF-8'))



