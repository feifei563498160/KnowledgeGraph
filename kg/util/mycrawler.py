#encoding=utf-8
'''
Created on 2016年11月4日

@author: feifei
'''

import kg.util.mylogger
from kg.util import mylogger
import os


def test(log_path,mylogger1):
    mylogger1.info("this is a test")
# logger_mycrawler.debug("test debug")
# logger_mycrawler.info("test info")
# logger_mycrawler.warning("test warning")

if __name__=="__main__":
    path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
    log_path = path_project+'/tmp/log'
    logger_mycrawler=mylogger.log_console_and_file(log_path)

    test(log_path,logger_mycrawler)
