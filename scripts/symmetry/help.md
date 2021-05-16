# 知识点检索系统

## 简介

此系统主要基于SQLite、PyQt5两个库进行开发，其中SQLite负责建立后端数据库，以及管理数据;PyQt5负责建立GUI，处理前端的控制逻辑。

目前实现的功能有：

* 管理知识点，即新建、删除、批量删除知识点
* 检索知识点，其默认开启的是基于正则表达式的字符模糊搜索，例如：输入关键`数学`，其实际匹配的是`^.*数学.*$`,即只要知识点名称中带有`数学`均会被搜索到。其还可以开启完全的正则表达式搜索模式，此时匹配的就是搜索框中的正则表达式。
* 对检索到的材料进行预览，如果是文本材料，其可以直接在右边的文本框中预览，如果是本地文件，可以点击文本框中的超链接，直接使用本地默认应用程序打开该文件。

## 文件组织结构 

| 文件名             | 说明                                 |
| ------------------ | :----------------------------------- |
| KnowledgeManage.py | 主程序接口                           |
| KnowledgeDB.py     | 数据库处理接口                       |
| MainWindowUI.py    | Qt Designer 生成的主界面代码         |
| TextDialogUI.py    | Qt Designer 生成的文本输入对话框代码 |
| TextInputDialog.py | 自定义文本输入对话框获取文本方法     |
| requirements.txt   | 程序依赖说明                         |
| test.db            | 测试数据库                           |

 



## 使用方法

### 建立虚拟环境(选作)

在该文件目录下打开命令行，输入命令：

```powershell
python -m venv env
```

![alt venv](picture/venv.gif)

启动虚拟环境下的Python：

```powershell
./env/Scripts/active
```

![alt active](picture/active.gif)

*注：也可直接跳过该过程，这样的话，依赖是直接安装在系统默认的Python环境下*

### 安装依赖

安装**requirements.txt**中的依赖：

```powershell
pip install -r requirements.txt
```

![alt pip](picture/pip.gif)

### 启动主程序

输入命令：

```powershell
python KnowledgeManage.py
```

![alt python](picture/python.gif)



## TODO

* GUI中数据处理还在主线程，没有利用多线程处理数据
* GUI中的部分操作还是不够人性化，例如在列表标题处可以添加一个全选按钮的，但是由于PyQt自身限制，实现起来比较麻烦，所以没有添加。