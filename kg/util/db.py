#coding=utf-8
'''
Created on 2016年12月7日

@author: feifei
'''

import os
import sys
import psycopg2
import time

class DB:
    
    def __init__(self,database="yago", user="postgres", password="19920201", host="localhost", port="5432"):
        self.database=database
        self.user=user
        self.password=password
        self.host=host
        self.port=port
      
    def connectSQL(self):
        conn = psycopg2.connect(database=self.database, user=self.user, password=self.password, host=self.host, port=self.port)
        print "connection time: "+time.strftime('%Y-%m-%d;%H-%M-%S',time.localtime(time.time()))
        return conn

#     def operate(self,sql):
#         conn=self.connectSQL()
#         cursor = conn.cursor()
#         cursor.execute(sql)
#         conn.commit()
#         conn.close()

def get_conn():
    return DB().connectSQL()

if __name__=='__main__':    
    conn=DB().connectSQL()
    cursor=conn.cursor()
    sql="select * from yagofacts limit 100;"
    cursor.execute(sql)
    rows=cursor.fetchall()
    print type(rows[0])
    conn.commit()
    cursor.close()
    conn.close()
      
    
    