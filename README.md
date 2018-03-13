# DDRtester
1site

================================================================
基于http://git.oschina.net/jakey.chen的串口工具进行的二次开发。

加入验证pattern，并于下位机进行通信的部分。
![](https://upload-images.jianshu.io/upload_images/4749583-fc2b780940c2b783.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

Serial Tool
================================================================
用python2.7、Tkinter、pyserial(使用版本3.3测试OK)模块开发的串口调试工具<br>

已将串口工具和USB整合在一起
* [SlaveDebugTool](https://git.oschina.net/jakey.chen/SlaveDebugTool)

使用python3稍作修改版本
* [py3版本](https://gitee.com/jakey.chen/Serial-Tool/tree/py3/)

安装使用
================================================================
需要安装的模块：<br>
在Windows下:<br>
    默认是有安装Tkinter的，因此只需要安装pyserial<br>
    可以通过pip来安装：<br>
        pip install pyserial<br>
    或者到 https://pypi.python.org/pypi/pywinusb 下载最新版安装<br>
        python setup.py install<br>
    或者到 http://www.lfd.uci.edu/~gohlke/pythonlibs/下载安装版<br>
在Ubuntu下：<br>
    默认是没有安装Tkinter的<br>
    需要先进行必要模块的安装<br>
    使用apt-get安装tk<br>
        sudo apt-get install python-tk<br>
    pyserial可以通过pip来安装：<br>
        pip install pyserial<br>
    或者到 https://pypi.python.org/pypi/pyserial 下载最新版安装<br>
        python setup.py install<br>
执行python main.py即可开始使用(ubuntu下需要使用root权限 sudo python main.py)<br>

![](http://git.oschina.net/jakey.chen/Serial-Tool/raw/master/Images/serial_tool.png)

使用技巧
================================================================
在左侧列表框，可以显示出当前连接的串口设备。<br>
可以通过双击打开设备（或者点击下面的Open打开设备）<br>
状态栏会有相应的提示信息<br>
点击Clear可以清除计数和接收的数据<br>
其他待定，暂使用良好，暂未发现Bug和需要改进的地方。<br>