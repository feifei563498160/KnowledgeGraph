#coding=utf-8
'''
Created on 2016��11��28��

@author: feifei
'''
# from PyPDF2 import PdfFileReader, PdfFileWriter
# 
# infn = 'infn.pdf'
# outfn = 'outfn.pdf'
# # 获取一个 PdfFileReader 对象
# pdf_input = PdfFileReader(open(infn, 'rb'))
# # 获取 PDF 的页数
# page_count = pdf_input.getNumPages()
# print(page_count)
# # 返回一个 PageObject
# page = pdf_input.getPage(i)
# 
# # 获取一个 PdfFileWriter 对象
# pdf_output = PdfFileWriter()
# # 将一个 PageObject 加入到 PdfFileWriter 中
# pdf_output.addPage(page)
# # 输出到文件中
# pdf_output.write(open(outfn, 'wb'))


from PyPDF2 import PdfFileReader, PdfFileWriter

def split_pdf(infn, outfn):
    pdf_output = PdfFileWriter()
    pdf_input = PdfFileReader(open(infn, 'rb'))
    # 获取 pdf 共用多少页
    page_count = pdf_input.getNumPages()
    print(page_count)
    # 将 pdf 第五页之后的页面，输出到一个新的文件
    for i in range(0, page_count):
        pdf_output.addPage(pdf_input.getPage(i))
    pdf_output.write(open(outfn, 'wb'))

def merge_pdf(infnList, outfn):
    pdf_output = PdfFileWriter()
    for infn in infnList:
        pdf_input = PdfFileReader(open(infn, 'rb'))
        # 获取 pdf 共用多少页
        page_count = pdf_input.getNumPages()
        print(page_count)
        for i in range(page_count):
            pdf_output.addPage(pdf_input.getPage(i))
    pdf_output.write(open(outfn, 'wb'))

def extract_pdf(infn, outfn):
    pdf_output = PdfFileWriter()
    pdf_input = PdfFileReader(open(infn, 'rb'))
    # 获取 pdf 共用多少页
    page_count = pdf_input.getNumPages()
    # 将 pdf 第五页之后的页面，输出到一个新的文件
    content=''
    for i in range(0, page_count):
        print 'i= ',i
        print pdf_input.getPage(i).extractText()
#         print pdf_input.getPage(i).extractText().split()
        content +=pdf_input.getPage(i).extractText()
#     print pdf_input.getPage(0).extractText()
#     content = u" ".join(content.replace(u"\xa0", u" ").strip().split())
    print content
     
if __name__ == '__main__':
    infn = './Mosby.pdf'
    outfn = './test_text.txt'
    extract_pdf(infn, outfn)
