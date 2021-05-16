import sys, pathlib
from PyQt5.QtWidgets import QDialog, QApplication, QDialogButtonBox, QMainWindow, QAbstractItemView
from PyQt5.QtGui import  QIcon
from src import Ui_Dialog


class DelPluginSet(object):
    @classmethod
    def getDeletePlugins(cls,pluginDict):
        """外部调用来获取被删除插件列表的函数

        Args:
            pluginDict (dict): 总的插件字典

        Returns:
            list: 需要被删除的插件名称
        """
        cls._dialog = QDialog()
        cls._dialogSet = Ui_Dialog()
        cls._dialogSet.setupUi(cls._dialog)
        currentWorkDir = pathlib.Path.cwd()
        iconDir = str(currentWorkDir.joinpath("src","icon.ico"))
        cls._dialog.setWindowIcon(QIcon(iconDir))
        cls._dialog.setWindowTitle("卸载插件")
        #类字段
        cls._pluginDict = pluginDict
        cls._deleteKeys = []
        cls._maintainKeys = []
        #汉化提示框
        buttonY = cls._dialogSet.buttonBox.button(QDialogButtonBox.Ok)
        buttonY.setText("确定")
        buttonN = cls._dialogSet.buttonBox.button(QDialogButtonBox.Cancel)
        buttonN.setText("取消")
        #listWidget配置
        cls._dialogSet.maintainList.setSelectionMode(QAbstractItemView.ExtendedSelection)
        cls._dialogSet.deleteList.setSelectionMode(QAbstractItemView.ExtendedSelection)
        #列出插件
        cls._updateMaintain()
        cls._updateDelete()
        #按钮
        cls._dialogSet.deleteButton.setEnabled(False)
        cls._dialogSet.undoButton.setEnabled(False)
        #信号与槽函数
        cls._dialog.rejected.connect(cls._rejectedHandle)
        cls._dialogSet.maintainList.itemSelectionChanged.connect(cls._maintainSelectionChangedHandle)
        cls._dialogSet.deleteList.itemSelectionChanged.connect(cls._deleteSelectionChangedHandle)
        cls._dialogSet.deleteButton.clicked.connect(cls._deleteButtonClickedHandle)
        cls._dialogSet.undoButton.clicked.connect(cls._undoButtonClickedHandle)
        cls._dialog.exec_()
        return cls._deleteKeys

    @classmethod
    def _rejectedHandle(cls):
        """取消按键的处理函数
        """
        cls._deleteKeys = []
        cls._dialog.close()

    @classmethod
    def _updateMaintain(cls):
        """刷新左侧保留框的插件
        """
        cls._maintainKeys = list(cls._pluginDict.keys())
        for deleteKey in cls._deleteKeys:
            cls._maintainKeys.remove(deleteKey)
        cls._dialogSet.maintainList.clear()
        for key in cls._maintainKeys:
            cls._dialogSet.maintainList.addItem(cls._pluginDict[key]["name"])

    @classmethod
    def _updateDelete(cls):
        """刷新右侧被删除框的插件
        """
        cls._dialogSet.deleteList.clear()
        for key in cls._deleteKeys:
            cls._dialogSet.deleteList.addItem(cls._pluginDict[key]["name"])

    @classmethod
    def _maintainSelectionChangedHandle(cls):
        """左侧框选中状态改变的槽函数
        """
        items = cls._dialogSet.maintainList.selectedItems()
        if items :
           cls._dialogSet.deleteButton.setEnabled(True)
        else:
           cls._dialogSet.deleteButton.setEnabled(False)
    
    @classmethod
    def _deleteSelectionChangedHandle(cls):
        """右侧框选中状态改变的槽函数
        """
        items = cls._dialogSet.deleteList.selectedItems()
        if items :
           cls._dialogSet.undoButton.setEnabled(True)
        else:
           cls._dialogSet.undoButton.setEnabled(False)

    @classmethod
    def _deleteButtonClickedHandle(cls):
        """中间删除按钮被按下的槽函数
        """
        items = cls._dialogSet.maintainList.selectedItems()
        indexes = [cls._dialogSet.maintainList.indexFromItem(item).row() for item in items]
        for index in indexes:
            cls._deleteKeys.append(cls._maintainKeys[index])
        cls._updateMaintain()
        cls._updateDelete()

    @classmethod
    def _undoButtonClickedHandle(cls):
        """中间撤销按钮被按下的槽函数
        """
        items = cls._dialogSet.deleteList.selectedItems()
        indexes = [cls._dialogSet.deleteList.indexFromItem(item).row() for item in items]
        for index in indexes[::-1]:
            cls._deleteKeys.pop(index)
        cls._updateMaintain()
        cls._updateDelete()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = QMainWindow()
    mainWindow.show()
    pluginDict = {"x":{"name":"开","describe":"哈哈"},"y":{"name":"一","describe":"哈哈"},"z":{"name":"啊","describe":"哈哈"},"m":{"name":"嗯嗯","describe":"哈哈"}}
    temp = DelPluginSet.getDeletePlugins(pluginDict)
    print(temp)
    sys.exit(app.exec_())
