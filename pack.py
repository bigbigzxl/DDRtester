#! /usr/bin/env python
# -*- coding: utf-8 -*-


# from distutils.core import  setup
# import py2exe
# import sys
# import FileDialog
# includes = ["encodings", "encodings.*"]
# sys.argv.append("py2exe")
# #error: [Errno 2] No such file or directory: 'MSVCP90.dll'
# options = {"py2exe":{ "bundle_files": 3, "dll_excludes":["MSVCP90.dll"]}}#64bits=3,32bits=1
# setup(options = options,
#       zipfile=None,
#       console = [{"script":'main.py', 'icon_resources':[(1, 'swallow_128px_1139556_easyicon.net.ico')]}])

from distutils.core import setup
import py2exe
import sys
import glob
#this allows to run it with a simple double click.
sys.argv.append('py2exe')

data_files = ["swallow_128px_1139556_easyicon.net.ico",
              (r'mpl-data', glob.glob(r'C:\Python27\Lib\site-packages\matplotlib\mpl-data\*.*')),
              (r'mpl-data', [r'C:\Python27\Lib\site-packages\matplotlib\mpl-data\matplotlibrc']),
              (r'mpl-data\images', glob.glob(r'C:\Python27\Lib\site-packages\matplotlib\mpl-data\images\*.*')),
              (r'mpl-data\fonts', glob.glob(r'C:\Python27\Lib\site-packages\matplotlib\mpl-data\fonts\*.*'))]


py2exe_options = {
		"includes": ["matplotlib.backends",
		             "matplotlib.figure",
		             "pylab",
		             "numpy",
		             "matplotlib.backends.backend_tkagg"],
		'excludes': ['_gtkagg',
		             '_tkagg',
		             '_agg2',
		             '_cairo',
		             '_cocoaagg',
		             '_fltkagg',
		             '_gtk',
		             '_gtkcairo', ],
		'dll_excludes': ['libgdk-win32-2.0-0.dll',"MSVCP90.dll",
		                 'libgobject-2.0-0.dll'],
        # "includes": ["sip"],  # 如果打包文件中有PyQt代码，则这句为必须添加的
        # "dll_excludes": ["MSVCP90.dll",],  # 这句必须有，不然打包后的程序运行时会报找不到MSVCP90.dll，如果打包过程中找不到这个文件，请安装相应的库
        "compressed": 1,
        "optimize": 2,
        "ascii": 0,
        "bundle_files": 3,  # 关于这个参数请看第三部分中的问题(2)
        }

setup(
      name = 'QAtester',
      version = '1.0',
      windows = [{"script":"main.py", "icon_resources":[(1, "swallow_128px_1139556_easyicon.net.ico")]}],
      zipfile = None,
      options = {'py2exe': py2exe_options},
	  data_files=data_files,
	
      )



# # !/usr/bin/env python
# # -*- coding:utf8 -*-
#
# """
# @file: setup
# @author: x00347195
# @time: 2016/5/17 11:31
# """
#
# from distutils.core import setup
# import py2exe
# import glob
#
# opts = {
# 	'py2exe': {
# 		"includes": ["matplotlib.backends",
# 		             "matplotlib.figure",
# 		             "pylab",
# 		             "numpy",
# 		             "matplotlib.backends.backend_tkagg"],
# 		'excludes': ['_gtkagg',
# 		             '_tkagg',
# 		             '_agg2',
# 		             '_cairo',
# 		             '_cocoaagg',
# 		             '_fltkagg',
# 		             '_gtk',
# 		             '_gtkcairo', ],
# 		'dll_excludes': ['libgdk-win32-2.0-0.dll',
# 		                 'libgobject-2.0-0.dll'],


# 		"dll_excludes": ["MSVCP90.dll",],  # 这句必须有，不然打包后的程序运行时会报找不到MSVCP90.dll，如果打包过程中找不到这个文件，请安装相应的库
#         "compressed": 1,
#         "optimize": 2,
#         "ascii": 0,
#         "bundle_files": 3,  # 关于这个参数请看第三部分中的问题(2)
# 	}
# }
#
# data_files = ["analysischanneldatatool.ico",
#               (r'mpl-data', glob.glob(r'C:\Python27\Lib\site-packages\matplotlib\mpl-data\*.*')),
#               (r'mpl-data', [r'C:\Python27\Lib\site-packages\matplotlib\mpl-data\matplotlibrc']),
#               (r'mpl-data\images', glob.glob(r'C:\Python27\Lib\site-packages\matplotlib\mpl-data\images\*.*')),
#               (r'mpl-data\fonts', glob.glob(r'C:\Python27\Lib\site-packages\matplotlib\mpl-data\fonts\*.*'))]
#
# setup(
# 	# options=options,
# 	zipfile=None,
# 	windows=[{"script": "main.py", "icon_resources": [(1, "swallow_128px_1139556_easyicon.net.ico")]}],
# 	data_files=data_files,
# 	version='Goku 1.0',
# 	name='sqxu',
# 	options=opts,
# )