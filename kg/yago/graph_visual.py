#coding=utf-8
'''
Created on 2016��12��14��

@author: feifei
'''
from py2neo import Graph
from py2neo import Node, Relationship
from kg.util import db





def create_node():
    
    pass

def create_relation():
    conn=db.get_conn()
    cursor=conn.cursor()
    sql="select subject,predicate,object from extract_facts2;"
    cursor.execute(sql)
    rows=cursor.fetchall()
    graph=Graph("http://localhost:7474", username="neo4j", password="19920201")
    graph.delete_all()
    for row in rows:
#         subject=row[0].replace("<","").replace(">","").strip().lower()
        subject=row[0].strip()
        predicate=row[1].strip()
        object_=row[2].strip()
#         object_=row[2].replace('"','').replace("@eng","").strip().lower()
        node1=Node(subject)
        node2=Node(object_)
        link=predicate
        node1_link_node2=Relationship(node1,link,node2)
        graph.create(node1_link_node2)
    conn.commit()
    cursor.close()
    conn.close()

    
def visualization():
    pass
   
def test(): 
    from py2neo import Node, Relationship
    from py2neo import Graph
    graph=Graph("http://localhost:7474", username="neo4j", password="19920201")
    graph.delete_all()
    
    zhangyimou=Node("Person",name="Zhang Yimou")
    zhangyimou.properties["age"]=65
    gongli=Node("Person",name="Gong Li")
    gongli_isMarriedTo_zhangyimou=Relationship(gongli,"isMarriedTo",zhangyimou)
    graph.create(gongli_isMarriedTo_zhangyimou)

    graph.create(gongli_isMarriedTo_zhangyimou)
    xian=Node("City",name="Xi'an")
    zhangyimou_wasBornIn_xian=Relationship(zhangyimou,"wasBornIn",xian)
    graph.create(zhangyimou_wasBornIn_xian)
    
    prize=Node("Prize",name="Silver Lion")
    zhangyimou_won_prize=Relationship(zhangyimou,"hasWonPrize",prize)
    graph.create(zhangyimou_won_prize)
if __name__=="__main__":
#     create_relation()
#     graph=Graph("http://localhost:7474", username="neo4j", password="19920201")
#     graph.delete_all()
    test()