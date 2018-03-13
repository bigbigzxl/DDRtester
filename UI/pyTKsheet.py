#! /usr/bin/env python
# -*- coding: utf-8 -*-
from tkinter import Tk, Scrollbar, Frame

from tkinter.ttk import Treeview
import ttk
from Tkinter import *
import Tkinter as tk
import time, os, csv
import tkMessageBox

class TKsheet(object):
	# tkinter里面：
	# root = Tk()创建程序窗口；
	# frame = Frame(root)创建第一级区域；
	# import ttk  tabControl = ttk.Notebook(frameX)可以在frame下创建多标签窗口！
	# 在notebook下可以建立下一级的frame：self.tab1 = ttk.Frame(tabControl)，这又是frame了哟！
	
	# 建立表格：一般是在界面里面嵌入显示，所以这里限定是在frame下嵌入（root下应该行，懒得去试咯~）
	# 传入一个载体，最好是frame！
	def __init__(self, frame=None, file_path=""):
		# super(MainSerialTool, self).__init__(master)
		self.frame = frame
		self.default_style()
		self.filepath = file_path
		# Button-1: 左键，绑定左键事件
		self.tree.bind('<Double-Button-1>', self.sheetrefresh)
	
	def default_style(self):
		# sheet size: default
		self.set_size()
		
		# 滚动条
		self.scrollBar = Scrollbar(self.frame)
		self.scrollBar.pack(side=tk.LEFT, fill=tk.Y)
		
		# Treeview组件，6列，显示表头，带垂直滚动条
		self.tree = Treeview(self.frame,
		                     columns=('c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'c8'),
		                     show="headings",
		                     yscrollcommand=self.scrollBar.set,
		                     )
		
		# 设置每列宽度和对齐方式
		self.tree.column('c1', width=95, anchor='w')  # n, ne, e, se, s, sw, w, nw, or center指的是列里面的数据靠西边，而不是headings
		self.tree.column('c2', width=80, anchor='center')
		self.tree.column('c3', width=70, anchor='center')
		self.tree.column('c4', width=95, anchor='center')
		self.tree.column('c5', width=95, anchor='center')
		self.tree.column('c6', width=95, anchor='center')
		self.tree.column('c7', width=95, anchor='center')
		self.tree.column('c8', width=75, anchor='center')
		
		# 设置每列表头标题文本
		# datetime,TestResult,InitTime,SceneVdd12,SceneVdd18,SleepVdd12,SleepVdd18,MEM+4K
		self.tree.heading('c1', text='测试时间')
		self.tree.heading('c2', text='||TestResult||')
		self.tree.heading('c3', text='||InitTime||')
		self.tree.heading('c4', text='||SceneVdd12||')
		self.tree.heading('c5', text='||SceneVdd18||')
		self.tree.heading('c6', text='||SleepVdd12||')
		self.tree.heading('c7', text='||SleepVdd18||')
		self.tree.heading('c8', text='||MEM+4K||')
		
		self.tree.pack(side=tk.LEFT, fill=tk.Y)
		
		# Treeview组件与垂直滚动条结合
		self.scrollBar.config(command=self.tree.yview)
	
	def set_size(self, shiftX=1, shiftY=1, sheet_width=800, sheet_height=500):
		# x，y是偏移量，离左上角的偏移像素
		self.frame.place(x=shiftX, y=shiftY, width=sheet_width, height=sheet_height)
	
	def sheetrefresh(self, event):
		# 定义并绑定Treeview组件的鼠标事件
		# 双击刷新sheet：读取当天的数据文件，抽取写入即可，双击一次则重新写入一次。
		#
		# 文件不存在，我啥也不干就好了嘛！小罗罗就要被动，不要总想搞些什么大新闻（从我这个上帝视角来看的话！）
		if not os.path.exists(self.filepath):
			
			return
		
		# 要是存在的话，我就读文件，然后显示出来
		with open(self.filepath, "rb") as sheet:
			reader = csv.reader(sheet, dialect='excel')
			# csv方式刚好读出来的就是数组格式
			for i, row in enumerate(reader):
				# 第一行是列名称，排除掉
				if i == 0:
					pass
				# 其他行就写进表格里面
				self.add_newline(row)
		
		print(event.x, event.y)
	
	def add_newline(self, position="end", insert_data=[]):
		# "" 参数为空则表示新建一个top level的行。行内嵌套先不研究，太费时间。
		# 第二个参数："0"表示从行首插入； "end"从行尾插入； "i"：从行i处插入；
		# insert_data=[time.strftime('[18/%m/%d %H:%M] ', time.localtime(time.time()))] * 8
		if len(insert_data) == 0:
			return
		try:
			self.tree.insert("", "end", values=insert_data)
		except Exception as e:
			print("sheet insert line fail.\r\n", e)
	
	def test_demo(self):
		# 插入演示数据
		
		# time.strftime('[%Y-%m-%d %H:%M:%S] ',time.localtime(time.time()))
		for i in range(3):
			self.tree.insert('', i, values=[str(i)] * 8)

if __name__ == "__main__":
	# 创建tkinter应用程序窗口
	root = Tk()
	# 设置窗口大小和位置
	root.geometry('800x600')  # +400+300
	# 不允许改变窗口大小
	root.resizable(False, False)
	# 设置窗口标题
	root.title('FT数据显示样本')
	# 使用Treeview组件实现表格功能
	frame = Frame(root)
	sheet1 = TKsheet(frame)
	# sheet1.test_demo()
	sheet1.add_newline(
		insert_data=[time.strftime('%m/%d %H:%M', time.localtime(time.time())), "pass", "21.3", "150.1", "18.2", "1.7",
		             "0.3", "powerFail"])
	# 运行程序，启动事件循环
	
	root.mainloop()