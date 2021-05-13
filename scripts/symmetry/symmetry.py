import sys
from PyQt5.QtWidgets import QMainWindow, QFrame, QApplication, QLabel, QGridLayout, QHBoxLayout, QComboBox, QPushButton
from PyQt5.QtCore import QTimer,Qt
from PyQt5 import QtGui
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import numpy as np

class Plugin():
    def __init__(self):
        super().__init__()

    def setUpUI(self, gridLayout):
        """设置frame上的UI，GUI程序提供一个空白的GridLayout对象，所有展示程序都在该GridLayout上进行

        Args:
            gridLayout (GridLayout): 程序的网格布局对象
        """
        frame = QFrame()
        gridLayout.addWidget(frame)
        self._gridLayout = QGridLayout(frame)
        #第一个3D展示框
        self._initGLWindow = gl.GLViewWidget()
        self._initGLWindow.opts['distance'] = 20
        #self._initGLWindow.show()#必须加，不然会有Bug
        gx = gl.GLGridItem()
        gx.rotate(90, 0, 1, 0)
        gx.translate(-10, 0, 0)
        gy = gl.GLGridItem()
        gy.rotate(90, 1, 0, 0)
        gy.translate(0, -10, 0)
        gz = gl.GLGridItem()
        gz.translate(0, 0, -10)
        self._initGLWindow.addItem(gx)
        self._initGLWindow.addItem(gy)
        self._initGLWindow.addItem(gz)
        self._gridLayout.addWidget(self._initGLWindow,0,0)
        #第二个3D展示框
        self._changeGLWindow = gl.GLViewWidget()
        self._changeGLWindow.opts['distance'] = 20
        #self._changeGLWindow.show()#必须加，不然会有Bug
        gridItem2 = gl.GLGridItem()
        self._changeGLWindow.addItem(gx)
        self._changeGLWindow.addItem(gy)
        self._changeGLWindow.addItem(gz)
        self._gridLayout.addWidget(self._changeGLWindow,0,1)
        #选择初始图形
        self._initComboBox = QComboBox()
        self._initComboBox.addItems(["点","3度旋转反演","4度旋转反演","6度旋转反演"])
        labelInit = QLabel()
        labelInit.setText("请选择初始形状：")
        self._initButton = QPushButton()
        self._initButton.setText("确定")
        hInitBox = QHBoxLayout()
        hInitBox.addStretch(1)
        hInitBox.addWidget(labelInit)
        hInitBox.addWidget(self._initComboBox)
        hInitBox.addWidget(self._initButton)
        #选择基础操作
        self._changeComboBox = QComboBox()
        self._changeComboBox.addItems(["对称心","镜像","2度旋转","3度旋转","4度旋转","6度旋转","3度旋转反演","4度旋转反演","6度旋转反演"])
        labelChange = QLabel()
        labelChange.setText("请选择基本对称操作：")
        self._changeButton = QPushButton()
        self._changeButton.setText("确定")
        hChangeBox = QHBoxLayout()
        hChangeBox.addStretch(1)
        hChangeBox.addWidget(labelChange)
        hChangeBox.addWidget(self._changeComboBox)
        hChangeBox.addWidget(self._changeButton)
        #添加选择组件
        self._gridLayout.addLayout(hInitBox,1,0)
        self._gridLayout.addLayout(hChangeBox,1,1)

    def run(self):
        """启动展示程序
        """
        pass

    def getInfo(self):
        """返回插件的基本信息

        Returns:
            dict: 返回一个包含插件基本信息的字典，字典具体格式为{"name":[插件的中文名],"describe":[插件的简述，可用在显示在程序的statusBar],"version":[插件的版本信息，可用于插件更新判断]}
        """
        info = {"name":"晶体对称操作", "describe":"3D展示晶体的对称操作", "version":"0.1"}
        return info

    def stop(self):
        """停止展示程序，主要处理演示动画时，定时器停止的问题
        """
        pass

    def _update(self):
        """动画刷新程序
        """
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
        """输入框数据改变的槽函数

        Args:
            value (float): 输入框的值
        """
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