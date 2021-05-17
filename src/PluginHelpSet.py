import sys, pathlib
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import  QIcon
from src import Ui_widget

class PluginHelpSet(object):
    @classmethod
    def showHelp(cls, pluginDict):
        """显示插件的帮助信息

        Args:
            pluginDict (dict): 插件列表
        """
        cls._currentWorkDir = pathlib.Path.cwd()
        #设置窗口
        cls._widget = QWidget()
        cls._widgetSet = Ui_widget()
        cls._widgetSet.setupUi(cls._widget)
        cls._widget.setWindowIcon(QIcon(":ico/icon.ico"))
        cls._widget.setWindowTitle("插件帮助")
        cls._pluginDict = pluginDict
        cls._pluginKeys = list(cls._pluginDict.keys())
        cls._showPlugin()
        cls._widgetSet.textBrowser.setText("点击左边的插件获取帮助信息")
        cls._widgetSet.listWidget.itemClicked.connect(cls._itemClickedHandle)
        cls._widget.show()
    
    @classmethod
    def _showPlugin(cls):
        """列出现有插件
        """
        for key in cls._pluginKeys:
            cls._widgetSet.listWidget.addItem(cls._pluginDict[key]["name"])
    
    @classmethod
    def _itemClickedHandle(cls,item):
        """列表的子项被点击的槽函数

        Args:
            item (QListWidgetItem): 被点击的项目
        """
        index = cls._widgetSet.listWidget.indexFromItem(item).row()
        pluginName = cls._pluginKeys[index]
        path = cls._currentWorkDir.joinpath("scripts", pluginName, "help.md")
        if path.exists():
            cls._widgetSet.textBrowser.setSource(QUrl.fromLocalFile(str(path)))
        else:
            cls._widgetSet.textBrowser.setText("该插件暂无帮助信息！")
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = QMainWindow()
    mainWindow.show()
    pluginDict = {"symmetry": {"name": "\u6676\u4f53\u5bf9\u79f0\u64cd\u4f5c", "describe": "3D\u5c55\u793a\u6676\u4f53\u7684\u5bf9\u79f0\u64cd\u4f5c", "version": "0.1"}, "wave": {"name": "\u4e00\u7ef4\u590d\u5f0f\u6676\u683c\u632f\u52a8", "describe": "\u957f\u6ce2\u8fd1\u4f3c\u4e0b\u7684\u4e00\u7ef4\u590d\u5f0f\u6676\u683c\u632f\u52a8", "version": "0.1"}}
    PluginHelpSet.showHelp(pluginDict)
    sys.exit(app.exec_())