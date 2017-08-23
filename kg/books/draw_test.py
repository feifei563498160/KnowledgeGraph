#coding=utf-8
'''
Created on 2017��4��11��

@author: FeiFei
'''
import matplotlib.pyplot as plt
import numpy as np

def draw(col_labels,row_labels,table_vals):
    ncol = len(col_labels)
    nrow = len(row_labels)
    # draw grid lines
    plt.plot(np.tile([0, ncol+1], 
            (nrow+2,1)).T, 
            np.tile(np.arange(nrow+2), 
            (2,1)),
            'k', linewidth=3)
            
    plt.plot(np.tile(np.arange(ncol+2), 
            (2,1)), 
            np.tile([0, nrow+1], 
            (ncol+2,1)).T,
            'k', linewidth=3)

    # plot labels
    for icol, col in enumerate(col_labels):
        plt.text(icol + 1.5, 
                 nrow + 0.5, 
                 col, 
                 ha='center',
                 va='center')
#                      fontproperties=myfont)
    for irow, row in enumerate(row_labels):
        plt.text(0.5, 
                 nrow - irow - 0.5, 
                 row, 
                 ha='center', 
                 va='center')
#                      fontproperties=myfont)

    # plot table content
    for irow, row in enumerate(table_vals):
        for icol, cell in enumerate(row):
            plt.text(icol + 1.5, 
                     nrow - irow - 0.5, 
                     cell, 
                     ha='center', 
                     va='center')
#                          fontproperties=myfont)
    plt.axis([-0.5, ncol + 1.5, -0.5, nrow+1.5])
    plt.axis('off')  #不显示坐标
    plt.show()
#         plt.savefig(u'./xxx.png')
    plt.close('all')

if __name__ == '__main__':
    col_labels=[u'本次名次',u'上次名次',u'进步名次']
    row_labels=['Luc']
    table_vals=[]
    table_vals.append([1,10,9])
    draw(col_labels,row_labels,table_vals)
#     myfont = matplotlib.font_manager.FontProperties(fname=’/Library/Fonts/华文仿宋.ttf’)
