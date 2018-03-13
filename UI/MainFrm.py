#! /usr/bin/env python
# -*- coding: utf-8 -*-

import ttk
import tkFont
import Tkinter as tk
import datetime,os
import threading

import PyTkinter as pytk
from SerialFrm import SerialFrame
from PIL import ImageTk, Image
g_font = ("Monaco", 16)


class MainFrame(object):
    '''
    main frame
    '''

    def __init__(self, master=None):
        '''
        constructor
        '''
        self.root = master
        self.create_frame()

        self.state = True
        # self.root.attributes("-fullscreen", self.state)
        
        self.root.bind("<F11>", self.toggle_fullscreen)
        # self.root.bind("<Key-space>", self.TestItem_AutoTesting_caller)
        
    def create_frame(self):
        self.frm_main = pytk.PyLabelFrame(self.root)
        self.frm_main.pack(fill="both", expand=1)

        self.create_frm_main()

        self.init_serial_frm()

    def create_frm_main(self):
        self.serial_frm = SerialFrame(self.frm_main)
        self.serial_frm.frm.pack(fill="both", expand=1, padx=2, pady=2)

    def show_current_time(self):
        '''
        show computer current date
        '''
        self.frm_status_bottom_label_date["text"] = str(datetime.datetime.now())[:-7]
        self.root.after(2**8, self.show_current_time)

    def toggle_fullscreen(self, event=None):
        '''
        toggle fullscreen
        '''
        self.state = not self.state
        self.root.attributes("-fullscreen", self.state)

    def init_serial_frm(self):
        '''
        init serial frm
        '''
        self.serial_frm.frm_left_btn["command"] = self.Toggle
        self.serial_frm.frm_left_listbox.bind("<Double-Button-1>", self.Toggle)
        self.serial_frm.frm_right_send_btn["command"] = self.Send
        self.serial_frm.frm_right_clear_btn["command"] = self.SerialClear
        self.serial_frm.threshold_str.set(100)
        self.serial_frm.threshold_str.trace('w', self.get_threshold_value)

        self.serial_frm.frm_right_TestItem_btn_AutoTest["command"] = self.TestItem_AutoTesting_caller
        self.serial_frm.frm_right_TestItem_btn_init["command"] = self.TestItem_Init_caller
        self.serial_frm.frm_right_TestItem_btn_RunTest["command"] = self.TestItem_RunTest_caller
        self.serial_frm.frm_right_TestItem_btn_mainscreen["command"] = self.TestItem_mainscreen_caller
        self.serial_frm.frm_right_TestItem_btn_SysPoweroff["command"] = self.TestItem_SysPoweroff_caller
        self.serial_frm.frm_right_TestItem_btn_SleepTest["command"] = self.TestItem_SleepTest_caller
        
    def Toggle(self, event=None):
        '''
        toggle dev
        '''
        pass

    def Send(self):
        '''
        send msg to dev
        '''
        pass


#######################################################
    #
    #测试函数体
    #
#######################################################
    def TestItem_AutoTesting_caller(self):
        pass
    
    def TestItem_mainscreen_caller(self):
        # to check if the launcher running.
        #   ---if can not power on then checked.
        pass

    def TestItem_RunTest_caller(self):
        pass

    def TestItem_SysPoweroff_caller(self):
        pass

    def TestItem_SleepTest_caller(self):
        pass
    
    def TestItem_Init_caller(self):
        pass
 ##########################################################
    
    
    
    def SerialClear(self):
        '''
        clear serial recieve text
        '''
        pass

    def UsbClear(self):
        '''
        clear usb recieve text
        '''
        pass

    def get_threshold_value(self, *args):
        '''
        get threshold value
        '''
        pass

    def start_thread_timer(self, callback, timer=1):
        '''
        util: start thread timer
        '''
        temp_thread = threading.Timer(timer, callback)
        temp_thread.setDaemon(True)
        temp_thread.start()

    def start_thread_target(self, callback, name="thread"):
        '''
        util: start thread target
        '''
        print("Tread name is {}".format(name))
        temp_thread = threading.Thread(target=callback, name=name)
        temp_thread.setDaemon(True)
        temp_thread.start()




if __name__ == '__main__':
    '''
    main loop
    '''
    root = tk.Tk()
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    root.geometry()

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

    app = MainFrame(root)
    
    root.mainloop()
