#encoding=utf-8
'''
Created on 2017��8��21��

@author: FeiFei
'''
from platform import node

class Node(object):
    def __init__(self,label=-1,value=-1):
        self.label=label
        self.value=value
        self.children=[]
    
    def getValue(self):
        return self.value
    
    def getLabel(self):
        return self.label
    
    def getChildren(self):
        return self.children
    
    def add(self,node):
        self.children.append(node)
        
        
# class Tree(object):
#     def __init__(self):
#         self.root=Node()
#         
#     def linktohead(self, node):
#         self.root.add(node)
#         
# #     def getLeaf(self):
#     def getRootLabel(self):
#         return self.root.getLabel()
#     
#     def getRootValue(self):
#         return self.root.getValue()
#     
#     def getChrildren(self):
#         return self.root.getChildren()
#     
def pre_order(tree):   
    if  tree==None:
        return
    
    print tree.getRootLabel(),tree.getRootValue()
    if isLeaf(tree)==False:
        for subtree in tree.getChrildren():
            pre_order(subtree)
    
def isLeaf(tree):
    if tree.getChrildren()==[]:
        return True
    return False


class Tree(object):
    # 初始化，传入根节点的值
    def __init__(self, root_value):
        self.root = root_value
        self.children = []
        
    def insert(self,value):
        if self.children==None:
            self.children=Tree(value)
        else:
            sub_tree=Tree(value)
            
    def set_root(self,root_value):    
        self.root = root_value
        
    def get_root(self):
        return self.root    
     
    def get_children(self):
        return self.children
    
if __name__=='__main__':
#     node0=Node(0,'a')
#     node1=Node(1,'b')
#     node2=Node(2,'c')
#     node3=Node(3,'d')
#     node4=Node(4,'e')
#     
#     node0.add(node1)
#     node0.add(node2)
#     node1.add(node3)
#     node1.add(node4)
#     
#     tree=Tree()
#     tree.linktohead(node0)
    tree1=Tree(1).insert(2)
    tree2=Tree(3).insert(4)
    tree3=Tree(3).insert(tree1)
    pre_order(tree3)
#     print tree
    
    