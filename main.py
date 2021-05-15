import sys, pathlib,json
from PyQt5.QtWidgets import QMainWindow, QApplication
from src.MainWindowSet import MainWindowSet

def getPluginDict():
    settingPath = pathlib.Path("./settings.json")
    if settingPath.exists():
        with open(str(settingPath),"r",encoding='utf-8') as fp:
            pluginDict = json.load(fp)
    else:
        pluginDict = {}
        with open(str(settingPath),"w",encoding='utf-8') as fp:
            json.dump(pluginDict,fp)
    return pluginDict

def setSettings(pluginDict):
    settingPath = pathlib.Path("./settings.json")
    with open(str(settingPath),"w",encoding='utf-8') as fp:
        json.dump(pluginDict,fp)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = QMainWindow()
    pluginDict = getPluginDict()#获取插件列表
    MainWindowSet.setUI(mainWindow, pluginDict)
    mainWindow.show()
    returnNum = app.exec_()
    setSettings(pluginDict)#设置插件列表JSON
    sys.exit(returnNum)
    