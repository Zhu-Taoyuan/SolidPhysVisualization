import sys
from PyQt5.QtWidgets import QMainWindow, QFrame, QApplication, QLabel, QGridLayout, QHBoxLayout, QComboBox, QPushButton
from PyQt5.QtCore import QTimer
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
        #构造网格，由于两个3D动画框可以共用，可以只构造一次
        gx = gl.GLGridItem()
        gx.rotate(90, 0, 1, 0)
        gx.translate(-10, 0, 0)
        gy = gl.GLGridItem()
        gy.rotate(90, 1, 0, 0)
        gy.translate(0, -10, 0)
        gz = gl.GLGridItem()
        gz.translate(0, 0, -10)
        #第一个3D展示框
        self._initGLWindow = gl.GLViewWidget()
        self._initGLWindow.opts["distance"] = 30
        self._initGLWindow.opts["azimuth"] = 30
        self._initGLWindow.addItem(gx)
        self._initGLWindow.addItem(gy)
        self._initGLWindow.addItem(gz)
        self._gridLayout.addWidget(self._initGLWindow,0,0)
        #第二个3D展示框
        self._changeGLWindow = gl.GLViewWidget()
        self._changeGLWindow.opts['distance'] = 30
        self._changeGLWindow.opts["azimuth"] = 30
        self._changeGLWindow.addItem(gx)
        self._changeGLWindow.addItem(gy)
        self._changeGLWindow.addItem(gz)
        self._gridLayout.addWidget(self._changeGLWindow,0,1)
        #选择初始图形
        self._initComboBox = QComboBox()
        self._initComboBox.addItems(["3度旋转反演","4度旋转反演","6度旋转反演"])
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
        self._changeComboBox.addItems(["对称心","镜像","1度旋转","2度旋转","3度旋转","4度旋转","6度旋转","1度旋转反演","2度旋转反演","3度旋转反演","4度旋转反演","6度旋转反演"])
        labelChange = QLabel()
        labelChange.setText("请选择对称操作：")
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
        #设置槽函数
        self._initButton.clicked.connect(self._initButtonClickedHandle)
        self._changeButton.clicked.connect(self._changeButtonClickedHandle)
        #定义形状坐标
        self._3RI = np.array([[10,0,5],[-5,5*np.sqrt(3),5],[-5,-5*np.sqrt(3),5],[5,5*np.sqrt(3),-5],[-10,0,-5],[5,-5*np.sqrt(3),-5]])
        self._4RI = np.array([[5,5,5],[-5,-5,5],[5,-5,-5],[-5,5,-5]])
        self._6RI = np.array([[10,0,5],[-5,5*np.sqrt(3),5],[-5,-5*np.sqrt(3),5],[10,0,-5],[-5,5*np.sqrt(3),-5],[-5,-5*np.sqrt(3),-5]])
        #定义线图坐标
        self._3RI_LINE = np.array([[10,0,5],[5,5*np.sqrt(3),5],[-5,5*np.sqrt(3),5],[-10,0,5],[-5,-5*np.sqrt(3),5],[5,-5*np.sqrt(3),5],[10,0,5]])
        self._4RI_LINE = np.array([[5,5,5],[5,-5,5],[-5,-5,5],[-5,5,5],[5,5,5]])
        self._6RI_LINE = self._3RI_LINE
        #定义类字段
        self._initShapeItem = gl.GLScatterPlotItem(pos=None, color=(1,0,0,1), size=1, pxMode=False)
        self._initGLWindow.addItem(self._initShapeItem)
        self._changeShapeItem = gl.GLScatterPlotItem(pos=None, color=(1,0,0,1), size=1, pxMode=False)
        self._changeGLWindow.addItem(self._changeShapeItem)
        self._initShape = self._3RI
        self._initShapeLine = self._3RI_LINE
        self._initLineItems = []
        self._changeShape = None
        self._changeShapeLine = None
        self._changeLineItems = []
        #计时器相关
        self._timer = None
        self._speed = 10
        self._timerCount = 0
        self._continueFlag = False
        #利用字典实现switch-case的功能
        self._INIT_SHAPE_DICT = {"3度旋转反演":[self._3RI,self._3RI_LINE], "4度旋转反演":[self._4RI,self._4RI_LINE],"6度旋转反演":[self._6RI,self._6RI_LINE]}
        self._CHANGE_FUNCTION_PARAMETER = {
            "对称心": "self._inverse()",
            "镜像": "self._mirror()",
            "1度旋转": "self._rotate(360/1)",
            "2度旋转": "self._rotate(360/2)",
            "3度旋转": "self._rotate(360/3)",
            "4度旋转": "self._rotate(360/4)",
            "6度旋转": "self._rotate(360/6)",
            "1度旋转反演": "self._rotateInverse(360/1)",
            "2度旋转反演": "self._rotateInverse(360/2)",
            "3度旋转反演": "self._rotateInverse(360/3)",
            "4度旋转反演": "self._rotateInverse(360/4)",
            "6度旋转反演": "self._rotateInverse(360/6)"
            }

    def run(self):
        """启动展示程序
        """
        self._changeShape = self._initShape.copy()
        self._changeShapeLine = self._initShapeLine.copy()
        self._initShapeItem.setData(pos=self._initShape)
        self._drawLine(self._initShapeLine, self._initGLWindow, self._initLineItems)
        self._changeShapeItem.setData(pos=self._changeShape)
        self._drawLine(self._changeShapeLine, self._changeGLWindow, self._changeLineItems)
        

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

    def _initButtonClickedHandle(self):
        """形状选择按键槽函数
        """
        choose = self._initComboBox.currentText()
        self._initShape = self._INIT_SHAPE_DICT[choose][0]
        self._initShapeLine = self._INIT_SHAPE_DICT[choose][1]
        self.run()
    
    def _drawLine(self,surfacePoint, window, preItems):
        """根据表面顶点坐标画立方体

        Args:
            surfacePoint (numpy.narray): x-y平面的顶点坐标
            window (GLViewWidget): 3D展示的窗口
            preItems (list): 用于清除上一次的轮廓 
        """
        for item in preItems:
            window.removeItem(item)
        preItems.clear()
        if(surfacePoint is not None):
            plt = gl.GLLinePlotItem(pos=surfacePoint, color=(0,1,0,1), width=1, antialias=True)
            preItems.append(plt)
            window.addItem(plt)
            surfacePointButtom = surfacePoint*np.array([[1,1,-1] for i in range(surfacePoint.shape[0])])
            plt = gl.GLLinePlotItem(pos=surfacePointButtom, color=(0,1,0,1), width=1, antialias=True)
            preItems.append(plt)
            window.addItem(plt)
            for i in range(surfacePoint.shape[0]):
                pos = np.array([surfacePoint[i],surfacePointButtom[i]])
                temp = gl.GLLinePlotItem(pos=pos, color=(0,1,0,1), width=1, antialias=True)
                preItems.append(temp)
                window.addItem(temp)

    def _changeButtonClickedHandle(self):
        """操作按钮的槽函数
        """
        choose = self._changeComboBox.currentText()
        eval(self._CHANGE_FUNCTION_PARAMETER[choose])
    
    def _inverse(self):
        """反演操作
        """
        self._factor = np.linspace(1,-1,self._speed)
        self._initButton.setEnabled(False)
        self._changeButton.setEnabled(False)
        self._timer = QTimer()
        self._timer.timeout.connect(self._inverseTimeoutHandle)
        self._timer.start(50)
    
    def _inverseTimeoutHandle(self):
        """反演的动画更新函数
        """
        self._timer.stop()
        if self._timerCount < self._speed:
            changeShape = self._factor[self._timerCount] * self._changeShape
            changeShapeLine = self._factor[self._timerCount] * self._changeShapeLine
            self._changeShapeItem.setData(pos=changeShape)
            self._drawLine(changeShapeLine, self._changeGLWindow, self._changeLineItems)
            self._timerCount += 1
            self._timer.start()#这种写法是避免中间的操作影响计时
        else:
            self._changeShape *= -1
            self._changeShapeLine *= -1
            self._initButton.setEnabled(True)
            self._changeButton.setEnabled(True)
            self._timerCount = 0
            self._timer = None
    
    def _mirror(self):
        """镜像函数
        """
        factor = np.linspace(1,-1,self._speed)
        self._mirrorShapeMatrixes = [np.array([[1,1,factor[x]] for i in range(self._changeShape.shape[0])]) for x in range(self._speed)]
        self._mirrorShapeLineMatrixes = [np.array([[1,1,factor[x]] for i in range(self._changeShapeLine.shape[0])]) for x in range(self._speed)]
        self._initButton.setEnabled(False)
        self._changeButton.setEnabled(False)
        self._timer = QTimer()
        self._timer.timeout.connect(self._mirrorTimeoutHandle)
        self._timer.start(50)
    
    def _mirrorTimeoutHandle(self):
        """镜像更换函数
        """
        self._timer.stop()
        if self._timerCount < self._speed:
            changeShape = self._mirrorShapeMatrixes[self._timerCount] * self._changeShape
            changeShapeLine = self._mirrorShapeLineMatrixes[self._timerCount] * self._changeShapeLine
            self._changeShapeItem.setData(pos=changeShape)
            self._drawLine(changeShapeLine, self._changeGLWindow, self._changeLineItems)
            self._timerCount += 1
            self._timer.start()#这种写法是避免中间的操作影响计时
        else:
            self._changeShape = self._mirrorShapeMatrixes[-1] * self._changeShape
            self._changeShapeLine = self._mirrorShapeLineMatrixes[-1] * self._changeShapeLine
            self._initButton.setEnabled(True)
            self._changeButton.setEnabled(True)
            self._timerCount = 0
            self._timer = None
    
    def _rotate(self, angle):
        """旋转操作函数

        Args:
            angle (float): 需要旋转的角度(角度值)
        """
        stepAngles = np.linspace(0,angle*np.pi/180,self._speed)
        self._rotateMatrixes = [np.array([[np.cos(stepAngle),-np.sin(stepAngle),0],[np.sin(stepAngle),np.cos(stepAngle),0],[0,0,1]]) for stepAngle in stepAngles]#变换矩阵
        self._initButton.setEnabled(False)
        self._changeButton.setEnabled(False)
        self._timer = QTimer()
        self._timer.timeout.connect(self._rotateTimeoutHandle)
        self._timer.start(50)
    
    def _rotateTimeoutHandle(self):
        """旋转动画更新函数
        """
        self._timer.stop()
        if self._timerCount < self._speed:
            changeShape = np.dot(self._rotateMatrixes[self._timerCount],self._changeShape.T).T
            changeShapeLine = np.dot(self._rotateMatrixes[self._timerCount],self._changeShapeLine.T).T
            self._changeShapeItem.setData(pos=changeShape)
            self._drawLine(changeShapeLine, self._changeGLWindow, self._changeLineItems)
            self._timerCount += 1
            self._timer.start()#这种写法是避免中间的操作影响计时
        else:
            self._changeShape = np.dot(self._rotateMatrixes[-1],self._changeShape.T).T
            self._changeShapeLine = np.dot(self._rotateMatrixes[-1],self._changeShapeLine.T).T
            self._initButton.setEnabled(True)
            self._changeButton.setEnabled(True)
            self._timerCount = 0
            self._timer = None
    
    def _rotateInverse(self, angle):
        """旋转反演操作

        Args:
            angle (float): 需要旋转的角度(角度值)
        """
        stepAngles = np.linspace(0,angle*np.pi/180,self._speed)
        self._rotateMatrixes = [np.array([[np.cos(stepAngle),-np.sin(stepAngle),0],[np.sin(stepAngle),np.cos(stepAngle),0],[0,0,1]]) for stepAngle in stepAngles]#变换矩阵 
        self._factor = np.linspace(1,-1,self._speed)
        self._continueFlag = True
        self._initButton.setEnabled(False)
        self._changeButton.setEnabled(False)
        self._timer = QTimer()
        self._timer.timeout.connect(self._rotateInverseTimeoutHandle)
        self._timer.start(50)

    def _rotateInverseTimeoutHandle(self):
        """旋转反演的更新函数
        """
        self._timer.stop()
        if self._continueFlag:
            if self._timerCount < self._speed:
                changeShape = np.dot(self._rotateMatrixes[self._timerCount],self._changeShape.T).T
                changeShapeLine = np.dot(self._rotateMatrixes[self._timerCount],self._changeShapeLine.T).T
                self._changeShapeItem.setData(pos=changeShape)
                self._drawLine(changeShapeLine, self._changeGLWindow, self._changeLineItems)
                self._timerCount += 1
                self._timer.start()#这种写法是避免中间的操作影响计时
            else:
                self._changeShape = np.dot(self._rotateMatrixes[-1],self._changeShape.T).T
                self._changeShapeLine = np.dot(self._rotateMatrixes[-1],self._changeShapeLine.T).T
                self._initButton.setEnabled(True)
                self._changeButton.setEnabled(True)
                self._timerCount = 0
                self._continueFlag = False
                self._timer.start()
        else:
            if self._timerCount < self._speed:
                changeShape = self._factor[self._timerCount] * self._changeShape
                changeShapeLine = self._factor[self._timerCount] * self._changeShapeLine
                self._changeShapeItem.setData(pos=changeShape)
                self._drawLine(changeShapeLine, self._changeGLWindow, self._changeLineItems)
                self._timerCount += 1
                self._timer.start()#这种写法是避免中间的操作影响计时
            else:
                self._changeShape *= -1
                self._changeShapeLine *= -1
                self._initButton.setEnabled(True)
                self._changeButton.setEnabled(True)
                self._timerCount = 0
                self._timer = None


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