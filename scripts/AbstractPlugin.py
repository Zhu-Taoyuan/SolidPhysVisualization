class Plugin():

    def setUpUI(self, gridLayout):
        """设置frame上的UI，GUI程序提供一个空白的GridLayout对象，所有展示程序都在该GridLayout上进行

        Args:
            gridLayout (GridLayout): 程序的网格布局对象
        """
        pass

    def run(self):
        """启动展示程序
        """
        pass
        

    def getInfo(self):
        """返回插件的基本信息

        Returns:
            dict: 返回一个包含插件基本信息的字典，字典具体格式为{"name":[插件的中文名],"describe":[插件的简述，可用在显示在程序的statusBar],"version":[插件的版本信息，可用于插件更新判断]}
        """
        pass


    def stop(self):
        """停止展示程序，主要处理演示动画时，定时器停止的问题
        """
        pass
