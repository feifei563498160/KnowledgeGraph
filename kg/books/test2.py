#coding=utf-8
'''
Created on 2017��6��20��

@author: FeiFei
'''
import os
import re
from kg.books.extract_dental_items import logger

def test_POSSent():
    import nltk
    from nltk.tag.stanford import StanfordPOSTagger
    java_path = "C:/ProgramData/Oracle/Java/javapath"
    os.environ['JAVAHOME'] = java_path
    tagger=StanfordPOSTagger('F:/eclipse_doctor/KnowledgeGraph/stanford-pos/english-bidirectional-distsim.tagger', 'F:/eclipse_doctor/KnowledgeGraph/stanford-pos/stanford-postagger-3.7.0.jar') 
    sent='abutment is a tooth, root, or implant used for support and retention of a fixed or removable prosthesis.'
    sent="substance abuse is the misuse of legal or illegal substances with the intent to alter some aspect of the user's experience"
    sent="trust is a relationship in which one person or entity holds fiduciary responsibility for another's property or enterprise"
    sent="mitotic activity-cells"
    sent="learning domains is the three spheres of learning-cognitive , affective , and psychomotor-that must be addressed by a teacher so as to influence behavioral change on the part of the learner"
    sent=u"inhibits α-glucosidase enzyme in the GI tract to slow the breakdown of carbohydrates to glucose"
    sent=u"α"
    text=nltk.word_tokenize(sent.encode('gb2312'))
    print tagger.tag(text)
    print tagger.tag(sent.split())
    logger.info(tagger.tag(text))
    logger.info(tagger.tag(sent.split()))
    
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

def main():
    path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
    path_data= path_project+os.sep+"input"+os.sep+"Mosby_Tag.txt" 
    lines=open(path_data,'r').readlines()
    items_tagged=getTaggedSent(lines)
    for item in items_tagged:
        print item
        
if __name__=='__main__':
#     test_POSSent()
    POSListString="[(u\"'s\", u'POS'), (u'experience', u'NN')]"
    print tagfromstring(POSListString)
#     main()
    