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
		self.linkObjDict = {}
		self.standardPriceDeviation = [[],[]]
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

def main():
	app = QtGui.QApplication(sys.argv)
	QMain = QMainWindow()
	#显示主窗口
	QMain.show()
	sys.exit(app.exec_())
	pass

if __name__ == '__main__':
	main()
