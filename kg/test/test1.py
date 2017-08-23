#coding=utf-8
'''
Created on 2017��7��8��

@author: FeiFei
'''

# users=["1","2"]
# print raw_input("hduh") in users
# 
# [].sort(cmp=None, key=None, reverse=False)

def func(x,y):
    return x+y

def test(f,a,b,c):
    print 'test'
    print f(a, b)
    print f(a,c)
    print f(b,c)
    
test(func, 3, 5, 7)
array = [1,2,3,6,5,4]

def sort_mp(array):
    for i in range(len(array)):
        for j in range(i):
            if array[j] > array[j + 1]:
                array[j], array[j + 1] = array[j + 1], array[j]
    return array

def cmp_mp(array_i,array_j):
    if array_i> array_j:
        return 1
    elif  array_i< array_j:
        return -1
    else:
        return 0
    
def sort_mp2(cmp_mp,array):
    for i in range(len(array)):
        for j in range(i):
            if cmp_mp(array[j],array[j + 1])==1:
                array[j], array[j + 1] = array[j + 1], array[j]
    return array
