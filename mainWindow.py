#!/usr/bin/python
# -*- coding: utf-8 -*-
#mainWindow.py
from PyQt4 import QtGui, QtCore, uic
import mlpCanvas
import datetime, sys

class QMainWindow(QtGui.QMainWindow):
	def __init__(self):
		super(QMainWindow,self).__init__()
		self.initUI()
	#初始化窗口布局
	def initUI(self):
		uic.loadUi('ui/mainWindows.ui', self)
		self.setWindowTitle(u'统计套利信号客户端')
		self.statusBar().showMessage(u'已连接服务器')
		#设置画布
		dc = mlpCanvas.MLPDynamicMplCanvas(self)
		self.verticalLayout.addWidget(dc)
		#设置表格
		self.messageTableWidget.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
		self.messageTableWidget.resizeColumnsToContents()
	#控制方法
	#显示行情时间
	def showMarketTime(self, marketTime):
		self.marketTime_LCD.display(marketTime)
	#显示本地时间
	def showLocalTime(self, localTime):
		self.localTime_LCD.display(localTime)
