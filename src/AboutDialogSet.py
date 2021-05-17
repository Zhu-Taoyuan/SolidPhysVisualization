import sys
from PyQt5.QtWidgets import QDialog, QApplication, QMainWindow, QDialogButtonBox
from PyQt5.QtGui import QDesktopServices, QIcon
from src import Ui_AboutDialog


class AboutDialogSet:
    @classmethod
    def showHelp(cls, helpText):
        """显示帮助文本

        Args:
            helpText (str): 帮助文本
        """
        cls._dialog = QDialog()
        cls._dialogSet = Ui_AboutDialog()
        cls._dialogSet.setupUi(cls._dialog)
        cls._dialog.setWindowIcon(QIcon(":ico/icon.ico"))
        cls._dialog.setWindowTitle("关于本程序")
        #设置textBrowser
        cls._dialogSet.textBrowser.setText(helpText)
        cls._dialogSet.textBrowser.setOpenLinks(False)
        cls._dialogSet.textBrowser.anchorClicked.connect(cls._anchorClickedHandle)
        #汉化按钮
        buttonClose = cls._dialogSet.buttonBox.button(QDialogButtonBox.Close)
        buttonClose.setText("关闭")
        cls._dialog.exec_()
    
    @classmethod
    def _anchorClickedHandle(cls, url):
        """超链接被点击的槽函数

        Args:
            url (QUrl):被点击的超链接 
        """
        QDesktopServices.openUrl(url)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = QMainWindow()
    mainWindow.show()
    helpText = '<b>这是帮助信息！</b> <a href="http://www.baidu.com">baidu.com</a>'
    AboutDialogSet.showHelp(helpText)
    sys.exit(app.exec_())