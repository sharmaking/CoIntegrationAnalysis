#!/usr/bin/python
# -*- coding: utf-8 -*-
#pairDetailDialogWindow.py
from PyQt4 import QtGui, QtCore, uic
import mlpCanvas

class QPairDetailDialogWindow(QtGui.QDialog):
	def __init__(self, QMain):
		super(QPairDetailDialogWindow,self).__init__(parent = QMain)
		self.QMain = QMain
		self.initUI()
		self.initEventConnection()
	#初始化窗口布局
	def initUI(self):
		uic.loadUi('ui/pairDetailDialog.ui', self)
		self.setWindowTitle(u'记录备注')
		#设置画布
		#self.dc = mlpCanvas.MLPDynamicMplCanvas(self)
		#self.verticalLayout.addWidget(self.dc)
	#初始化窗口元件事件关联
	def initEventConnection(self):
		#对话提交
		self.buttonBox.accepted.connect(self.accept) # 确定
		self.buttonBox.rejected.connect(self.reject) # 取消
	#得到真实交易点
	def getComment(self):
		comment = self.textEdit.document().toPlainText()
		comment = QtCore.QTextCodec.toUnicode(u"备注")
		print comment
		return str(comment)