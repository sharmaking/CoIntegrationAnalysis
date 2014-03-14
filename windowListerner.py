#!/usr/bin/python
# -*- coding: utf-8 -*-
#windowListerner.py
from PyQt4 import QtCore
import datetime

class QWindowListerner(QtCore.QThread):
	def __init__(self, Qmain, messageBox):
		super(QWindowListerner,self).__init__()
		self.Qmain = Qmain
		self.messageBox = messageBox

	def __del__(self):
		self.wait()

	def run(self):
		while True:
			while not self.messageBox.empty():
				systemMessage = self.messageBox.get()
				if systemMessage[0] == 0:	#初始化参数表
					self.Qmain.getPairPara(systemMessage[1])
				elif systemMessage[0] == 1:	#显示时间
					self.Qmain.showMarketTime(str(systemMessage[1])[5:19])
					self.Qmain.showLocalTime(str(datetime.datetime.now().time())[:8])
				elif systemMessage[0] == 2:	#配对股票策略值的情况
					self.Qmain.getPairValue(systemMessage[1])
			pass
		pass
 		self.terminate()