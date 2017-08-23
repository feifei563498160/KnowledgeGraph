#coding=utf-8
'''
Created on 2017��1��12��

@author: feifei
'''
import os
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument

path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
path_book = path_project+os.sep+"input"+os.sep+"McCrackens Removable Partial Prosthodontics_nodrm.pdf"
path_out = path_project+os.sep+"output"+os.sep+"Contemporary Fixed Prosthodontics, 5ed index.txt"

# Open a PDF document.
fp = open(path_book, 'rb')
parser = PDFParser(fp)
document = PDFDocument(parser)

# Get the outlines of the document.
outlines = document.get_outlines()
with open(path_out,"w") as f:
    for (level,title,dest,a,se) in outlines:
        f.write(title.encode("utf-8")+"\n")
print "over"