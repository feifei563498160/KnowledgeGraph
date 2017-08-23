#coding=utf-8
'''
Created on 2017��4��12��

@author: FeiFei
'''


class Pattern:
    '''
    TokenString: '{NN}+after'
    TokenList: ['{NN}','after']
    TokenFix: [('process','NN'),('after','IN')]
    TokenWindow: [(u'from', 'IN'),(u'the', 'DT'),(u'alveolar', 'JJ'),(u'process', 'NN'),(u'after'
, 'IN')]
    '''
    TokenString=''
    TokenList=[]
    TokenFix=[]
    TokenWindow=[]
    shift=0
    priority=0.0
    freq=0
    
    
    
class Token:
    word=''
    pos=''
    support_degree=0
    def __init__(self,word,pos,support_degree=0):
        self.word=word
        self.pos=pos
        self.support_degree=support_degree

    def get_word(self):
        return self.__word


    def get_pos(self):
        return self.__pos


    def get_support_degree(self):
        return self.__support_degree


    def set_word(self, value):
        self.__word = value


    def set_pos(self, value):
        self.__pos = value


    def set_support_degree(self, value):
        self.__support_degree = value


    def del_word(self):
        del self.__word


    def del_pos(self):
        del self.__pos


    def del_support_degree(self):
        del self.__support_degree
        
    
    def equal(self,token):
        if self.word==token.word and self.pos==token.pos:
            return True
        return False
    def equal_word(self,token):
        if self.word==token.word:
            return True
        return False
    
    def show(self):
        return (self.word,self.pos)
        
    word = property(get_word, set_word, del_word, "word's docstring")
    pos = property(get_pos, set_pos, del_pos, "pos's docstring")
    support_degree = property(get_support_degree, set_support_degree, del_support_degree, "support_degree's docstring")

class Item:
    
    pronunciation=''
    concept=''
    pos2definition=[]
    
    def __init__(self, pronunciation, concept, pos2definition):
        self.pronunciation = pronunciation
        self.concept = concept
        self.pos2definition = pos2definition

    def get_pronunciation(self):
        return self.__pronunciation


    def get_concept(self):
        return self.__concept


    def get_pos_2definition(self):
        return self.__pos2definition


    def set_pronunciation(self, value):
        self.__pronunciation = value


    def set_concept(self, value):
        self.__concept = value


    def set_pos_2definition(self, value):
        self.__pos2definition = value


    def del_pronunciation(self):
        del self.__pronunciation


    def del_concept(self):
        del self.__concept


    def del_pos_2definition(self):
        del self.__pos2definition

    pronunciation = property(get_pronunciation, set_pronunciation, del_pronunciation, "pronunciation's docstring")
    concept = property(get_concept, set_concept, del_concept, "concept's docstring")
    pos2definition = property(get_pos_2definition, set_pos_2definition, del_pos_2definition, "pos2definition's docstring")

    

class Definition:

    definition=''
    pos=''
    attributes=[]
    
    def __init__(self, definition, pos, attributes):
        self.definition = definition
        self.pos = pos
        self.attributes = attributes

    def get_definition(self):
        return self.__definition


    def get_pos(self):
        return self.__pos


    def get_attributes(self):
        return self.__attributes


    def set_definition(self, value):
        self.__definition = value


    def set_pos(self, value):
        self.__pos = value


    def set_attributes(self, value):
        self.__attributes = value


    def del_definition(self):
        del self.__definition


    def del_pos(self):
        del self.__pos


    def del_attributes(self):
        del self.__attributes

    definition = property(get_definition, set_definition, del_definition, "definition's docstring")
    pos = property(get_pos, set_pos, del_pos, "pos's docstring")
    attributes = property(get_attributes, set_attributes, del_attributes, "attributes's docstring")


