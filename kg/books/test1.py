#coding=utf-8
'''
Created on 2017��4��5��

@author: FeiFei
'''
from datetime import datetime
import os
from kg.util.file import load_json
import codecs
import json
from collections import Counter
from kg.util.mylogger import log_console_and_file
import re
import sys
from kg.util.string import cut_list
from multiprocessing.pool import Pool
import multiprocessing
import threading
import time
from nltk.tree import Tree
import chardet



try: 
    import xml.etree.cElementTree as ET 
except ImportError: 
    import xml.etree.ElementTree as ET
  
# path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
# path_log_output=path_project+os.sep+"output"+os.sep+"log_test1.txt"
path_log_output="../../log_Mosby_parse.txt"
logger=log_console_and_file(path_log_output)

def test_StanfordAndNLTKPOS():
    import nltk
    from nltk.tag.stanford import StanfordPOSTagger
    sent='a low-calorie sweetener that reduces caries activity and the growth and transmission of S. mutans.'
    sent='a wire formed by drawing a cast structure through a die; used in dentistry for partial denture clasps and orthodontic appliances.'
    sent='readily stained with acid dyes.'
    print chardet.detect(sent)
#     sent='technique metered spray refers to a topical anesthetic dispersal technique that controls the amount and rate at which a drug is administered.'
#     sent='older term for a traumatic ulcer of the oral mucosa.'
#     sent='one or more vertically parallel surfaces of abutment teeth shaped to direct the path of placement and removal of a remarkable partial denture. Also called guiding plane.'
#     sent='agents that bond, seal, or cement particles or objects together.'
#     sent='teeth that are at such an angle as to cause them to be out of centric contact with opposing teeth during occlusion.'
    start=datetime.now()
    text = nltk.word_tokenize(sent)
    nltk_pos=nltk.pos_tag(text)
    
    java_path = "C:/ProgramData/Oracle/Java/javapath"
    os.environ['JAVAHOME'] = java_path
    stanford_tagger=StanfordPOSTagger('F:/eclipse_doctor/KnowledgeGraph/stanford-pos/english-bidirectional-distsim.tagger','F:/eclipse_doctor/KnowledgeGraph/stanford-pos/english-bidirectional-distsim.tagger')
    stanford_pos=stanford_tagger.tag(text)
    print 'nltk_pos: '+str(nltk_pos)
    print 'stanford_pos: '+str(stanford_pos)
#     end=datetime.now()
#     print (end-start).microseconds
    
def test2():   
    path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
    path_data= path_project+os.sep+"input"+os.sep+"simility.txt"
    sum=0
    with open(path_data,'r') as f:
        lines=f.readlines()
        for line in lines:
            sum+=float(line.strip())
    avg=sum/len(lines)
    print avg

def test4():
    path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
    path_data= path_project+os.sep+"input"+os.sep+"items_tagged_modified.json"
    path_pattern= path_project+os.sep+"output"+os.sep+"Patterns_auto.json"
    data=load_json(path_data)
    logger.info("loaded all the data")
#     patterns=acquire_patterns(data)
    logger.info("has acquired all the patterns")
#     json.dump(patterns, codecs.open(path_pattern, 'w','utf-8'),ensure_ascii=False,indent=2)
    logger.info("output over")
 
def test5():
    path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
    path_data= path_project+os.sep+"input"+os.sep+"items_tagged_modified.json"
    
#     path_pattern= path_project+os.sep+"output"+os.sep+"Patterns_auto.json"
    data=load_json(path_data)
    logger.info("loaded all the data")
    values=[]
    for item in data:
        pos2definition=item["pos2definition"]
        for pos2def in pos2definition:
            for value in pos2def["attributes"].values():
                values.append(len(value.split(" ")))
    c_value_len=Counter(values)
    print sorted(c_value_len.iteritems(),key=lambda asd:asd[0],reverse=False)
    logger.info("output over")

def test7():
    path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
    path_data= path_project+os.sep+"input"+os.sep+"items_tagged_modified.json"
    path_tagged_output= path_project+os.sep+"output"+os.sep+"items_tagged_modified_no_bracket.json"
#     path_pattern= path_project+os.sep+"output"+os.sep+"Patterns_auto.json"
    data=load_json(path_data)
    logger.info("loaded all the data")
    data_new=[]
    for item in data:
        pos2definition=item["pos2definition"]        
        for pos2def in pos2definition:
            for attribute,value in pos2def["attributes"].iteritems():
                pos2def["attributes"][attribute]=re.sub(r'\([\s\S]*?\)', "", value)
        data_new.append(item)    
    json.dump(data_new, codecs.open(path_tagged_output, 'w','utf-8'),ensure_ascii=False,indent=2)           
    logger.info("output over")
    

def tranfer_pattern(pattern):
    postfix=pattern[pattern.index('$'):]
    pattern_words=pattern[:pattern.index('$')].split('+')
    pattern_tokens=[]
    for pattern_word in pattern_words:
        token={}
        token['word']=[]
        token['pos']=[]
        if '|' in pattern_word:
            words=pattern_word.split('|')
            for word in words:
                if '{' in word:
                    token['pos'].append(word[1:-1])
                else:
                    token['word'].append(word)
        else:
            if '{' in pattern_word:
                token['pos'].append(pattern_word[1:-1])
            else:
                token['word'].append(pattern_word)         
        pattern_tokens.append(token)  
    pattern_result=''
    for i in range(len(pattern_tokens)-1):
        pattern_result+=(str(pattern_tokens[i])+'+')
    pattern_result+=str(pattern_tokens[-1])
    pattern_result+=postfix
    return pattern_result

def test8():
    path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
    path_data= path_project+os.sep+"output"+os.sep+"patterns_priority.json"
    path_data_new= path_project+os.sep+"output"+os.sep+"patterns_priority_new.json"
    data=load_json(path_data)
    data_new={}
    print data
    for pattern,pattern_name in data.iteritems():
#         print item
        pattern_new=tranfer_pattern(pattern)
        data_new[pattern_new]=pattern_name
    sorted_data=sorted(data.iteritems(), key=lambda asd:asd[1],reverse=True)
    json.dump(sorted_data, codecs.open(path_data_new, 'w','utf-8'),ensure_ascii=False,indent=2)

def test_extactVerbGroup():
    path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
    path_data= path_project+os.sep+"input"+os.sep+"dictionary.xml"
    path_VerbGroup= path_project+os.sep+"output"+os.sep+"VerbGroup.txt"
    fp_VG=open(path_VerbGroup,'w')
    try:
        tree=ET.parse(path_data)
        root=tree.getroot()
    except Exception, e:
        print "Error: can't parse file:  %s" % path_data
        sys.exit(-1)
#     print root.findall('entry')[100].find('head').find('pos').text
    
    verbGroups=set([])
    for entry in root.findall('entry'):
        head=entry.find('head')
        pos=head.find('pos')
        hwd_head=head.find('hwd')
        senses=entry.findall('sense')
        if pos!=None and pos.text=='verb' and hwd_head!=None and senses!=None:
            for sense in senses:
                gramExas=sense.findall('gramExa')
                if gramExas!=None:
                    for gramExa in gramExas:
                        hwd=gramExa.find('hwd')
#                         print hwd.text
                        if hwd!=None and contain(['somebody', 'something', '(that)', 'what', 'why', 'how','where','when','yourself'],hwd.text)==True:
                            hwd_t=hwd.text
                            print hwd_t
                            if hwd_t.endswith('etc'):
                                hwd_t.replace(' etc','')
                            elif 'etc' in hwd_t and hwd_t.endswith('etc')==False:
                                continue
                            
                            hwd_t_news=[]
                            if '/' in hwd_t:
                                if len(hwd_t.split(' '))==2:
                                    hwd_t_words=hwd_t.split(' ')
                                    for hwd_t_word in hwd_t_words[1].split('/'):
                                        hwd_t_news.append(hwd_t_words[0]+' '+hwd_t_word)
                            else:
                                hwd_t_news.append(hwd_t)   
                            for hwd_t_new in  hwd_t_news:      
                                verbGroups.add(re.sub('\(.*?\)', '', hwd_t_new))
#                             fp_VG.write(hwd.text.encode('utf-8')+'\n')
    verbGroups_sorted=sorted(list(verbGroups))
    cnt_two=0
    prepList=[]
    for verbGroup in  verbGroups_sorted:
        if len(verbGroup.split(' '))==2:
            cnt_two+=1
            prepList.append(verbGroup.split(' ')[1])
        fp_VG.write(verbGroup.encode('utf-8')+'\n') 
    c_prep=Counter(prepList)
    sorted_c_prep=sorted(c_prep.iteritems(),key=lambda asd:asd[1],reverse=True)
    print cnt_two
    print sorted_c_prep
    
def contain(ls,text):
    for elem in ls:
        if elem in text:
            return False
    return True

def getProductions(pos):
    from nltk.corpus import treebank
    fileids=treebank.fileids()
    pos_ProductionList=[]
    for fileld in fileids:
        trees=treebank.parsed_sents(fileld)
        for tree in trees:
            productions=tree.productions()
            for production in productions:
                if str(production.lhs())==pos:
                    pos_ProductionList.append(production)
    c_POS=Counter(pos_ProductionList)
    c_POS_sorted=sorted(c_POS.iteritems(),key=lambda asd:asd[1],reverse=True)
    print c_POS_sorted
    
             
def test_PennCorpus():
    from nltk.corpus import treebank
    fileids=treebank.fileids()
    ADJP_ProductionList=[]
    ADVP_ProductionList=[]
    NP_ProductionList=[]
    VP_ProductionList=[]
    for fileld in fileids:
        trees=treebank.parsed_sents(fileld)
        for tree in trees:
            productions=tree.productions()
            for production in productions:
                if str(production.lhs())=='ADJP':
                    ADJP_ProductionList.append(production)
                if str(production.lhs())=='ADVP':
                    ADVP_ProductionList.append(production)
                if str(production.lhs())=='NP':
                    NP_ProductionList.append(production)
                if str(production.lhs())=='VP':
                    VP_ProductionList.append(production)
                    
    print len(ADJP_ProductionList),len(ADVP_ProductionList),len(NP_ProductionList),len(VP_ProductionList)
    c_ADJP=Counter(ADJP_ProductionList)
    c_ADVP=Counter(ADVP_ProductionList)
    c_NP=Counter(NP_ProductionList)
    c_VP=Counter(VP_ProductionList)
    c_ADJP_sorted=sorted(c_ADJP.iteritems(),key=lambda asd:asd[1],reverse=True)
    c_ADVP_sorted=sorted(c_ADVP.iteritems(),key=lambda asd:asd[1],reverse=True)
    c_NP_sorted=sorted(c_NP.iteritems(),key=lambda asd:asd[1],reverse=True)
    c_VP_sorted=sorted(c_VP.iteritems(),key=lambda asd:asd[1],reverse=True)
#     print c_ADJP_sorted
#     print c_ADVP_sorted
#     print c_NP_sorted
#     print c_VP_sorted

def test_Phrase():
    import nltk
    from nltk.corpus import treebank
    fileids=treebank.fileids()
    grammar=r"""
    ADVP:{<RB>(<CC>*<RB>*|<JJ>*)}
    {}
    """
    for fileld in fileids:
        sents=treebank.tagged_sents(fileld)
        for sent in sents:
            tree_Gram=nltk.RegexpParser(grammar).parse(sent)
            for subtree in tree_Gram.subtrees():
                if subtree.label()=="ADVP":
                    print subtree
                    
def test_GrammarParser():
    import nltk
    from nltk.corpus import treebank
    grammar = r"""NP:
    {<DT>*(<NN>|<NNP>|<NNS>)+}          # Chunk everything
    }<VBD|IN>+{      # Chink sequences of VBD and IN
    """
#     tree=treebank.parsed_sents('wsj_0001.mrg')[0]
#     print tree
    grammar_VP=r"""VP:
    {<VBZ><VP>}
    """
#     tree=nltk.RegexpParser(grammar).parse(treebank.parsed_sents('wsj_0001.mrg')[0].pos())
#     print tree
    fileids=treebank.fileids()
    
#     for fileld in fileids:
    for i in range(len(fileids)):
        if i>10:
            break
#         trees=treebank.parsed_sents(fileld)
        trees=treebank.parsed_sents(fileids[i])
        for tree in trees:
            tree_Gram=nltk.RegexpParser(grammar).parse(tree)
            for subtree in tree_Gram.subtrees():
                if subtree.label()=="VP":
                    print subtree

def test_list_copy():
    l2=[1,2,3,4,5,6]
    print id(l2)
    def alter(ll):
        l_tmp=[]
        for ele in ll:
            l_tmp.append(ele+1)                                                                                                                                                                                                       
#         global ll
        del ll[:]
        ll.extend(l_tmp)
        print id(ll)
    
    alter(l2)
    for i in range(3):
        alter(l2)
    
    print l2   

def test_VBPenn():
    from nltk.corpus import treebank
    fileids=treebank.fileids()
    VBContexts=[]
    for i in range(len(fileids)):
        sentPOSList=treebank.tagged_sents(fileids[i])
        for sentPOS in sentPOSList:
#             print 'sentPOS',sentPOS
            VBContext=getVBContext(sentPOS)
#             print 'VBContext',VBContext
            if len(VBContext)!=0:
                POSList=''
                for wordPOS in VBContext:
#                     print 'wordPOS',wordPOS
                    POSList+=wordPOS[1]+'+'
                VBContexts.append((POSList,VBContext))
    print   VBContexts
#     c_VBContexts=Counter(VBContexts)            
#     print   c_VBContexts            
 
def test_VBBrown():
    from nltk.corpus import brown
    fileids=brown.fileids()
    ADJP_ProductionList=[]
    ADVP_ProductionList=[]
    NP_ProductionList=[]
    VP_ProductionList=[]
    for fileld in fileids:
        trees=brown.parsed_sents(fileld)
        for tree in trees:
            productions=tree.productions()
            for production in productions:
                if str(production.lhs())=='ADJP':
                    ADJP_ProductionList.append(production)
                if str(production.lhs())=='ADVP':
                    ADVP_ProductionList.append(production)
                if str(production.lhs())=='NP':
                    NP_ProductionList.append(production)
                if str(production.lhs())=='VP':
                    VP_ProductionList.append(production)
                    
    print len(ADJP_ProductionList),len(ADVP_ProductionList),len(NP_ProductionList),len(VP_ProductionList)
    c_ADJP=Counter(ADJP_ProductionList)
    c_ADVP=Counter(ADVP_ProductionList)
    c_NP=Counter(NP_ProductionList)
    c_VP=Counter(VP_ProductionList)
    c_ADJP_sorted=sorted(c_ADJP.iteritems(),key=lambda asd:asd[1],reverse=True)
    c_ADVP_sorted=sorted(c_ADVP.iteritems(),key=lambda asd:asd[1],reverse=True)
    c_NP_sorted=sorted(c_NP.iteritems(),key=lambda asd:asd[1],reverse=True)
    c_VP_sorted=sorted(c_VP.iteritems(),key=lambda asd:asd[1],reverse=True)
    print c_ADJP_sorted
    print c_ADVP_sorted
    print c_NP_sorted
    print c_VP_sorted

def getVBContext(sentPOS): 
    for i in range(len(sentPOS)):
        if sentPOS[i][1] in ['VB','VBD','VBG','VBN','VBP','VBZ']:
            if i==0:
                return sentPOS[:2]
            elif i>=1 and i<=len(sentPOS)-3:
                return sentPOS[i-1:i+3]
            elif i==len(sentPOS)-1:
                return sentPOS[i-1:i+1]
    return []  

def test_VBMosby():
    import nltk
    path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
    path_data= path_project+os.sep+"input"+os.sep+"items_tagged_modified.json"
    path_data= path_project+os.sep+"output"+os.sep+"items_modified.json"
    data=json.load(codecs.open(path_data, encoding='UTF-8'))
    VBContexts=[]
    VBContextTuple=[]
    for item in data:
        pos2definition=item["pos2definition"]
        for pos2def in pos2definition:
            definition=pos2def["definition"]
            definition_pure=re.sub(r'\([\s\S]*?\)', "", definition)
            text = nltk.word_tokenize(definition_pure)
            def_pos=nltk.pos_tag(text)
            VBContext=getVBContext(def_pos)
            if len(VBContext)!=0:
                POSList=[]
                for wordPOS in VBContext:
#                     print 'wordPOS',wordPOS
                    POSList.append(wordPOS[1])
                VBContexts.append('+'.join(POSList))
                VBContextTuple.append(('+'.join(POSList),VBContext))
#     print VBContexts
    c_VBContexts=Counter(VBContexts)  
    VBContextTuple_sorted=sorted(VBContextTuple,key=lambda asd:asd[0],reverse=False)          
    print   c_VBContexts 
    for VBtuple in   VBContextTuple_sorted:
        logger.info(str(VBtuple))   

def test_ItemFirstTwoWords():
    import nltk
    path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
    path_data= path_project+os.sep+"input"+os.sep+"items.json"
    data=json.load(codecs.open(path_data, encoding='UTF-8'))
    firstTwoWords=[]
    firstTwoWordsTuple=[]
    firstTwoWordsSet=set([])
    for item in data:
        pos2definition=item["pos2definition"]
        for pos2def in pos2definition:
            if pos2def['pos'].startswith('n')==False:
                continue
            definition=pos2def["definition"]
            definition_pure=re.sub(r'\([\s\S]*?\)', "", definition)
            text = nltk.word_tokenize(definition_pure)
            def_pos=nltk.pos_tag(text)
            firstTwoPOS=def_pos[0][1]+'+'+def_pos[1][1]
            firstTwoWords.append(firstTwoPOS)
            firstTwoWordsTuple.append((firstTwoPOS,def_pos[:2]))
#             cases=[]
#             if firstTwoPOS not in firstTwoWordsSet and len(cases)<=2:
#                 firstTwoWordsSet.add(firstTwoPOS)
#                 cases.append(def_pos[:2])
#                 firstTwoWordsTuple.append((firstTwoPOS,cases))
#                 
#             elif len(cases)>2:
#                 del cases[:]
                
    for tuple_ in sorted(firstTwoWordsTuple,key=lambda asd:asd[0],reverse=False):
        logger.info(tuple_)
    c_firstTwoWords=Counter(firstTwoWords)
    print c_firstTwoWords
    print sorted(c_firstTwoWords.keys())
    
    
def test_VBPhrase_Mosby():
    import nltk
    path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
    path_data= path_project+os.sep+"input"+os.sep+"items.json"
    data=json.load(codecs.open(path_data, encoding='UTF-8'))
    for item in data:
        pos2definition=item["pos2definition"]
        for pos2def in pos2definition:
            if pos2def['pos'].startswith('n')==False:
                continue
            definition=pos2def["definition"]
            definition_pure=re.sub(r'\([\s\S]*?\)', "", definition)
            text = nltk.word_tokenize(definition_pure)
            def_pos=nltk.pos_tag(text)
            

def test_parser():
    import nltk
    from nltk.parse import stanford
    from nltk.parse.stanford import StanfordParser
    os.environ['STANFORD_PARSER'] = 'F:/eclipse_doctor/KnowledgeGraph/stanford-parser/stanford-parser.jar'
    os.environ['STANFORD_MODELS'] = 'F:/eclipse_doctor/KnowledgeGraph/stanford-parser/stanford-parser-3.7.0-models.jar'
    java_path = "C:/ProgramData/Oracle/Java/javapath"
    os.environ['JAVAHOME'] = java_path
    
    start = datetime.now()
    print start
    parser = stanford.StanfordParser(model_path="F:/eclipse_doctor/KnowledgeGraph/stanford-parser/englishPCFG.ser.gz")
    end = datetime.now()
    print end
    print "cost time: "+str((end - start).microseconds)
    
    sent='angulated abutment is an abutment whose body is not parallel to the long axis of the implant. It is utilized when the implant is at a different inclination in relation to the proposed prosthesis.'
    start = datetime.now()
    print start
    trees=parser.parse(sent.split())
    end = datetime.now()
    print end
    print "cost time: "+str((end - start).microseconds)
    print 'len(trees)',len(list(trees))
    
    path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
    path_data= path_project+os.sep+"input"+os.sep+"items_tagged_modified.json"
    data=json.load(codecs.open(path_data, encoding='UTF-8'))
    start_all=datetime.now()
    cnt=0
    trees_all=[]
    for item in data:
        pos2definition=item["pos2definition"]
        for pos2def in pos2definition:
            definition=pos2def["definition"]
            definition_pure=re.sub(r'\([\s\S]*?\)', "", definition)
            text = nltk.word_tokenize(definition_pure)
            sents_pos_period=cut_list(text, ['.'])
            for sent_list in sents_pos_period:
                cnt+=1
                start = datetime.now()
#                 print start
                trees=parser.parse(' '.join(sent_list).split())
                trees_all.append(trees)
                end = datetime.now()
#                 print end
#                 print "cost time: "+str((end - start).microseconds)
    end_all=datetime.now()
    print end_all
    sum_time=(end_all-start_all).seconds
    sum_time_mic=(end_all-start_all).microseconds
    avg_time=(end_all-start_all).seconds*1.0/cnt
    print sum_time,sum_time_mic,avg_time,cnt
#     print list(parser.parse(sent.split()))
#     for tree in trees:
# #         print tree
#         productions=tree.productions()
#         for production in productions:
#             if str(production.lhs())=='NP':
#                 print production
 
def test_multiThread(): 
    p=Pool()
    multiprocessing.freeze_support() 
    cpus = multiprocessing.cpu_count()
    lock =threading.Lock() 
    i=1
    result=[]
    while(i):
        if i<10000/cpus:
            if lock.acquire():
                for j in range(cpus):
                    print 'thread: ',i*cpus+j
                    result.append(p.apply_async(fun,args=(i,j)))
                 
                i+=1
                lock.release() 
        else:
            break
    p.close()
    p.join()
    for res in result:
        print res.get()
    
def fun(i,j):
    print 'wait: ',i,j
    time.sleep(1)    
    return str(i)+'; '+str(j)

def test_parseDef(item,parser):
    import nltk
    treeDef=[]
    pos2definition=item["pos2definition"]
    for pos2def in pos2definition:
        definition=pos2def["definition"]
        definition_pure=re.sub(r'\([\s\S]*?\)', "", definition)
        text = nltk.word_tokenize(definition_pure)
        sents_pos_period=cut_list(text, ['.'])
        for sent_list in sents_pos_period:
            tree=parser.parse(' '.join(sent_list).split())
            treeDef.append(tree)
    return treeDef
    
def test_multiThreadMosby(): 
    path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
    path_data= path_project+os.sep+"input"+os.sep+"items_tagged_modified.json"
    data=json.load(codecs.open(path_data, encoding='UTF-8'))
    
    from nltk.parse import stanford
    from nltk.parse.stanford import StanfordParser
    os.environ['STANFORD_PARSER'] = 'F:/eclipse_doctor/KnowledgeGraph/stanford-parser/stanford-parser.jar'
    os.environ['STANFORD_MODELS'] = 'F:/eclipse_doctor/KnowledgeGraph/stanford-parser/stanford-parser-3.7.0-models.jar'
    java_path = "C:/ProgramData/Oracle/Java/javapath"
    os.environ['JAVAHOME'] = java_path
    
    parser = stanford.StanfordParser(model_path="F:/eclipse_doctor/KnowledgeGraph/stanford-parser/englishPCFG.ser.gz")
    
    start = datetime.now()
    print start
    
    p=Pool()
    multiprocessing.freeze_support() 
    cpus = multiprocessing.cpu_count()
    lock =threading.Lock() 
    i=1
#     result=[]
    VBProd=[]
    while(i):
        if i<len(data)/cpus:
            if lock.acquire():
                for j in range(cpus):
                    print 'thread: ',i*cpus+j
                    trees=p.apply_async(test_parseDef,args=(data[i*cpus+j],parser))
                    VBProd.extend(getVBProd(trees))
                i+=1
                lock.release() 
        else:
            break
    p.close()
    p.join()
    
    end = datetime.now()
    print end
    print "cost time: "+str((end - start).seconds)   

#     for production in VBProd:
#         if production.lhs()


def getVBProd(trees):
    VBList=[]
    for tree in trees:
#         print tree
        productions=tree.productions()
        for production in productions:
            if str(production.lhs())=='VP':
                VBList.append(production)
    return VBList



def test_parseSent():
    import nltk
    from nltk.parse import stanford
    os.environ['STANFORD_PARSER'] = 'F:/eclipse_doctor/KnowledgeGraph/stanford-parser/stanford-parser.jar'
    os.environ['STANFORD_MODELS'] = 'F:/eclipse_doctor/KnowledgeGraph/stanford-parser/stanford-parser-3.7.0-models.jar'
    java_path = "C:/ProgramData/Oracle/Java/javapath"
    os.environ['JAVAHOME'] = java_path
    
    parser = stanford.StanfordParser(model_path="F:/eclipse_doctor/KnowledgeGraph/stanford-parser/englishPCFG.ser.gz")
    
    sent='It is utilized when the implant is at a different inclination in relation to the proposed prosthesis.'
    tokens=nltk.word_tokenize(sent)
    tree=parser.parse(tokens)
    tree=parser.parse(tokens)
    print list(tree)
#     print list(tree)
    for subtree in tree:
        print subtree

from colorama import Fore,init
init(autoreset=True)



def test_POSSent():
    import nltk
    from nltk.tag.stanford import StanfordPOSTagger
    java_path = "C:/ProgramData/Oracle/Java/javapath"
    os.environ['JAVAHOME'] = java_path
    tagger=StanfordPOSTagger('F:/eclipse_doctor/KnowledgeGraph/stanford-pos/english-bidirectional-distsim.tagger', 'F:/eclipse_doctor/KnowledgeGraph/stanford-pos/stanford-postagger-3.7.0.jar') 
    sent='abutment is a tooth, root, or implant used for support and retention of a fixed or removable prosthesis.'
    sent='angulated abutment is an abutment whose body is not parallel to the long axis of the implant. It is utilized when the implant is at a different inclination in relation to the proposed prosthesis.'
    sent=u'substance abuse is the misuse of legal or illegal substances with the intent to alter some aspect of the user閳ユ獨 experience. May include medications, illicit drugs, legal substances with potential mood-altering effects, or substances whose primary use may not be for human consumption.'
#     print chardet.detect(sent)
    tokens=nltk.word_tokenize(sent)
#     print tagger.tag(sent.split())
    print tagger.tag(tokens)

def tagMosby(path_data,path_out):
    import nltk
    from nltk.tag.stanford import StanfordPOSTagger
    java_path = "C:/ProgramData/Oracle/Java/javapath"
    os.environ['JAVAHOME'] = java_path
    tagger=StanfordPOSTagger('F:/eclipse_doctor/KnowledgeGraph/stanford-pos/english-bidirectional-distsim.tagger', 'F:/eclipse_doctor/KnowledgeGraph/stanford-pos/stanford-postagger-3.7.0.jar') 
    
#     path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
#     path_data= path_project+os.sep+"input"+os.sep+"items_tagged_modified.json"
#     path_data= path_project+os.sep+"input"+os.sep+"items_modified.json"

    data=json.load(codecs.open(path_data, encoding='UTF-8'))
    cnt=0
    for item in data:
        pos2definition=item["pos2definition"]
        cnt+=1
        print "process %dth definition" % cnt
        for pos2def in pos2definition:
            del pos2def["def_tagged"]
#             definition=pos2def["definition"]
#             definition_pure=re.sub(r'\([\s\S]*?\)', "", definition)
#             print definition_pure
#             text = nltk.word_tokenize(definition_pure)
# #             tag_tokens=[token[0].decode('utf-8').encode('gbk') for token in tagger.tag(text)]
#             pos2def['def_tagged']=str(tagger.tag(text))
#             sents_pos_period=cut_list(text, ['.'])
#             for sent_list in sents_pos_period:
#                 print sent_list
#                 logger.info(tagger.tag(sent_list))
#             logger.info('--------')
#         logger.info('~~~~~~~')
    path_tagged_output="items_modified_POS.json"
    json.dump(data, codecs.open(path_out, 'w','utf-8'),ensure_ascii=False,indent=2)
    
def parseMosby():
#     path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
#     path_data= path_project+os.sep+"input"+os.sep+"items_tagged_modified.json"
    path_data="F:/eclipse_doctor/KnowledgeGraph/kg/books/extractor/data/items_modified.json"
    data=json.load(codecs.open(path_data, encoding='UTF-8'))
    
    import nltk
    from nltk.parse import stanford
    from nltk.parse.stanford import StanfordParser
    os.environ['STANFORD_PARSER'] = 'F:/eclipse_doctor/KnowledgeGraph/stanford-parser/stanford-parser.jar'
    os.environ['STANFORD_MODELS'] = 'F:/eclipse_doctor/KnowledgeGraph/stanford-parser/stanford-parser-3.7.0-models.jar'
    java_path = "C:/ProgramData/Oracle/Java/javapath"
    os.environ['JAVAHOME'] = java_path
    
    parser = stanford.StanfordParser(model_path="F:/eclipse_doctor/KnowledgeGraph/stanford-parser/englishPCFG.ser.gz")
    cnt=0
    for item in data:
        print "parse %dth item"%cnt
        cnt+=1
        if cnt<4686:
            continue
        pos2definition=item["pos2definition"]
        for pos2def in pos2definition:
            definition=pos2def["definition"]
            definition_pure=re.sub(r'\([\s\S]*?\)', "", definition)
            text = nltk.word_tokenize(definition_pure)
            sents_pos_period=cut_list(text, ['.'])
            for sent_list in sents_pos_period:
#                 print list(parser.parse(sent_list))
                logger.info(list(parser.parse(sent_list)))
            logger.info('--------')   
        logger.info('~~~~~~~')
        
        
def item_replace(path_data1,path_data2,path_out):
    data=json.load(codecs.open(path_data1, encoding='UTF-8'))
    cnt=0
    for item in data:
        pos2definition=item["pos2definition"]

def biSearch(L,item):
    left=0
    right=len(L)-1
    while left<=right:
        mid=(left+right)/2
        if item["concept"]==L(mid)["concept"]:
            return mid
        elif item["concept"]<L(mid)["concept"]:
            right=mid-1
        else:
            left=mid+1
    return -1

def test():
    import wget
    wget.download("http://music.baidu.com/song/100575177","D://")
    
if __name__ == '__main__':
    
#     test_extactVerbGroup()
#     test_PennCorpus()
#     test_GrammarParser()
#     test_list_copy()
#     test_VB()
#     test_VBMosby()
#     test_ItemFirstTwoWords()
#     test_VBBrown()
#     test_Phrase()
#     getProductions('PP')
#     test_parser()
#     test_multiThread()

    test_parseSent()
#     test_POSSent()
#     POSMosby()

#     test_parseSent()
#     path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
#     path_data1= path_project+os.sep+"input"+os.sep+"items_tagged_modified_POS.json"
# #     path_data1= path_project+os.sep+"input"+os.sep+"items_modified_test.json"
#     path_data2= path_project+os.sep+"input"+os.sep+"items_modified_POS.json"
# #     path_data2= path_project+os.sep+"input"+os.sep+"items_modified_test.json"
#     path_output1="items_tagged_modified_no_POS.json"
#     path_output2="items_modified_no_POS.json"
#     tagMosby(path_data1,path_output1)
#     tagMosby(path_data2,path_output2)
#     test()
#     parseMosby()
