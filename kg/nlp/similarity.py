#coding=utf-8
'''
Created on 2017��4��8��

@author: FeiFei
'''


def cosineSimilarity (vec1, vec2):
    import numpy as np
    from numpy import linalg as la
    
    intA = np.mat(vec1) 
    intB = np.mat(vec2)
    num = float(intA * intB.T) #若为行向量: A * B.T
    donom = la.norm(intA) * la.norm(intB) ##余弦值 
    return 0.5+ 0.5*(num / donom) # 归一化
    #关于归一化：因为余弦值的范围是 [-1,+1] ，相似度计算时一般需要把值归一化到 [0,1]

def euclidSimilar(inA, inB):
    import numpy as np
    from numpy import linalg as la
    
    return 1.0/(1.0+la.norm(inA-inB)) 
    # 归一化：在欧氏距离公式中，取值范围会很大，所以用上式归一化。

