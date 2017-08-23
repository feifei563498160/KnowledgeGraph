#coding=utf-8
'''
Created on 2017��4��28��

@author: FeiFei
'''

import wx
class TwoButtonEvent(wx.PyCommandEvent): #1 定义事件
    def __init__(self, evtType, id):
        wx.PyCommandEvent.__init__(self, evtType, id)
        self.clickCount = 0
    def GetClickCount(self):
        return self.clickCount
    def SetClickCount(self, count):
        self.clickCount = count
        
myEVT_TWO_BUTTON = wx.NewEventType() #2 创建一个事件类型
EVT_TWO_BUTTON = wx.PyEventBinder(myEVT_TWO_BUTTON, 1) #3 创建一个绑定器对象

class TwoButtonPanel(wx.Panel):
    def __init__(self, parent, id=-1, leftText="Left",rightText="Right"):
        wx.Panel.__init__(self, parent, id)
        self.leftButton = wx.Button(self, label=leftText)
        self.rightButton = wx.Button(self, label=rightText,
        pos=(100,0))
        self.leftClick = False
        self.rightClick = False
        self.clickCount = 0
        #4 下面两行绑定更低级的事件
        self.leftButton.Bind(wx.EVT_LEFT_DOWN, self.OnLeftClick)
        self.rightButton.Bind(wx.EVT_LEFT_DOWN, self.OnRightClick)
    def OnLeftClick(self, event):
        self.leftClick = True
        self.OnClick()
        event.Skip() #5 继续处理
        72 / 565
    def OnRightClick(self, event):
        self.rightClick = True
        self.OnClick()
        event.Skip() #6 继续处理
    def OnClick(self):
        self.clickCount += 1
        if self.leftClick and self.rightClick:
            self.leftClick = False
            self.rightClick = False
            evt = TwoButtonEvent(myEVT_TWO_BUTTON, self.GetId()) #7 创建自定 义事件
            evt.SetClickCount(self.clickCount) # 添加数据到事件
            self.GetEventHandler().ProcessEvent(evt) #8 处理事件
            
class CustomEventFrame(wx.Frame):
    def __init__(self, parent, id):
        wx.Frame.__init__(self, parent, id, 'Click Count: 0',size=(300, 100))
        panel = TwoButtonPanel(self)
        self.Bind(EVT_TWO_BUTTON, self.OnTwoClick, panel) #9 绑定自定义事件

    def OnTwoClick(self, event): #10 定义一个事件处理器函数
        self.SetTitle("Click Count: %s" % event.GetClickCount())
        
if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = CustomEventFrame(parent=None, id=-1)
    frame.Show()
    app.MainLoop()
        
        
        
        