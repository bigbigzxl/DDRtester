#! /usr/bin/env python
# -*- coding: utf-8 -*-

import ttk
import time, os,re
import tkFont
import logging
import datetime
import binascii
import platform
import threading
import Tkinter as tk
import tkMessageBox
import csv
from UI.MainFrm import MainFrame
from Utils.SerialHelper import SerialHelper
import FileDialog
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# 根据系统 引用不同的库
if platform.system() == "Windows":
	from serial.tools import list_ports
else:
	import glob
	import os
	import re

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

# 结束符（16进制）CR 13; NL(LF) 10
END_HEX = "16"
CURR_ERROR = -10

class MainSerialTool(MainFrame):
	'''
    main func class
    '''
	
	def __init__(self, master=None):
		super(MainSerialTool, self).__init__(master)
		self.root = master
		self.time_gap = 0
		self.serial_receive_count = 0
		self.serial_recieve_data = ""
		self.receive_data_zxl = ""
		
		self.current_clicked_btn = ""
		self.serial_listbox = list()
		self.flash_flag = True
		self.find_all_devices()
		self.Item_testtime = 0
		self.TIME_OUT = 60
		self.mem_runtime = 0
		self.STOP = False
		self.FailLog_folderPath,self.database_path = self.Init_TestData()
		#这还是在框架里面的表格部分哩~
		# self.sheet.filepath = self.database_path
		
		
		#只能在这绑定，在MainFram里面无法调用出来！
		self.root.bind("<Key-space>", self.TestItem_AutoTesting)
		
		self.serial_frm.frm_right_send.insert("end", "TestItem0#", "red")
		
	def find_all_devices(self):
		'''
        线程检测连接设备的状态
        '''
		self.find_all_serial_devices()
		self.start_thread_timer(self.find_all_devices, 1)
	
	def find_all_serial_devices(self):
		'''
        检查串口设备
        '''
		try:
			if platform.system() == "Windows":
				self.temp_serial = list()
				for com in list(list_ports.comports()):
					try:
						strCom = com[0].encode(
							"utf-8") + ": " + com[1][:-7].encode("utf-8")
					except:
						strCom = com[0] + ": " + \
						         com[1][:-7].decode("gbk").encode("utf-8")
					self.temp_serial.append(strCom)
				for item in self.temp_serial:
					if item not in self.serial_listbox:
						self.serial_frm.frm_left_listbox.insert("end", item)
				for item in self.serial_listbox:
					if item not in self.temp_serial:
						size = self.serial_frm.frm_left_listbox.size()
						index = list(self.serial_frm.frm_left_listbox.get(
							0, size)).index(item)
						self.serial_frm.frm_left_listbox.delete(index)
				
				self.serial_listbox = self.temp_serial
			
			elif platform.system() == "Linux":
				self.temp_serial = list()
				self.temp_serial = self.find_usb_tty()
				for item in self.temp_serial:
					if item not in self.serial_listbox:
						self.serial_frm.frm_left_listbox.insert("end", item)
				for item in self.serial_listbox:
					if item not in self.temp_serial:
						index = list(self.serial_frm.frm_left_listbox.get(
							0, self.serial_frm.frm_left_listbox.size())).index(item)
						self.serial_frm.frm_left_listbox.delete(index)
				self.serial_listbox = self.temp_serial
		except Exception as e:
			logging.error(e)
	
	def Toggle(self, event=None):
		'''
        打开/关闭 设备
        '''
		self.serial_toggle()
		
	def Send(self):
		'''
        发送数据
        '''
		self.serial_send()
	
	def serial_send(self):
		'''
        串口数据发送 CR 13; NL(LF) 10
        '''
		send_data = self.serial_frm.frm_right_send.get("0.0", "end").strip()
		if self.serial_frm.new_line_cbtn_var.get() == 1:  # 是否添加换行符
			send_data = send_data + "\n"
		
		logging.info(">>>" + str(send_data))
		if self.serial_frm.send_hex_cbtn_var.get() == 1:  # 是否使用16进制发送
			send_data = send_data.replace(" ", "").replace("\n", "10")
			self.ser.write(send_data, True)
		else:
			self.ser.write(send_data)
	
	def SerialClear(self):
		'''
        clear serial receive text
        '''
		self.serial_receive_count = 0
		self.serial_frm.frm_right_receive.delete("0.0", "end")
	
	def serial_toggle(self):
		'''
        打开/关闭串口设备
        '''
		if self.serial_frm.frm_left_btn["text"] == "Open":
			try:
				serial_index = self.serial_frm.frm_left_listbox.curselection()
				if serial_index:
					self.current_serial_str = self.serial_frm.frm_left_listbox.get(
						serial_index).encode("utf-8")
				else:
					self.current_serial_str = self.serial_frm.frm_left_listbox.get(
						self.serial_frm.frm_left_listbox.size() - 1).encode("utf-8")
				
				if platform.system() == "Windows":
					self.port = self.current_serial_str.split(":")[0]
				elif platform.system() == "Linux":
					self.port = self.current_serial_str
				self.baudrate = self.serial_frm.frm_left_combobox_baudrate.get()
				self.parity = self.serial_frm.frm_left_combobox_parity.get()
				self.databit = self.serial_frm.frm_left_combobox_databit.get()
				self.stopbit = self.serial_frm.frm_left_combobox_stopbit.get()
				self.ser = SerialHelper(Port=self.port,
				                        BaudRate=self.baudrate,
				                        ByteSize=self.databit,
				                        Parity=self.parity,
				                        Stopbits=self.stopbit)
				
				self.ser.on_connected_changed(self.serial_on_connected_changed)
				
			except Exception as e:
				logging.error(e)
				try:
					self.serial_frm.frm_status_label["text"] = "Open [{0}] Failed!".format(
						self.current_serial_str)
					self.serial_frm.frm_status_label["fg"] = "#DC143C"
				except Exception as ex:
					logging.error(ex)
		
		elif self.serial_frm.frm_left_btn["text"] == "Close":
			self.ser.disconnect()
			self.serial_frm.frm_left_btn["text"] = "Open"
			self.serial_frm.frm_left_btn["bg"] = "#008B8B"
			self.serial_frm.frm_status_label["text"] = "Close Serial Successful!"
			self.serial_frm.frm_status_label["fg"] = "#8DEEEE"
	
	def get_threshold_value(self, *args):
		'''
        get threshold value
        '''
		try:
			self.ser.threshold_value = int(self.serial_frm.threshold_str.get())
		except:
			pass
	
	def serial_on_connected_changed(self, is_connected):
		"""
        串口连接状态改变回调
        """
		if is_connected:
			self.ser.connect()
			if self.ser.is_connected:
				self.serial_frm.frm_status_label["text"] = "Open [{0}] Successful!".format(
					self.current_serial_str)
				self.serial_frm.frm_status_label["fg"] = "#66CD00"
				self.serial_frm.frm_left_btn["text"] = "Close"
				self.serial_frm.frm_left_btn["bg"] = "#F08080"
				
				self.ser.on_data_received(self.serial_on_data_received)
				
			else:
				self.serial_frm.frm_status_label["text"] = "Open [{0}] Failed!".format(
					self.current_serial_str)
				self.serial_frm.frm_status_label["fg"] = "#DC143C"
		else:
			self.ser.disconnect()
			self.serial_frm.frm_left_btn["text"] = "Open"
			self.serial_frm.frm_left_btn["bg"] = "#008B8B"
			self.serial_frm.frm_status_label["text"] = "Close Serial Successful!"
			self.serial_frm.frm_status_label["fg"] = "#8DEEEE"
	
	def serial_on_data_received(self, data):
		"""
        串口接收数据回调函数:只有在串口接收线程里面判断接收到了1行之后才会调用这个函数
        """
		# self.serial_recieve_data += data
		# self.serial_recieve_data_hex = binascii.hexlify(self.serial_recieve_data)
		
		self.receive_data_zxl += data
		
		# 将1s内发送过来的数据集中显示；
		if time.time() - self.time_gap < 1:
			return
		else:
			self.time_gap = time.time()
		
		# #数据量太大的时候，会出现界面（界面卡顿说明是界面部分的代码出问题了）卡顿的现象，于是我们推测是数据量太大了！于是减少显示之！
		# if len(self.receive_data_zxl) >200:
		# 	self.receive_data_zxl = data
		#貌似没效果，看来原因不在这，容后再细细分析
		
		# if  self.ser.threshold_value <= len(self.serial_recieve_data) or self.serial_recieve_data_hex.endswith(END_HEX):
		if self.serial_frm.receive_hex_cbtn_var.get() == 1:
			self.serial_frm.frm_right_receive.insert("end", "[" + str(datetime.datetime.now()) + " - "
			                                         + str(self.serial_receive_count) + "]:\n", "green")
			data_str = " ".join([hex(ord(x))[2:].upper().rjust(
				2, "0") for x in self.receive_data_zxl])
			logging.info("<<<" + str(data_str))
			self.serial_frm.frm_right_receive.insert(
				"end", data_str + "\n")
			self.serial_frm.frm_right_receive.see("end")
		else:
			if self.receive_data_zxl.endswith("\r\n"):
				#把回退符给去掉之后，就没有界面卡顿了，因此我推断这是tkinter处理特殊字符的一个性能bug
				#绝对不是数据量太大的缘故，因为你数据量能有多大，我现在去掉回退符也没少多少数据，但是却不卡了，这说明啥！
				self.receive_data_zxl = self.receive_data_zxl.strip().replace("\b", "")
			
			self.serial_frm.frm_right_receive.insert("end", "[" + str(datetime.datetime.now()) + " - "
			                                         + str(self.serial_receive_count) + "]:\n", "green")
			self.serial_frm.frm_right_receive.insert("end", self.receive_data_zxl + "\n")
			logging.info("<<<" + str(self.receive_data_zxl))
			self.serial_frm.frm_right_receive.see("end")
		self.serial_receive_count += 1
		# self.serial_recieve_data = ""
		self.receive_data_zxl = ""
	
	def find_usb_tty(self, vendor_id=None, product_id=None):
		'''
        查找Linux下的串口设备
        '''
		tty_devs = list()
		for dn in glob.glob('/sys/bus/usb/devices/*'):
			try:
				vid = int(open(os.path.join(dn, "idVendor")).read().strip(), 16)
				pid = int(open(os.path.join(dn, "idProduct")).read().strip(), 16)
				if ((vendor_id is None) or (vid == vendor_id)) and ((product_id is None) or (pid == product_id)):
					dns = glob.glob(os.path.join(
						dn, os.path.basename(dn) + "*"))
					for sdn in dns:
						for fn in glob.glob(os.path.join(sdn, "*")):
							if re.search(r"\/ttyUSB[0-9]+$", fn):
								tty_devs.append(os.path.join(
									"/dev", os.path.basename(fn)))
			except Exception as ex:
				pass
		return tty_devs
	
	
	#########################################################
	#检测函数：
	#  用来做边界检测。
	#########################################################
	def check_luncher(self):
		# 仅检测主界面是否存在哟！
		# waitting for system lunch.
		timeout = 30
		lunched = False
		cmd = "dumpsys activity | grep Focus"
		for i in range(10):
			self.ser.write("TestItem8" + "\n")
			start_time = time.time()
			while (time.time() - start_time) < timeout:
				
				if self.STOP:
					return False
				
				if "com.android.tv.launcher" in self.receive_data_zxl:
					lunched = True
					break
			if lunched == True:
				break
		if lunched == False:
			print ("luncher failed.\r\n")
			return False
		
		print ("luncher success.\r\n")
		return True
	
	def check_sleep_H6(self):
		#无论你是处于什么状态，我都会把你整成休眠状态，至死方休！！！吼~
		# return:
		#   True: enter sleeping.
		#   false: enter sleepMode failed with timeout
		check_sleep_sting = "PM: Entering mem sleep"#"PM: suspend entry"

		self.ser.write("TestItem5" + "\n")
		start_time = time.time()
		while (time.time() - start_time) < 5:
			if check_sleep_sting in self.receive_data_zxl:#有时抓不到这个数据
				return True
			
			if self.STOP:
				return False
		
		return False
	
	def check_wakeup_H6(self):
		# return:
		#   True: wakeup ok.
		#   false: wakeup fail.
		check_wakeup_string = "HDMI"#这个才是屏幕亮了 #"PM: Finishing wakeup"这个屏幕还不一定亮了，只是PMU起来了
		time.sleep(1)
		self.ser.write("TestItem5" + "\r\n")
		start_time = time.time()
		
		while (time.time() - start_time) < 20:
			
			if check_wakeup_string in self.receive_data_zxl:
				return True
			
			if self.STOP:
				return False
		
		return False
	
	def flash_button_color(self):
		# "#DC143C"  # deep red
		# "#F08080"  # light red
		# "#3cb371"  # light green
		# "#006400"  # deep green
		if self.current_clicked_btn == "":
			tkMessageBox.showerror(message='兄弟，这个按键没有设置好把？')
			return
		self.flash_flag = True
		count= 0
		while self.flash_flag:
			#1秒改变一次状态
			if count % 10 == 0:
				if count == 1000:
					count = 0
				if int(count/10)%2:
					self.current_clicked_btn["bg"] = "#F08080"  # light red
				else:
					self.current_clicked_btn["bg"] = "#3cb371"  # light green
				count += 1
			else:
				#提高灵敏度
				count += 1
				time.sleep(0.1)
		#将当前被点击的按钮清除掉
		self.current_clicked_btn = ""
	
	def stop_button_flash(self):
		#stop flash
		self.flash_flag = False
		#wait for flash thread to exit
		while True:
			if self.current_clicked_btn == "":
				break
			else:
				time.sleep(0.1)
		
	def check_before_test(self):
		#仅检测当前是否还有其他的
		try:
			if self.ser and self.ser.is_connected:
				print("serial is opened.\r\n")
		except Exception as e:
			if "has no attribute" in str(e):
				# f = tk.Toplevel(self.root, width=300, height=300)
				# f.title('warnning')
				# lf = tk.Label(f, text='打开串口先！兄弟~')
				# lf.pack()
				# 提出错误对话窗,主界面会等这个错误信息被你关掉之后才会响应
				tkMessageBox.showerror(message='~是不是没打开串口啊？')
				return False
		
		# 检测测试过程中乱按键的情况
		# falsh botton
		# 当我正在测试的时候，你去点了其他的按钮，此时应该被截获的
		if self.current_clicked_btn != "" and self.flash_flag:
			tkMessageBox.showerror(message='等等，别急，让前面的先测完！')
			return False
		
		#如果过五关斩六将你还能活着，那么，你就就是天选之人！
		self.STOP = False
		return True
		
	def writeCMD_check(self, cmd="", check_string="", timeout=30):
		
		Timeout = timeout
		# Cmd = cmd
		# Check_string = check_string
		StartTime = time.time()
		EndTime = time.time()
		
		#check parameter
		if cmd == "" or check_string == "":
			print("\r\nwrong cmd or check_string in writeCMD_check()\r\n")
			return False
		
		#start check
		self.ser.write(cmd + "\n")
		while EndTime - StartTime < Timeout:
			if check_string in self.receive_data_zxl:
				break
			else:
				EndTime = time.time()
		
		# return check outcome.
		if EndTime - StartTime + 0.5 < Timeout:
			return True
		
		return False
	
	def run_memtester(self, size = "128M", circle = "1000"):
		
		run_size = size
		run_circle = circle
	
		END_string = "8-bit Writes"
		START_sting = "memtester version"
		cmd = "TestItem0#/data/memtester {} {} 0 &".format(size, circle)
		
		start_pattern = re.compile(START_sting)
		end_pattern = re.compile(END_string)
		
		self.ser.write(cmd + "\n")
		
		#开四核
		# for i in range(4):
		# 	self.ser.write(cmd + "\n")
			
		StartTime = time.time()
		while True:
			#数据量太大的时候会导致搜索很费时间
			# if len(self.receive_data_zxl) > 100:
			# 	continue
			#if START_sting in self.receive_data_zxl:
			if start_pattern.search(self.receive_data_zxl):
				break
			else:
				time.sleep(0.1)
		Spend_Time = time.time() - StartTime
		self.mem_runtime =  float('%.1f'%Spend_Time)

	def get_current(self, channel = "", timeout = 10):
		#############channel number###############
		# *1: SleepMode: VDD12 Current test
		# *2: RunningMode: VDD12 Current test
		# *3: SleepMode: VDD18 Current test
		# *4: RunningMode: VDD18 Current test
		##########################################
		
		#parameter check
		if channel == "":
			return -10
		
		self.ser.write(channel + "\n")
		
		start_time = time.time()
		end_time = time.time()
		while end_time - start_time < timeout:
			
			#l = "petrel-p1:/ # running mode: VDD12 Current test,The Current is [143.00] mA;"
			
			search_outcome = re.search(r"\[.*?\] mA",self.receive_data_zxl) #self.receive_data_zxl
			#print search_outcome
			if search_outcome:
				#"[123.34] mA"
				#"[123.34]"
				current_block = search_outcome.group().split(' ')[0]
				#"123.34"
				current_str = re.search(r"\d+\.\d+", current_block).group()
				return current_str
			else:
				#之前有匹配不到的情况出现，因为我在这里加了0.1s的间隙，就是这个间隙使得self.receive_data_zxl数据被输出到屏幕然后就被清空了~
				#所以还是一个速度匹配的问题，我只有更快一点才能掌握更多的优先权！
				pass
				
			end_time = time.time()
				
		#timeout return error value
		return -10
	
	
	def all_status_reset(self):
		
		self.serial_frm.frm_right_TestItem_btn_init["text"] = "Init\n reset status"
		self.serial_frm.frm_right_TestItem_btn_init["background"] = "#3cb371"
		
		self.serial_frm.frm_right_TestItem_btn_mainscreen["text"] = "mainscreen current\n reset status"
		self.serial_frm.frm_right_TestItem_btn_mainscreen["background"] = "#3cb371"
		
		self.serial_frm.frm_right_TestItem_btn_SleepTest["text"] = "sleep current\n reset status"
		self.serial_frm.frm_right_TestItem_btn_SleepTest["background"] = "#3cb371"
		
		self.serial_frm.frm_right_TestItem_btn_RunTest["text"] = "memtester+video\n reset status"
		self.serial_frm.frm_right_TestItem_btn_RunTest["background"] = "#3cb371"
		

	
	##################DataBase part#########################
	#
	#
	########################################################
	def Init_TestData(self):
		# 检测文件或者文件夹是否存在,不存在就创建一下！
		#最后是要返回一个文件地址的！
		# pwd = os.getcwd()
		folder_path = os.path.join(os.getcwd(), "TestData")
		if not os.path.exists(folder_path):
			# 创建文件夹
			os.makedirs(folder_path)
		
		#存在的话，我们看下今天的测试文件有木有？
		today_str = time.strftime('%Y%m%d', time.localtime(time.time()))
		file_path = os.path.join(folder_path, today_str + ".csv")
		
		#今天还没存过，那么我就创建一个。
		if not os.path.exists(file_path):
			with open(file_path, 'wb') as csvfile:
				# datetime,TestResult,InitTime,SceneVdd12,SceneVdd18,SleepVdd12,SleepVdd18,MEM+4K
				Item_names = ["datetime", "TestResult", "InitTime", "SceneVdd12", "SceneVdd18", "SleepVdd12", "SleepVdd18", "MEM+4K" ]
				spamwriter = csv.writer(csvfile, dialect='excel')
				spamwriter.writerow(Item_names)
				
		return folder_path,file_path
			
	def record_TestData(self, data):
		with open(self.database_path, 'ab') as csvfile:
			spamwriter = csv.writer(csvfile, dialect='excel')
			spamwriter.writerow(data)
		
	def record_FailLog(self,data):
		#文件夹在软件打开的时候就初始化过了
		
		FailLog_FilePath = os.path.join(self.FailLog_folderPath, "FailLog{}.txt".format(
			time.strftime('%Y%m%d', time.localtime(time.time()))))
		
		# 今天还没存过，那么我就创建一个。
		if not os.path.exists(FailLog_FilePath):
			with open(FailLog_FilePath, 'wb') as f0:
				f0.writelines("============="+time.strftime('[%Y-%m-%d %H:%M:%S] ',time.localtime(time.time())) + " start to record" + "\r\n\r\n")
				
		#直接写进去，没有的话就新建咯！
		with open(FailLog_FilePath, "ab") as f:
			f.writelines(time.strftime('[%Y-%m-%d %H:%M:%S] ',time.localtime(time.time())) + "\r\n\r\n" + data + "\r\n\r\n")
			
			
			
	#########################################################
	#测试函数：
	#  功能测试pattern。
	#########################################################
	
	def TestItem_AutoTesting_caller(self):
		# check
		# is serials open ?
		# 为什么把检查串口放到这里？
		# 因为：第一我的操作步骤里面有sleep操作，因此放到按键回调函数这里会使得界面一卡一卡的；
		# 其次，check_serial_open里面的tkMessageBox函数是不能在线程里面执行的，因此从线程里面提出来，
		# 虽然破坏了一定的简洁性，但是效果还是很不错的嘛！
		if self.check_before_test():
			pass
		else:
			return False
		
		self.start_thread_target(self.TestItem_AutoTesting, name="TestItem_AutoTesting_caller")
	def TestItem_AutoTesting(self):
		print("start to run AutoTesting...\r\n")
		#这个总的按钮是不闪的
		#["TestResult", "InitTime", "MainsceenCurrVDD12", "MainsceenCurrVDD18", "SleepCurrVDD12", "SleepCurrVDD18", "RunappTime" ]
		TestData_line = ["",  "",  "",  "", "", "", "", ""]
		
		# reset all button status
		self.all_status_reset()
		
		#step0: record timestamp
		TestData_line[0] = time.strftime('[%m/%d %H:%M]', time.localtime(time.time()))
		
		#step1: init test
		init_time_str = self.TestItem_Init()
		if init_time_str is not False:
			TestData_line[2] = init_time_str
		#print TestData_line
		
		if self.STOP:
			return False
		
		
		#step2: mainscreen current test
		mainscreen_curr_str = self.TestItem_mainscreen()
		if mainscreen_curr_str[0] is not False:
			TestData_line[3],TestData_line[4] = mainscreen_curr_str
	
		if self.STOP:
			return False
	
		#step3: sleep current test
		sleepcurrent_str = self.TestItem_SleepTest()
		if sleepcurrent_str[0]  is not False:
			TestData_line[5],TestData_line[6] = sleepcurrent_str
			
		if self.STOP:
			return False
		
		#step4: runapp test
		runapp_time_str = self.TestItem_RunTest()
		if runapp_time_str is not False:
			TestData_line[7] = runapp_time_str
			
			
		if self.STOP:
			return False
		
		
		
		#step5: check Item outcome
		for i in range(len(TestData_line)):
			if i == 0:
				pass
			else:
				if TestData_line[i] == "":
					#fail
					TestData_line[1] = "fail"
					self.record_TestData(TestData_line)
					self.serial_frm.frm_right_TestItem_btn_AutoTest["bg"] = "#DC143C"  # deep red
					self.TestItem_SysPoweroff()
					return False
				
		if self.STOP:
			return False
			
		#step6: write test date to database
		TestData_line[1] = "pass"
		self.record_TestData(TestData_line)
		self.serial_frm.frm_right_TestItem_btn_AutoTest["bg"] = "#006400"  # deep green
		
		#step7: system down and power off
		self.TestItem_SysPoweroff()
		
		
	def TestItem_Init_caller(self):
		# 界面函数里面不能用延时，因此单独开一个线程来做有延时的操作；
		# 界面回调函数是在toplevel层运行的，因此只要有延时就会使得界面卡住；
		
		# #这兄弟有最高权限
		# #先强行停止闪烁
		# self.stop_button_flash()
		#
		#注意此时之前的测试项还是在跑的，但是我们直接跑初始化，即重启，了！但是被打断的线程还在继续，因此这里是有bug的，我暂时不加这个功能。
		# is serials open ?
		if self.check_before_test():
			pass
		else:
			return False
		
		
		self.start_thread_target(self.TestItem_Init, name="TestItem_Init_caller")
	def TestItem_Init(self):
		
		# record test time.
		self.Item_testtime = time.time()
		
		# 初始化：先断电再上电，并检测是否正常开机
		print("$LPDDR3$: start to Init...\r\n")
		#
		self.serial_frm.frm_right_TestItem_btn_init["text"] = "Init\n  start..."
		
		# falsh botton
		# ----clear status
		if self.flash_flag:
			self.flash_flag = False
			time.sleep(0.3)
			self.flash_flag = True
		else:
			self.flash_flag = True
		# ---run a thread to flash button.
		
		# 注意一下这里，那些按键都是在serial_frm这个框下面建立的，我刚是直接漏过这步去调按键，当然找不到啊！
		self.current_clicked_btn = self.serial_frm.frm_right_TestItem_btn_init
		# self.start_thread_timer(self.flash_button_color, 1)
		self.start_thread_target(self.flash_button_color)
		
		# # power off
		# print("$LPDDR3$: start power off.\r\n")
		# self.ser.write("poweroff" + "\n")
		# time.sleep(1)
		
		# power on
		print("$LPDDR3$: start power on.\r\n")
		self.ser.write("poweron" + "\n")
		
		# check is power on?
		##how many lines have received!
		self.serial_receive_count = 0
		# wait until system on
		
		timeout = 30
		StartTime = time.time()
		EndTime = time.time()
		while EndTime - StartTime < timeout:
			
			if self.STOP:
				return False
			
			if "psci: CPU1 killed" in self.receive_data_zxl:
				break
			else:
				pass
			# print("waitting for system on.\r\n")
			EndTime = time.time()
		
		if EndTime - StartTime + 0.5 < timeout:
			print("$LPDDR3$: system booting success.\r\n")
		else:
			print("$LPDDR3$: system booting fail.\r\n")
			# stop falsh button
			self.flash_flag = False
			time.sleep(0.5)
			self.serial_frm.frm_right_TestItem_btn_init["bg"] = "#DC143C"  # deep red
			return False
		# init state, send "su" to H6
		StartTime = time.time()
		EndTime = time.time()
		while EndTime - StartTime < timeout:
			#在耗时的部分加入全局停止检测
			if self.STOP:
				return False
			
			self.ser.write("TestItem9" + "\n")
			# key words: petrel-p1:/ #
			# 因为显示那里的优先级高一些啊，显示完之后就清空了
			# 因此我这里大概率是抢不到值的，因此我在显示那里开启“储水”1s，然后送显示，这样子我就有可能及时的查看到数据
			# 利用一个时间差，你死命地清空，我都看不清了，但是你慢一点搬的话，我就可以借机瞄两眼；
			# 这里的思路就是这样，嘿~挺巧妙的，真有趣! 这世界！
			if "petrel-p1:/ #" in self.receive_data_zxl:
				break
			else:
				time.sleep(0.2)
		if EndTime - StartTime + 0.5 < timeout:
			print("$LPDDR3$: system on success.\r\n")
		else:
			print("$LPDDR3$: system on fail.\r\n")
			self.flash_flag = False
			time.sleep(0.5)
			self.serial_frm.frm_right_TestItem_btn_init["bg"] = "#DC143C"  # deep red
			return False
		
		if self.check_luncher():
			self.flash_flag = False
			time.sleep(0.5)
			self.serial_frm.frm_right_TestItem_btn_init["bg"] = "#006400"  # deep green
			print("$LPDDR3$: Init test PASS.\r\n")
			self.Item_testtime = time.time() - self.Item_testtime
			self.serial_frm.frm_right_TestItem_btn_init["text"] = "Init\nTime={}s".format(
				float("%.1f" % self.Item_testtime))
			return str(float("%.1f" % self.Item_testtime))
		else:
			self.flash_flag = False
			time.sleep(0.5)
			# change button color from light red to deep red meanning "testing fail".
			self.serial_frm.frm_right_TestItem_btn_init["bg"] = "#DC143C"  # deep red
			print("$LPDDR3$: check luncher fail.\r\n")
			return False
	

	def TestItem_mainscreen_caller(self):
		# is serials open ?
		if self.check_before_test():
			pass
		else:
			return False
		
		self.start_thread_target(self.TestItem_mainscreen, name="TestItem_mainscrren_caller")
	def TestItem_mainscreen(self):
		#主界面下的电流测试
		# record test time.
		self.Item_testtime = time.time()
		
		print("$LPDDR3$: start to mainscreen...\r\n")
		
		# 1 先改变按钮的显示状态
		self.serial_frm.frm_right_TestItem_btn_mainscreen["text"] = "mainscreen\n  start..."
		
		# 2 开线程开始闪烁按钮：
		# 注意一下这里，那些按键都是在serial_frm这个框下面建立的，我刚是直接漏过这步去调按键，当然找不到啊！
		self.current_clicked_btn = self.serial_frm.frm_right_TestItem_btn_mainscreen
		self.start_thread_target(self.flash_button_color)
		
		# 是使得H6在开机状态下回到主界面；
		# 测试主界面下的电流值
		# print("$LPDDR3$: start to back to mainscreen.\r\n")
		# self.ser.write("TestItem6" + "\n")
		#
		# StartTime = time.time()
		# EndTime = time.time()
		# while EndTime - StartTime < self.TIME_OUT:
		# 	if self.check_luncher():
		# 		break
		# 	else:
		# 		pass
		# 	# print("waitting for system on.\r\n")
		# 	EndTime = time.time()
		#
		# if EndTime - StartTime + 0.5 < self.TIME_OUT:
		# 	print("$LPDDR3$: back to mainscreen success.\r\n")
		# else:
		# 	print("$LPDDR3$: back to mainscreen fail.\r\n")
		# 	# stop falsh button
		# 	self.stop_button_flash()
		# 	time.sleep(0.3)
		# 	self.serial_frm.frm_right_TestItem_btn_mainscreen["bg"] = "#DC143C"  # deep red
		# 	return False
		
		
		
		
		#VDD1.8 current test @running mode ===> TestItem4
		current_VDD18_str = self.get_current(channel="TestItem4")
		
		if type(current_VDD18_str) is int and current_VDD18_str < 0:
			print("cant get current value, please check error.\r\n")
			self.stop_button_flash()
			time.sleep(0.3)
			self.serial_frm.frm_right_TestItem_btn_mainscreen["text"] = "mainscreen\n  END"
			self.serial_frm.frm_right_TestItem_btn_mainscreen["bg"] = "#DC143C"  # deep red
			return False,False
		
		
		#flush serial buffer
		self.receive_data_zxl = ""
		time.sleep(3)
		
		##########################################################################
		# VDD1.2V running mode
		currentVDD12_str = self.get_current(channel="TestItem2")
		
		if type(currentVDD12_str) is int and currentVDD12_str < 0:
			print("cant get current value, please check error.\r\n")
			self.stop_button_flash()
			time.sleep(0.3)
			self.serial_frm.frm_right_TestItem_btn_mainscreen["text"] = "mainscreen\n  END"
			self.serial_frm.frm_right_TestItem_btn_mainscreen["bg"] = "#DC143C"  # deep red
			return False,False
		else:
			print("$LPDDR3$: Init test PASS.\r\n")
			self.stop_button_flash()
			self.serial_frm.frm_right_TestItem_btn_mainscreen["bg"] = "#006400"  # deep green
			self.Item_testtime = time.time() - self.Item_testtime
			self.serial_frm.frm_right_TestItem_btn_mainscreen["text"] = "MainScr&Curr\n Time={}s\n ".format(float("%.1f" % self.Item_testtime)) \
																			+ "VDD1.2="+str(currentVDD12_str) + "mA\n" \
																			+ "VDD1.8=" + str(current_VDD18_str) + "mA"
			return currentVDD12_str,current_VDD18_str
	

	
	def TestItem_SleepTest_caller(self):
		# is serials open ?
		if self.check_before_test():
			pass
		else:
			return False
		
		self.start_thread_target(self.TestItem_SleepTest, name="TestItem_SleepTest_caller")
	def TestItem_SleepTest(self):
		
		# 休眠的电流测试
		# record test time.
		self.Item_testtime = time.time()
		
		print("$LPDDR3$: start  sleeptest...\r\n")
		
		# 1 先改变按钮的显示状态
		self.serial_frm.frm_right_TestItem_btn_SleepTest["text"] = "SleepCurr\n  start..."
		
		# 2 开线程开始闪烁按钮：
		# 注意一下这里，那些按键都是在serial_frm这个框下面建立的，我刚是直接漏过这步去调按键，当然找不到啊！
		self.current_clicked_btn = self.serial_frm.frm_right_TestItem_btn_SleepTest
		self.start_thread_target(self.flash_button_color)
		
		
		#do slep and check
		#有时一次是抓不到的，我把一次检测的时间由原来的15s减为5s，这里外面再多检查几次，从而增强鲁棒性
		sleep_state = False
		for i in range(3):
			if self.check_sleep_H6() is True:
				sleep_state = True
				break
			else:
				continue
		if sleep_state is False:
			self.stop_button_flash()
			self.serial_frm.frm_right_TestItem_btn_SleepTest["bg"] = "#DC143C"  # deep red
			self.Item_testtime = time.time() - self.Item_testtime
			self.serial_frm.frm_right_TestItem_btn_SleepTest["text"] = "EnterSleep Fail!\n Time={}s".format(
				float("%.1f" % self.Item_testtime))
			return False,False
			
			
		
		time.sleep(2)
		
		# VDD1.8V running mode
		current_VDD18_str = self.get_current(channel="TestItem3")
		print("current_VDD18_str=",current_VDD18_str)
		if type(current_VDD18_str) is int and current_VDD18_str < 0:
			# 整醒~
			self.check_wakeup_H6()
			self.stop_button_flash()
			self.Item_testtime = time.time() - self.Item_testtime
			self.serial_frm.frm_right_TestItem_btn_SleepTest["text"] = "SleepCurr Fail!\n Time={}s".format(
				float("%.1f" % self.Item_testtime))
			self.serial_frm.frm_right_TestItem_btn_SleepTest["bg"] = "#DC143C"  # deep red
			return False,False  # -10 means fail


		#因为测完VDD1.8之后，马上就检测VDD1.2由于在0.5s内吧！导致缓冲区里面VDD1.8的排在前面且没有被flush掉，因此后面的也认为如此了！
		#flush handly
		# flush buffer
		self.receive_data_zxl = ""
		time.sleep(2)


		# VDD1.2V running mode
		currentVDD12_str = self.get_current(channel="TestItem1")
		

		
		#先保证能起来
		if self.check_wakeup_H6() is False:
			self.stop_button_flash()
			self.Item_testtime = time.time() - self.Item_testtime
			self.serial_frm.frm_right_TestItem_btn_SleepTest["text"] = "cant wakeup\n Time={}s\n ".format(
				float("%.1f" % self.Item_testtime)) + "VDD1.2=" + str(currentVDD12_str) + "mA" + "\nVDD1.8=" + str(
				current_VDD18_str) + "mA"
			self.serial_frm.frm_right_TestItem_btn_SleepTest["bg"] = "#DC143C"  # deep red
			return False,False
		
		
		if type(currentVDD12_str) is int and currentVDD12_str < 0:
			print("cant get current value, please check error.\r\n")
			self.stop_button_flash()
			self.Item_testtime = time.time() - self.Item_testtime
			self.serial_frm.frm_right_TestItem_btn_SleepTest["text"] = "SleepCurr Fail!\n Time={}s".format(
				float("%.1f" % self.Item_testtime))
			self.serial_frm.frm_right_TestItem_btn_SleepTest["bg"] = "#DC143C"  # deep red
			return False,False
		else:
			print("$LPDDR3$: sleep current test PASS.\r\n")
			self.stop_button_flash()
			self.serial_frm.frm_right_TestItem_btn_SleepTest["bg"] = "#006400"  # deep green
			self.Item_testtime = time.time() - self.Item_testtime
			self.serial_frm.frm_right_TestItem_btn_SleepTest["text"] = "SleepCurr\n Time={}s\n ".format(
				float("%.1f" % self.Item_testtime)) + "VDD1.2=" +str(currentVDD12_str) + "mA" + "\nVDD1.8="+str(current_VDD18_str)+"mA"
			return currentVDD12_str,current_VDD18_str
	
	
	def TestItem_RunTest_caller(self):
		# 界面函数里面不能用延时，因此单独开一个线程来做有延时的操作；
		# 界面回调函数是在toplevel层运行的，因此只要有延时就会使得界面卡住；
		
		# is serials open ?
		if self.check_before_test():
			pass
		else:
			return False
		
		self.start_thread_target(self.TestItem_RunTest, name="TestItem_RunTest_caller")
	def TestItem_RunTest(self):
		
		# record test time.
		self.Item_testtime = time.time()
		
		# 0 初始化：先断电再上电，并检测是否正常开机
		print("$LPDDR3$: start to RunTest...\r\n")
		
		# 1 先改变按钮的显示状态
		self.serial_frm.frm_right_TestItem_btn_RunTest["text"] = "RunTest\n  start..."
		
		# 2 开线程开始闪烁按钮：
		# 注意一下这里，那些按键都是在serial_frm这个框下面建立的，我刚是直接漏过这步去调按键，当然找不到啊！
		self.current_clicked_btn = self.serial_frm.frm_right_TestItem_btn_RunTest
		self.start_thread_target(self.flash_button_color)
		
		# 3 发送指令并检测
		# 3.1 for sure: get root authority;
		self.ser.write("TestItem9" + "\n")
		
		# 3.2 run memtester
		# Mode：blocked
		# self.start_thread_target(self.run_memtester, name="TestItem_run_memtester_caller")
		time.sleep(0.1)
		# just send am instryction instead.
		self.ser.write(
			"TestItem0#am start -n com.softwinner.TvdVideo/.TvdVideoActivity -d /sdcard/Movies/4K-super_car2.mp4\r\n")
		time.sleep(3)
		
		time.sleep(0.1)
		self.ser.write("TestItem0#echo 8 >/proc/sysrq-trigger\r\n")
		time.sleep(0.1)
		self.run_memtester(size="128M", circle="1000")
		# 191.8s
		print("memtester 128M 1 ,startup spend time = %.1f" % self.mem_runtime)
		
		# 3.3 start uiautomator and check
		print("$LPDDR3$: start to run Uiautomator.\r\n")
		key_string = "cpufreq max to 1800000 min to 816000"
		
		# run uiautomator success
		# if self.writeCMD_check(cmd="TestItem7", check_string=key_string, timeout=30):
		# 	# 6s检测到
		# 	print("runapp startup time:%ds" % (time.time() - self.Item_testtime))
		# else:
		# 	# 由于系统压力很大，这个不一定检测的到
		# 	# self.stop_button_flash()
		# 	# self.serial_frm.frm_right_TestItem_btn_RunTest["bg"] = "#DC143C"  # deep red
		# 	print("$LPDDR3$: run test app fail.\r\n")
		
		
		
		# during test: check everithing ok?
		#
		# 在memtester和视频播放起来后，是可以让他一直播放的，
		# 我们要做的是检测其中memtester是否会报错，以及系统是否卡死
		#########################################
		test_time = 200
		start_time = time.time()
		systemdown_starttime = time.time()
		test_status = ""
		while time.time() - start_time < test_time:
			if self.STOP ==  True:
				return False
			if self.receive_data_zxl == "":
				if time.time() - systemdown_starttime > 30:
					# 系统死机
					test_status = "systemdown"
					break
				else:
					systemdown_starttime = time.time()
			if "FAILURE:" in self.receive_data_zxl:
				self.record_FailLog(self.receive_data_zxl)
				#这里可能会有问题，公共资源我强制占用可能会导致界面那显示不出来
				#这里想解决的问题是：假如我写完之后不清空，那么很有可能就是重复写进log文件了，存在的问题是清空了就不能在界面显示了
				self.receive_data_zxl = ""
				test_status = "mem_failure"
			# print("am i stucking here?\r\n")
		
		if (test_status == "systemdown") or (test_status == "mem_failure"):
			self.stop_button_flash()
			self.serial_frm.frm_right_TestItem_btn_RunTest["bg"] = "#DC143C"  # deep red
			self.serial_frm.frm_right_TestItem_btn_RunTest["text"] = test_status + "\n Fail!!!"
			print("$LPDDR3$: run test app fail.\r\n")
			return False
		else:
			self.stop_button_flash()
			self.serial_frm.frm_right_TestItem_btn_RunTest["bg"] = "#006400"  # deep green
			self.Item_testtime = time.time() - self.Item_testtime
			self.serial_frm.frm_right_TestItem_btn_RunTest["text"] = "Runapp\n Time={}s".format(
				float("%.1f" % self.Item_testtime))
			return str(float("%.1f" % self.Item_testtime))
		
		# #一定得等4K视频播放完，否则会延迟执行
		# #back to mainscreen
		# self.ser.write("TestItem6" + "\n")
		# #wait to back to mainscreen:
		# # 因为播放4K视频加跑memtester会产生很大压力，从而通过串口发送的指令很可能无法马上被检测到并执行，因此等一会吧！
		#
		# if self.check_luncher():
		# 	self.stop_button_flash()
		# 	self.serial_frm.frm_right_TestItem_btn_RunTest["bg"] = "#006400"  # deep green
		# 	print("$LPDDR3$: Init test PASS.\r\n")
		# 	self.Item_testtime = time.time() - self.Item_testtime
		# 	self.serial_frm.frm_right_TestItem_btn_RunTest["text"] = "Runapp\n Time={}s".format(float("%.1f" % self.Item_testtime))
		# 	return str(float("%.1f" % self.Item_testtime))
		# else:
		# 	self.stop_button_flash()
		# 	self.serial_frm.frm_right_TestItem_btn_RunTest["bg"] = "#DC143C"  # deep red
		# 	self.serial_frm.frm_right_TestItem_btn_RunTest["text"] = "Runapp+mem\n Fail!!!"
		# 	print("$LPDDR3$: run test app fail.\r\n")
		# 	return False
	
	
	def TestItem_SysPoweroff_caller(self):
		# is serials open ? NO!!!最高权限
		# if self.check_before_test():
		# 	pass
		# else:
		# 	return False
		self.start_thread_target(self.TestItem_SysPoweroff, name="TestItem_SysPoweroff_caller")
	def TestItem_SysPoweroff(self):
		# 初始化界面
		# 全局停止标志
		self.STOP = True
		self.stop_button_flash()
		
		self.ser.write("TestItem0#reboot -p\r\n")
		time.sleep(2)
		self.ser.write("poweroff\r\n")


if __name__ == '__main__':
	'''
    main loop
    '''

	#for matplot in canvas in notebook.
	matplotlib.use('TkAgg')
	
	root = tk.Tk()
	root.columnconfigure(0, weight=1)
	root.rowconfigure(0, weight=1)
	root.geometry()
	root.title("LPDDR3_FT Tester(Serial)")
	
	monacofont = tkFont.Font(family="Monaco", size=16)
	root.option_add("*TCombobox*Listbox*background", "#292929")
	root.option_add("*TCombobox*Listbox*foreground", "#FFFFFF")
	root.option_add("*TCombobox*Listbox*font", monacofont)
	
	root.configure(bg="#292929")
	combostyle = ttk.Style()
	combostyle.theme_use('default')
	combostyle.configure("TCombobox",
	                     selectbackground="#292929",
	                     fieldbackground="#292929",
	                     background="#292929",
	                     foreground="#FFFFFF")
	
	
	app = MainSerialTool(root)
	
	if os.name == 'nt':  # 判断现在正在实用的平台，Windows 返回 ‘nt'; Linux 返回’posix'
		root.iconbitmap(default='swallow_128px_1139556_easyicon.net.ico')

	root.mainloop()
