#!/usr/bin/python
# -*- coding: utf-8 -*-
#windowController.py
from PyQt4 import QtGui
import sys, multiprocessing
import mainWindow, windowListerner

class QWindowsController(multiprocessing.Process):
	def __init__(self, messageBox):
		super(QWindowsController, self).__init__()
		self.messageBox = messageBox

	def run(self):
		app = QtGui.QApplication(sys.argv)
		QMain = mainWindow.QMainWindow()
		#界面信息处理线程
		wListerner = windowListerner.QWindowListerner(QMain, self.messageBox)
		wListerner.start()
		#显示主窗口
		QMain.show()
		sys.exit(app.exec_())
