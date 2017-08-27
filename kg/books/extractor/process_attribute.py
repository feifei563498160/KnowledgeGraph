#encoding=utf-8
'''
Created on 2017��8��25��

@author: FeiFei
'''
import xlrd
import os
import codecs
import json
inpath='sources'+os.sep+'schemas.xlsx'

data=xlrd.open_workbook(inpath)
table=data.sheets()[0]
nrows = table.nrows

data_patterns=[]

type_line_num=[]
for i in range(1,nrows):
    attri_name=table.cell(i,5).value
    if nrows==None:
        break
    if attri_name=='':
        type_line_num.append(i)

for i in range(len(type_line_num)):
    item={}
    if i<len(type_line_num)-1:
        cate=''
        if table.cell(type_line_num[i],3).value!='':
            cate=table.cell(type_line_num[i],3).value
        elif table.cell(type_line_num[i],2).value!='':
            cate=table.cell(type_line_num[i],2).value
        elif table.cell(type_line_num[i],1).value!='':
            cate=table.cell(type_line_num[i],1).value
        elif table.cell(type_line_num[i],0).value!='':
            cate=table.cell(type_line_num[i],0).value
        
        item_attri={}   
        des_CN=table.cell(type_line_num[i],7).value
        des_EG=table.cell(type_line_num[i],8).value
        item_attri["description_CN"]=des_CN
        item_attri["description_EG"]=des_EG
        attri={}
        for j in range(type_line_num[i]+1,type_line_num[i+1]):
            attri_name=table.cell(j,5).value
            type_=table.cell(j,6).value
            des_CN=table.cell(j,7).value
            des_EG=table.cell(j,8).value
            attri_dic={}
            attri_dic['type']=type_
            attri_dic['description_CN']=des_CN
            attri_dic['description_EG']=des_EG
            l1=[]
            attri_dic["patterns"]=l1
            attri[attri_name]=attri_dic
        
        item_attri["attributes"]=attri
        item[cate]=item_attri
        data_patterns.append(item)
        
path_out='patterns_new.json'   
json.dump(data_patterns, codecs.open(path_out, 'w','utf-8'),ensure_ascii=False,indent=2)   
    
    