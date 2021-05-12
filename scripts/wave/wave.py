import sys
from PyQt5.QtWidgets import QMainWindow, QFrame, QApplication, QLabel, QHBoxLayout
from PyQt5.QtCore import QTimer
from PyQt5 import QtGui
import pyqtgraph as pg
import numpy as np

class Plugin():
    def __init__(self):
        super().__init__()

    def setUpUI(self, gridLayout):
        """设置frame上的UI，GUI程序提供一个空白的QFrame对象，所有展示程序都在该Frame上进行

        Args:
            frame (QFrame): 展示程序的画布
        """
        self._pgLayout = pg.GraphicsLayoutWidget(border=(100,100,100))
        gridLayout.addWidget(self._pgLayout,0,0)
        self._pgLayout.addLabel("长波近似下的声学波",col=0, colspan=4)
        self._pgLayout.nextRow()
        self._p1 = self._pgLayout.addPlot(title = "波动动画")
        self._p1.hideAxis("left")
        self._p2 = self._pgLayout.addPlot(title = "某点的振动图像")
        self._pgLayout.nextRow()
        self._pgLayout.addLabel("长波近似下的光学波",col=0, colspan=4)
        self._pgLayout.nextRow()
        self._p3 = self._pgLayout.addPlot(title = "波动动画")
        self._p3.hideAxis("left")
        self._p4 = self._pgLayout.addPlot(title = "某点的振动图像")
        #质量设置按钮
        self._spinBox = pg.SpinBox(value=1, bounds=[0.5, 2], step=0.1)
        self._spinBox.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self._spinBox.valueChanged.connect(self._valueChangedHandle)
        hBox = QHBoxLayout()
        hBox.addStretch(1)
        label = QLabel()
        label.setText("M(红):m(蓝)：")
        hBox.addWidget(label)
        hBox.addWidget(self._spinBox)
        gridLayout.addLayout(hBox,1,0)
        #常数定义
        self._m = 1
        self._M = 1  
        self._a = 50
        self._b = 15
        self._q = 1
        self._omega = np.pi/8
        self._A = self._a/10


    def run(self):
        """启动展示程序
        """
        self._time = 0 
        self._xMSoundByT = []
        self._xmSoundByT = []
        self._xMOpticByT = []
        self._xmOpticByT = []
        self._timeArray = []
        #确定格点坐标
        self._xMInit = np.arange(0,500,self._a)
        self._y = np.zeros(self._xMInit.shape)
        #声学波
        mSize = 10
        MSize = round((self._M/self._m)*mSize)
        self._MItemSound = self._p1.plot(pen=None, symbol='o', symbolPen=None, symbolSize=MSize, symbolBrush=(255, 0, 0, 255))
        self._mItemSound = self._p1.plot(pen=None, symbol='o', symbolPen=None, symbolSize=mSize, symbolBrush=(0, 255, 0, 255))
        self._MSound = self._p2.plot(pen=(255, 0, 0, 255))
        self._mSound = self._p2.plot(pen=(0, 255, 0, 100))#为了让两条线都能看到
        #光学波
        self._MItemOptic = self._p3.plot(pen=None, symbol='o', symbolPen=None, symbolSize=MSize, symbolBrush=(255, 0, 0, 255))
        self._mItemOptic = self._p3.plot(pen=None, symbol='o', symbolPen=None, symbolSize=mSize, symbolBrush=(0, 255, 0, 255))
        self._MOptic = self._p4.plot(pen=(255, 0, 0, 255))
        self._mOptic = self._p4.plot(pen=(0, 255, 0, 255))
        #动画定时
        self._timer = QTimer()
        self._timer.timeout.connect(self._update)
        self._timer.start(50)
    
    def stop(self):
        self._timer.stop()
        self._p1.clear()
        self._p2.clear()
        self._p3.clear()
        self._p4.clear()

    def getInfo(self):
        """返回插件的基本信息

        Returns:
            dict: 返回一个包含插件基本信息的字典，字典具体格式为{"name":[插件的中文名],"describe":[插件的简述，可用在显示在程序的statusBar],"version":[插件的版本信息，可用于插件更新判断]}
        """
        info = {"name":"一维复式晶格振动", "describe":"长波近似下的一维复式晶格振动", "version":"0.1"}
        return info

    def _update(self):
        #声学
        xSound = self._A*np.cos(self._q*self._xMInit+self._omega*self._time)
        xMSound = self._xMInit + xSound
        xmSound = self._xMInit + xSound + self._b
        self._MItemSound.setData(xMSound,self._y)
        self._mItemSound.setData(xmSound,self._y)
        #光学
        xOptic = xSound
        xMOptic = self._xMInit + xOptic
        xmOptic = -(self._M/self._m)*xOptic + self._b + self._xMInit
        self._MItemOptic.setData(xMOptic,self._y)
        self._mItemOptic.setData(xmOptic,self._y)
        if self._time == 0:
            self._p1.enableAutoRange('xy', False)
            self._p3.enableAutoRange('xy', False)
        #画振动图
        self._xMSoundByT.append(xSound[0])
        self._xmSoundByT.append(xSound[0])
        self._xMOpticByT.append(xOptic[0])
        self._xmOpticByT.append(-(self._M/self._m)*xOptic[0])
        self._timeArray.append(self._time)
        if self._time > 100:
            self._xMSoundByT.pop(0)
            self._xmSoundByT.pop(0)
            self._xMOpticByT.pop(0)
            self._xmOpticByT.pop(0)
            self._timeArray.pop(0)
        timeArray = np.array(self._timeArray)
        self._MSound.setData(timeArray,np.array(self._xMSoundByT))
        self._mSound.setData(timeArray,np.array(self._xmSoundByT))
        self._MOptic.setData(timeArray,np.array(self._xMOpticByT))
        self._mOptic.setData(timeArray,np.array(self._xmOpticByT))
        self._time += 1
    
    def _valueChangedHandle(self, value):
        self._M = value*self._m
        self.stop()
        self.run()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainForm = QMainWindow()
    frame = QFrame()
    mainForm.setCentralWidget(frame)
    demo = Plugin()
    demo.setUpUI(mainForm, frame)
    demo.run()
    mainForm.show()
    sys.exit(app.exec_())