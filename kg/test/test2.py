#coding=utf-8
'''
Created on 2017��7��8��

@author: FeiFei
'''
# from echarts import Echart, Legend, Bar, Axis
# chart = Echart('GDP', 'This is a fake chart')
# chart.use(Bar('China', [2, 3, 4, 5]))
# chart.use(Legend(['GDP']))
# chart.use(Axis('category', 'bottom', data=['Nov', 'Dec', 'Jan', 'Feb']))
# chart.plot()

from echarts import Echart, Legend, Bar, Axis, Pie
chart = Echart('Map Picks in MLG', 'In group A')
chart.use(Pie('Map Picks in MLG', 
              [{'value': 2, 'name': 'de_dust2'},
               {'value': 3, 'name': 'de_cache'},
               {'value': 12, 'name': 'de_mirage'},
               {'value': 9, 'name': 'de_inferno'}
              ],
            radius=["50%", "70%"])
         )
chart.use(Legend(["de_dust2", "de_cache", "de_mirage", "de_inferno"]))
del chart.json["xAxis"]
del chart.json["yAxis"]
chart.plot()