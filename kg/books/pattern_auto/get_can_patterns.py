#coding=utf-8
'''
Created on 2017��7��4��

@author: FeiFei
'''
from kg.books.pattern_auto.KMP_match import get_match_pos
from kg.util.string import cut_truple_list
from itertools import product
from _collections import defaultdict
import nltk
from kg.books.pattern_auto.record import logger

'''
the flowing methods aim to produce candidate patterns
'''

prefix_window_size=5
CYCLE=2 #the max iter num used to shift

def get_can_pos_set(size):
    can_pos_set=[]
    for i in range(size):
        can_pos=[]
        for j in range(size):
            if i<=j:
                can_pos.append(j)
        can_pos_set.append(can_pos)
    return can_pos_set

def getChunkPrefix(size,attribute_value_tokens,sentTokens):
    match_pos=get_match_pos(attribute_value_tokens,sentTokens)
    can_pos_set=[]
    start=match_pos[0]
    if start==-1:
        logger.info('this value cannot match')
#         logger.info('sent:'+str((sentTokens)))
#         logger.info('attribute_value:'+str((attribute_value_tokens)))
        return []
    
    window=[]
    prefixShiftSentList=[]
    '''
    when the start<size, we fetch the window util start from 0,
    when the start>=size, we fetch the window util start from start-size,
    '''
    
    for i in range(CYCLE):
#     for i in range(size):
        if start<size and start<len(sentTokens):
            can_pos_set=get_can_pos_set(start)
            window=sentTokens[:start]
        elif start>=size and start<len(sentTokens):
            can_pos_set=get_can_pos_set(size)
            window=sentTokens[start-size:start]
        else:
            continue
        
        for can_pos in can_pos_set:
            prefix=[]
            for pos in can_pos:
                prefix.append(window[pos])
            prefixShiftSentList.append((prefix,i,sentTokens))
        start=start+1
    
    return  prefixShiftSentList

def getPrefix(size,attribute_value_tokens,sentTokens): 
    chunks=cut_truple_list(attribute_value_tokens,[(';', ':')])
    prefixShiftSentList=[]
    for chunk in chunks:
        prefixShiftSentList.extend(getChunkPrefix(size,chunk,sentTokens))
    return prefixShiftSentList

def truple2list(truple):
    return [truple[0],'{'+truple[1]+'}']
        
def getPatternCan(prefixShiftSentList):
    patternShiftFixtokenSentList=[]
    for  (fixs_token,shift,sent) in prefixShiftSentList:
        truple_list=[]
        if len(fixs_token)==1:
            truple_list=[x for x in product(truple2list(fixs_token[0]))]
        elif len(fixs_token)==2:
            truple_list=[x for x in product(truple2list(fixs_token[0]),truple2list(fixs_token[1]))]
        elif len(fixs_token)==3:
            truple_list=[x for x in product(truple2list(fixs_token[0]),truple2list(fixs_token[1]),truple2list(fixs_token[2]))]
        elif len(fixs_token)==4:
            truple_list=[x for x in product(truple2list(fixs_token[0]),truple2list(fixs_token[1]),truple2list(fixs_token[2]),truple2list(fixs_token[3]))]    
        elif len(fixs_token)==5:
            truple_list=[x for x in product(truple2list(fixs_token[0]),truple2list(fixs_token[1]),truple2list(fixs_token[2]),truple2list(fixs_token[3]),truple2list(fixs_token[4]))]    
        else:
            continue
        
        for truple in truple_list:
            pattern_real='+'.join(truple)
            patternShiftFixtokenSentList.append((pattern_real,shift,fixs_token,sent))
            
    return patternShiftFixtokenSentList


'''
the next method manage the whole process to acquire the patterns we want
'''
def acquire_patterns(data):
    attribute2PSFSList=defaultdict(list)
    attribute2prefix=defaultdict(list)
    for item in data:
        pos2definition=item["pos2definition"]
#         logger.info('concept: %s'%concept)
        for pos2def in pos2definition:
            definition=pos2def['definition']
#             logger.info('definition: \n%s'%definition)
            text=nltk.word_tokenize(definition)
            definition_tokens=nltk.pos_tag(text)
#             logger.info('definition_pos: \n%s'%definition_pos)
            attributes=pos2def['attributes']
            for attribute_name,attribute_value in attributes.iteritems():
                attribute_value_text=nltk.word_tokenize(attribute_value)
                attribute_value_tokens=nltk.pos_tag(attribute_value_text)
                sentTokenList=cut_truple_list(definition_tokens,[('.', '.')])
                prefixShiftSentList=[]
                for sentToken in sentTokenList:
                    prefixTmp=getPrefix(prefix_window_size,attribute_value_tokens,sentToken)
                    if len(prefixTmp)!=0:
                        prefixShiftSentList.extend(prefixTmp)
                for prefixShiftSent in prefixShiftSentList:
                    prefix=prefixShiftSent[0]
                    if len(prefix)>=prefixShiftSent[1]:
                        attribute2prefix[attribute_name].append(('+'.join([x[1] for x in prefix]),prefixShiftSent[1],prefix))
                    
                pSFSList=getPatternCan(prefixShiftSentList)
                attribute2PSFSList[attribute_name].extend(pSFSList)
#             logger.info('\n')
    #PSFFS add the freq in tuple
#     for item in attribute2prefix.iteritems():
#         logger.info(item[0]+":")
#         logger.info(str(item[1]))
    return attribute2PSFSList
#     return attribute2prefix

def test_getChunkPrefix():
    size=5
    attribute_value_tokens=[(u'age', 'NN'), (u'based', 'VBN'), (u'on', 'IN'), (u'skeletal', 'JJ'), (u'measurements', 'NNS'), (u'relative', 'VBP'), (u'to', 'TO'), (u'chronological', 'JJ'), (u'skeletal', 'NN'), (u'development', 'NN')]
    sentTokens=[(u'skeletal', 'JJ'), (u'age', 'NN'), (u'is', 'VBZ'), (u'the', 'DT'), (u'age', 'NN'), (u'based', 'VBN'), (u'on', 'IN'), (u'skeletal', 'JJ'), (u'measurements', 'NNS'), (u'relative', 'VBP'), (u'to', 'TO'), (u'chronological', 'JJ'), (u'skeletal', 'NN'), (u'development', 'NN')]
#     attribute_value_tokens=[(u'phagocytic', 'JJ'), (u'cell', 'NN'), (u'of', 'IN'), (u'the', 'DT'), (u'reticuloendothelial', 'JJ'), (u'system', 'NN'), (u'including', 'VBG'), (u'specialized', 'JJ'), (u'Kupffer\u9225\u6a9a', 'NNP'), (u'cells', 'NNS'), (u'in', 'IN'), (u'the', 'DT'), (u'liver', 'NN'), (u'and', 'CC'), (u'spleen', 'NN'), (u',', ','), (u'and', 'CC'), (u'histiocytes', 'NNS'), (u'in', 'IN'), (u'loose', 'JJ'), (u'connective', 'JJ'), (u'tissue', 'NN')]
#     sentTokens=[(u'macrophage', 'NN'), (u'is', 'VBZ'), (u'any', 'DT'), (u'phagocytic', 'JJ'), (u'cell', 'NN'), (u'of', 'IN'), (u'the', 'DT'), (u'reticuloendothelial', 'JJ'), (u'system', 'NN'), (u'including', 'VBG'), (u'specialized', 'JJ'), (u'Kupffer\u9225\u6a9a', 'NNP'), (u'cells', 'NNS'), (u'in', 'IN'), (u'the', 'DT'), (u'liver', 'NN'), (u'and', 'CC'), (u'spleen', 'NN'), (u',', ','), (u'and', 'CC'), (u'histiocytes', 'NNS'), (u'in', 'IN'), (u'loose', 'JJ'), (u'connective', 'JJ'), (u'tissue', 'NN')]
    for x in getChunkPrefix(size,attribute_value_tokens,sentTokens):
        print x

if __name__=="__main__":
    test_getChunkPrefix()
    pass
