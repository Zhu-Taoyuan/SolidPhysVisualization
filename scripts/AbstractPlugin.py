import abc
class AbstractPlugin(abc.ABCMeta):
    def __init__(self):
        super().__init__()

    @abc.abstractmethod
    def setUpUI(self,frame):
        """设置frame上的UI，GUI程序提供一个空白的QFrame对象，所有展示程序都在该Frame上进行

        Args:
            frame (QFrame): 展示程序的画布
        """
        pass

    @abc.abstractmethod
    def run(self):
        """启动展示程序
        """
        pass

    @abc.abstractclassmethod
    def getInfo(self):
        """返回插件的基本信息

        Returns:
            dict: 返回一个包含插件基本信息的字典，字典具体格式为{"name":[插件的中文名],"describe":[插件的简述，可用在显示在程序的statusBar],"version":[插件的版本信息，可用于插件更新判断]}
        """
        pass