#coding=utf-8
'''
Created on 2016年11月2日

@author: feifei
'''

import unittest 
import kg.util.segment
from kg.util import segment

class mytest(unittest.TestCase):
    
    def setUp(self):
        unittest.TestCase.setUp(self)
    
    def tearDown(self):
        unittest.TestCase.tearDown(self)
    
    def test_extract_n_gram(self):
        str="""邻牙无明显倾斜，近远中间隙约6mm,对颌牙无明显过长，
        合龈距约10mm种植术前检查下额CBCT：处牙槽嵴顶宽度6mm，骨高度明显低于邻牙，（嵴顶距下颌神经管）约8-10mm，骨质密度尚可，下颌舌骨后窝凹陷不明显 。
        口腔卫生状况一般。血常规检查未见明显异常。"""
        str_before="""检查：缺失，牙槽嵴中度吸收，粘膜无红肿，嵴顶颊舌侧角化龈宽度约6mm。"""
        str_after=["检查","缺失","牙槽嵴中度吸收","粘膜无红肿","嵴顶颊舌侧角化龈宽度约6mm"]
        self.assertEqual(segment.cut_sentence(str_before), str_after, "test cut_sentence fail")
        
        
        
if __name__ =='__main__':  
    unittest.main() 