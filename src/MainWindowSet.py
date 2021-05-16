import sys, pathlib, PyQt5, os, shutil
from PyQt5.QtWidgets import QMainWindow, qApp, QApplication, QTreeWidgetItem, QLabel, QAction, QMessageBox, QFileDialog
from PyQt5.QtGui import  QIcon
from src import Ui_MainWindow, DelPluginSet, PluginHelpSet, AboutDialogSet
import qdarkstyle
from itertools import chain
from pypinyin import pinyin, Style

class MainWindowSet(object):
    @classmethod
    def setUI(cls, mainWindow, pluginDict):
        cls._mainWindow = mainWindow
        cls._pluginDict = pluginDict
        cls._prePlugin = None
        #设置环境变量
        dirname = pathlib.Path(PyQt5.__file__).parent
        plugin_path = dirname.joinpath("Qt5","plugins", "platforms")
        os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = str(plugin_path)
        currentWorkDir = pathlib.Path.cwd()
        cls._currentWorkDir = str(currentWorkDir)
        #加载黑色主题
        darkStylesheet = qdarkstyle.load_stylesheet_pyqt5()
        qApp.setStyleSheet(darkStylesheet)
        #加载UI组件
        cls._mainWindowUI = Ui_MainWindow()
        cls._mainWindowUI.setupUi(mainWindow)
        cls._mainWindow.setWindowTitle('SolidPhysVisualization')
        iconDir = str(currentWorkDir.joinpath("src","icon.ico"))
        cls._mainWindow.setWindowIcon(QIcon(iconDir))
        cls._mainWindowUI.treeWidget.setRootIsDecorated(False)
        #加载插件
        cls._showPlugin()
        #加载菜单
        #文件菜单
        fileMenu = cls._mainWindowUI.menubar.addMenu("文件")
        exitAction = QAction("退出",cls._mainWindow)
        exitAction.setStatusTip("退出程序")
        exitAction.triggered.connect(qApp.exit)
        fileMenu.addAction(exitAction)
        #插件菜单
        pluginMenu = cls._mainWindowUI.menubar.addMenu("插件")
        updatePluginsAction = QAction("添加/更新插件",cls._mainWindow)
        updatePluginsAction.setStatusTip("选择插件并自动更新或者添加")
        updatePluginsAction.triggered.connect(cls._updatePluginsHandle)
        pluginMenu.addAction(updatePluginsAction)
        deletePluginsAction = QAction("卸载插件", cls._mainWindow)
        deletePluginsAction.setStatusTip("卸载已经安装的插件")
        deletePluginsAction.triggered.connect(cls._deletePluginsHandle)
        pluginMenu.addAction(deletePluginsAction)
        helpPluginsAction = QAction("查看帮助",cls._mainWindow)
        helpPluginsAction.setStatusTip("查看所有插件的帮助信息")
        helpPluginsAction.triggered.connect(cls._helpPluginsHandle)
        pluginMenu.addAction(helpPluginsAction)
        #关于菜单
        aboutMenu = cls._mainWindowUI.menubar.addMenu("关于")
        aboutAction = QAction("关于本程序",cls._mainWindow)
        aboutAction.setStatusTip("查看主程序的相关信息")
        aboutAction.triggered.connect(cls._aboutHandle)
        aboutMenu.addAction(aboutAction)
    
    @classmethod
    def _setWelcome(cls):
        """在treeWidget中添加欢迎按钮
        """      
        root = QTreeWidgetItem(cls._mainWindowUI.treeWidget)
        root.setText(0,"欢迎界面")

    @classmethod
    def _setWelcomeFrameUI(cls):
        """设置欢迎页面的UI
        """
        label = QLabel('<div align="center"><font size=50><i>Welcome!<i></font><br><br><br><br><br><br><br><br><font size=50>请点击左侧演示程序列表启动演示程序</font></div>')
        cls._mainWindowUI.gridLayout.addWidget(label)

    @classmethod
    def _insertPlugins(cls):
        """启动插件
        """
        cls._fileNamesSorted = cls._sortPluginName()
        for fileName in cls._fileNamesSorted:
            root = QTreeWidgetItem(cls._mainWindowUI.treeWidget)
            root.setText(0,cls._pluginDict[fileName]["name"])
            root.setStatusTip(0,cls._pluginDict[fileName]["describe"])

    @classmethod
    def _itemClickedHandle(cls, item, column):
        """处理treeWidgetItem被点击的信号的槽函数

        Args:
            item (treeWidgetItem): 被点击的项
            column (int): 被点击的位置 
        """
        cls._stopPlugin()
        index = cls._mainWindowUI.treeWidget.indexOfTopLevelItem(item)
        if index == 0:
            cls._setWelcomeFrameUI()
        else:
            pulginIndex = index - 1
            pluginName = cls._fileNamesSorted[pulginIndex]
            plugin = cls._getPluginClass(pluginName)
            plugin.setUpUI(cls._mainWindowUI.gridLayout)
            plugin.run()
            cls._prePlugin = plugin

    @classmethod
    def _updatePluginsHandle(cls):
        """更新或升级插件
        """
        filePath,_ = QFileDialog.getOpenFileName(cls._mainWindow, "选择插件", cls._currentWorkDir, "Python文件(*.py)")
        if filePath :
            filePath = pathlib.Path(filePath)
            fileDir = filePath.parents[0]
            pluginName = filePath.stem
            pluginDir = pathlib.Path(cls._currentWorkDir).joinpath("scripts",pluginName)
            #将插件同目录的文件全部拷贝到scripts下的与插件名相同的文件夹下
            if pluginDir.exists():
                if str(fileDir) != str(pluginDir):
                    messageBox = QMessageBox(cls._mainWindow)
                    messageBox.setWindowTitle("询问")
                    messageBox.setText("选择的插件已经存在，是否替换已有的插件?")
                    messageBox.setIcon(QMessageBox.Question)
                    messageBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                    buttonY = messageBox.button(QMessageBox.Yes)
                    buttonY.setText("确定")
                    buttonN = messageBox.button(QMessageBox.No)
                    buttonN.setText("取消")
                    messageBox.exec_()
                    if messageBox.clickedButton() == buttonY:
                        shutil.rmtree(str(pluginDir))
                        shutil.copytree(str(fileDir), str(pluginDir))

                    # reply = QMessageBox().question(cls._mainWindow,"询问","选择的插件已经存在，是否替换已有的插件?", QMessageBox.Yes|QMessageBox.No)
                    # if reply == QMessageBox.Yes:
                    #     shutil.rmtree(str(pluginDir))
                    #     shutil.copytree(str(fileDir), str(pluginDir))
            else:
                shutil.copytree(str(fileDir), str(pluginDir))
            plugin = cls._getPluginClass(pluginName)
            info = plugin.getInfo()
            cls._pluginDict[pluginName] = info
            cls._stopPlugin()
            cls._showPlugin()

    @classmethod
    def _deletePluginsHandle(cls):
        """卸载插件
        """
        deletePlugins = DelPluginSet.getDeletePlugins(cls._pluginDict)
        if deletePlugins:
            for plugin in deletePlugins:
                cls._pluginDict.pop(plugin)
            messageBox = QMessageBox(cls._mainWindow)
            messageBox.setWindowTitle("询问")
            messageBox.setText("是否删除插件对应的源文件?")
            messageBox.setIcon(QMessageBox.Question)
            messageBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            buttonY = messageBox.button(QMessageBox.Yes)
            buttonY.setText("是")
            buttonN = messageBox.button(QMessageBox.No)
            buttonN.setText("否")
            messageBox.exec_()
            if messageBox.clickedButton() == buttonY:
                for plugin in deletePlugins:
                    pluginDir = pathlib.Path(cls._currentWorkDir).joinpath("scripts",plugin)
                    shutil.rmtree(str(pluginDir))
            cls._stopPlugin()
            cls._showPlugin()
    @classmethod
    def _helpPluginsHandle(cls):
        PluginHelpSet.showHelp(cls._pluginDict)

    @classmethod
    def _aboutHandle(cls):
        helpText = '<b>这是帮助信息！</b> <a href="http://www.baidu.com">baidu.com</a>'
        AboutDialogSet.showHelp(helpText)

    @classmethod
    def _sortPluginName(cls):
        """将插件名按中文名称排序

        Returns:
            list: 排序后的文件名
        """
        plugs = {cls._pluginDict[fileName]["name"]:fileName for fileName in cls._pluginDict.keys()}
        names = sorted(plugs.keys(),key=lambda name: "".join(chain.from_iterable(pinyin(name,style=Style.TONE3))))
        fileNames = [plugs[name] for name in names]
        return fileNames

    @classmethod
    def _getPluginClass(cls, pluginName):
        """根据插件名，返回对应的插件类

        Args:
            pluginName (str): 插件的文件名

        Returns:
            plugin: 插件类对象
        """
        moduleName = "scripts."+pluginName+"."+pluginName
        moduleObj = __import__("scripts."+pluginName+"."+pluginName,fromlist=True) if moduleName not in sys.modules else sys.modules[moduleName]
        pluginClass = getattr(moduleObj,"Plugin")
        return pluginClass()
    
    @classmethod
    def _stopPlugin(cls):
        """停止并清理上一次运行的插件
        """
        #停止控件的运行
        if cls._prePlugin is not None:
            cls._prePlugin.stop()
            cls._prePlugin = None
        #清除以前的控件
        for indexWidget in range(cls._mainWindowUI.gridLayout.count()):
            try:
                cls._mainWindowUI.gridLayout.itemAt(indexWidget).widget().deleteLater()
            except AttributeError:
                pass
    
    @classmethod
    def _showPlugin(cls):
        """加载欢迎和插件界面
        """
        cls._mainWindowUI.treeWidget.clear()
        cls._setWelcome()
        cls._setWelcomeFrameUI()
        #加载插件
        cls._insertPlugins()
        cls._mainWindowUI.treeWidget.itemClicked.connect(cls._itemClickedHandle)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = QMainWindow()
    pluginDict = {"x":{"name":"开","describe":"哈哈"},"y":{"name":"一","describe":"哈哈"},"z":{"name":"啊","describe":"哈哈"}}
    MainWindowSet.setUI(mainWindow, pluginDict)
    mainWindow.show()
    sys.exit(app.exec_())
