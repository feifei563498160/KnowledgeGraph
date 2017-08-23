#coding=utf-8
'''
Created on 2016年12月22日

@author: feifei
'''
import os
import sys
from binascii import b2a_hex

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument, PDFNoOutlines,\
    PDFTextExtractionNotAllowed
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTFigure, LTImage, LTChar
from pdfminer.pdfdevice import PDFDevice

def gain_index():
    path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
    path_book = path_project+os.sep+"input"+os.sep+"Contemporary Fixed Prosthodontics, 5ed.pdf"
   
    # Open a PDF document.
    fp = open(path_book, 'rb')
    parser = PDFParser(fp)
    document = PDFDocument(parser)
    
    # Get the outlines of the document.
    outlines = document.get_outlines()
    cnt=0
    for (level,title,dest,a,se) in outlines:
        if cnt<10:
            print (level, title)
            cnt+=1
        else:
            break
        
def main():
    path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
    path_book = path_project+os.sep+"input"+os.sep+"Contemporary Fixed Prosthodontics, 5ed.pdf"
    path_pdf_out = path_project+os.sep+"output"+os.sep+"pdf_result"
    # Open a PDF file.
    fp = open(path_book, 'rb')
    # Create a PDF parser object associated with the file object.
    parser = PDFParser(fp)
    # Create a PDF document object that stores the document structure.
    # Supply the password for initialization.
    document = PDFDocument(parser)
    # Check if the document allows text extraction. If not, abort.
    if not document.is_extractable:
        raise PDFTextExtractionNotAllowed
    # Create a PDF resource manager object that stores shared resources.
    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    # Create a PDF device object.
    device = PDFDevice(rsrcmgr, laparams=laparams)
    # Create a PDF interpreter object.
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    # Process each page contained in the document.
    
    cnt =0
    for page in PDFPage.create_pages(document):
        if cnt<10:
            interpreter.process_page(page)
            layout = device.get_result()
            
            cnt+=1
        else:
            break
   
   
def with_pdf(path_book,images_folder):
    fp = open(path_book, 'rb')
    parser = PDFParser(fp)
    document = PDFDocument(parser)
    if not document.is_extractable:
        raise PDFTextExtractionNotAllowed
    rsrcmgr = PDFResourceManager()
#     laparams = LAParams()
#     device = PDFDevice(rsrcmgr, laparams=laparams)
    device = PDFDevice(rsrcmgr)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    text_content = []
    for i, page in enumerate(PDFPage.create_pages(document)):
        interpreter.process_page(page)
        # receive the LTPage object for this page
        layout = device.get_result()
        text_content.append(parse_lt_objs(layout, (i+1), images_folder))
    return text_content

def parse_lt_objs(lt_objs, page_number, images_folder, text=[]):
    """Iterate through the list of LT* objects and capture the text or image data contained in each"""
    text_content = [] 

    page_text = {} # k=(x0, x1) of the bbox, v=list of text strings within that bbox width (physical column)
    for lt_obj in lt_objs:
        if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
            # text, so arrange is logically based on its column width
            page_text = update_page_text_hash(page_text, lt_obj)
            print page_text
        elif isinstance(lt_obj, LTImage):
            # an image, so save it to the designated folder, and note its place in the text 
            saved_file = save_image(lt_obj, page_number, images_folder)
            if saved_file:
                # use html style <img /> tag to mark the position of the image within the text
                text_content.append('<img src="'+os.path.join(images_folder, saved_file)+'" />')
            else:
                print >> sys.stderr, "error saving image on page", page_number, lt_obj.__repr__
        elif isinstance(lt_obj, LTFigure):
            # LTFigure objects are containers for other LT* objects, so recurse through the children
            text_content.append(parse_lt_objs(lt_obj, page_number, images_folder, text_content))

    for k, v in sorted([(key,value) for (key,value) in page_text.items()]):
        # sort the page_text hash by the keys (x0,x1 values of the bbox),
        # which produces a top-down, left-to-right sequence of related columns
        text_content.append(''.join(v))

    return '\n'.join(text_content)
    
def update_page_text_hash (h, lt_obj, pct=0.2):
    """Use the bbox x0,x1 values within pct% to produce lists of associated text within the hash"""

    x0 = lt_obj.bbox[0]
    x1 = lt_obj.bbox[2]

    key_found = False
    for k, v in h.items():
        hash_x0 = k[0]
        if x0 >= (hash_x0 * (1.0-pct)) and (hash_x0 * (1.0+pct)) >= x0:
            hash_x1 = k[1]
            if x1 >= (hash_x1 * (1.0-pct)) and (hash_x1 * (1.0+pct)) >= x1:
                # the text inside this LT* object was positioned at the same
                # width as a prior series of text, so it belongs together
                key_found = True
                v.append(to_bytestring(lt_obj.get_text()))
                h[k] = v
    if not key_found:
        # the text, based on width, is a new series,
        # so it gets its own series (entry in the hash)
        h[(x0,x1)] = [to_bytestring(lt_obj.get_text())]

    return h

def to_bytestring (s, enc='utf-8'):
    """Convert the given unicode string to a bytestring, using the standard encoding,
    unless it's already a bytestring"""
    if s:
        if isinstance(s, str):
            return s
        else:
            return s.encode(enc)
        
          
def save_image (lt_image, page_number, images_folder):
    """Try to save the image data from this LTImage object, and return the file name, if successful"""
    result = None
    if lt_image.stream:
        file_stream = lt_image.stream.get_rawdata()
        if file_stream:
            file_ext = determine_image_type(file_stream[0:4])
            if file_ext:
                file_name = ''.join([str(page_number), '_', lt_image.name, file_ext])
                if write_file(images_folder, file_name, file_stream, flags='wb'):
                    result = file_name
    return result
 
def determine_image_type (stream_first_4_bytes):
    """Find out the image file type based on the magic number comparison of the first 4 (or 2) bytes"""
    file_type = None
    bytes_as_hex = b2a_hex(stream_first_4_bytes)
    if bytes_as_hex.startswith('ffd8'):
        file_type = '.jpeg'
    elif bytes_as_hex == '89504e47':
        file_type = '.png'
    elif bytes_as_hex == '47494638':
        file_type = '.gif'
    elif bytes_as_hex.startswith('424d'):
        file_type = '.bmp'
    return file_type

def write_file (folder, filename, filedata, flags='w'):
    """Write the file data to the folder and filename combination
    (flags: 'w' for write text, 'wb' for write binary, use 'a' instead of 'w' for append)"""
    result = False
    if os.path.isdir(folder):
        try:
            file_obj = open(os.path.join(folder, filename), flags)
            file_obj.write(filedata)
            file_obj.close()
            result = True
        except IOError:
            pass
    return result

def extract_outlines(path):
    from pdfminer.pdfparser import PDFParser
    from pdfminer.pdfdocument import PDFDocument

    # Open a PDF document.
    fp = open(path, 'rb')
    parser = PDFParser(fp)
    document = PDFDocument(parser)

    # Get the outlines of the document.
    outlines = document.get_outlines()
    for (level,title,dest,a,se) in outlines:
        print (level, title)
        
if __name__=="__main__":
#     main()
#     gain_index()
    path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
    path_book = path_project+os.sep+"input"+os.sep+"Contemporary Fixed Prosthodontics, 5ed.pdf"
#     image_folder=path_project+os.sep+"input"+os.sep+"pdf_inages"+os.sep
#     with_pdf(path_book, image_folder)
    extract_outlines(path_book)


