# import matplotlib.pyplot as plt
# import csv
# import re
# with open("testoutcome.csv","rb") as csvfile:
# 	reader = csv.reader(csvfile)#, dialect='excel'
# 	for row in reader:
# 		if "VDD12" in row[0]:
#


# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt

name_list = ['<0.5mA',"0.5mA<I<2mA","Fail"]
num_list = [1.5]
num_list1 = [1]
plt.bar(range(len(num_list)), num_list, label='Pass', fc='y')
plt.bar(range(len(num_list)), num_list1, bottom=num_list, label='Fail', tick_label=name_list, fc='r')
plt.title("VDD1.8")
plt.legend()
plt.show()