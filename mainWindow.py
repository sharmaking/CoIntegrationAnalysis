#!/usr/bin/python
# -*- coding: utf-8 -*-
#mainWindow.py
from PyQt4 import QtGui, QtCore, uic
import mlpCanvas
import datetime, sys, time

class QMainWindow(QtGui.QMainWindow):
	def __init__(self):
		super(QMainWindow,self).__init__()
		self.initUI()
		self.initEventConnection()
		self.curPairKey = ""
		self.pairPara = {}			#配对参数
		self.pairTradeStatus = {}	#配对交易状态
	#初始化窗口布局
	def initUI(self):
		uic.loadUi('ui/mainWindows.ui', self)
		self.setWindowTitle(u'统计套利信号客户端')
		self.statusBar().showMessage(u'已连接服务器')
		#设置画布
		self.dc = mlpCanvas.MLPDynamicMplCanvas(self)
		self.verticalLayout.addWidget(self.dc)
		#设置表格
		self.messageTableWidget.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)	#自动设置宽度
		self.messageTableWidget.horizontalHeader().setStretchLastSection(True)
		self.messageTableWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)	#设置选择行为，以行为单位
		self.messageTableWidget.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)	#设置选择模式，选择单行
		self.messageTableWidget.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)		#禁止编辑
	#初始化窗口元件事件关联
	def initEventConnection(self):
		self.pairlistWidget.itemDoubleClicked.connect(self.showSelectPairDetail)
		#self.connect(self.pairlistWidget, QtCore.SIGNAL('itemDoubleClicked()'),
        #    self.showSelectPairDetail)
	#------------------------------
	#后台策略方法
	#------------------------------
	#显示行情时间
	def showMarketTime(self, marketTime):
		self.marketTime_LCD.display(marketTime)
	#显示本地时间
	def showLocalTime(self, localTime):
		self.localTime_LCD.display(localTime)
	#获取参数表
	def getPairPara(self, pairPara):
		self.pairPara = pairPara
		for key, para in sorted(self.pairPara.items(), key=lambda d:d[0]):
			self.pairlistWidget.addItem(key)
			self.pairTradeStatus[key] = {"datas":[], "tradPoint":[]}
		self.pairNumLabel.setText(str(len(self.pairPara)))
		time.sleep(1)
		self.setCurrentPair(self.pairPara.items()[0][0])
	#获得配对参数
	def getPairValue(self, pairValue):
		pairKey, valuetime, pa, pb, value = pairValue
		self.pairTradeStatus[pairKey]["pa"] = pa
		self.pairTradeStatus[pairKey]["pb"] = pb
		self.pairTradeStatus[pairKey]["datas"].append((valuetime, value))
		#显示参数
		if pairKey == self.curPairKey:
			self.stockAPriceLabel.setText(str(pa))
			self.stockBPriceLabel.setText(str(pb))
			self.valueLabel.setText(str(value))
	#显示开平仓信号
	def getTradeMessage(self, tradeMessage):
		self.messageTableWidget.setRowCount(self.messageTableWidget.rowCount() + 1)
		self.pairTradeStatus[tradeMessage["pairKey"]]["tradPoint"].append(tradeMessage)
		if tradeMessage["type"] == "open":
			itemRow = self.formartTradeMessage(tradeMessage, "open")
			for i in xrange(len(itemRow)):
				self.messageTableWidget.setItem(self.messageTableWidget.rowCount()-1,i,itemRow[i])
		elif tradeMessage["type"] == "close":
			itemRow = self.formartTradeMessage(tradeMessage, "close")
			for i in xrange(len(itemRow)):
				self.messageTableWidget.setItem(self.messageTableWidget.rowCount()-1,i,itemRow[i])
		elif tradeMessage["type"] == "stop":
			itemRow = self.formartTradeMessage(tradeMessage, "stop")
			for i in xrange(len(itemRow)):
				self.messageTableWidget.setItem(self.messageTableWidget.rowCount()-1,i,itemRow[i])
		pass
	def formartTradeMessage(self, tradeMessage, tradeType):
		itemRow = [
			QtGui.QTableWidgetItem(str(tradeMessage["pairKey"])),
			QtGui.QTableWidgetItem(str(tradeMessage["type"])),
			QtGui.QTableWidgetItem(str(tradeMessage["dateTime"])[:19]),
			QtGui.QTableWidgetItem(str(tradeMessage["beta"])),
			#------stock_a
			QtGui.QTableWidgetItem(str(tradeMessage["stock_A"])),
			QtGui.QTableWidgetItem(str(tradeMessage["dirc_A"])),
			QtGui.QTableWidgetItem(str(tradeMessage["pa"])),
			#QtGui.QTableWidgetItem(str(tradeMessage["vol_a"])),
			#------stock_b
			QtGui.QTableWidgetItem(str(tradeMessage["stock_B"])),
			QtGui.QTableWidgetItem(str(tradeMessage["dirc_B"])),
			QtGui.QTableWidgetItem(str(tradeMessage["pb"])),
			#QtGui.QTableWidgetItem(str(tradeMessage["vol_b"]))
			]
		if tradeType == "open":
			itemRow.insert(7, QtGui.QTableWidgetItem(str(tradeMessage["vol_a"])))
			itemRow.insert(11, QtGui.QTableWidgetItem(str(tradeMessage["vol_b"])))
			#for item in itemRow:
			#	item.setBackground(QtGui.QColor(233,248,254,100))
		elif tradeType == "close":
			itemRow.insert(7, QtGui.QTableWidgetItem(str(tradeMessage["ratio_A"])))
			itemRow.insert(11, QtGui.QTableWidgetItem(str(tradeMessage["ratio_B"])))
			itemRow.insert(12, QtGui.QTableWidgetItem(str(tradeMessage["ratio"])))
			for item in itemRow:
				item.setBackground(QtGui.QColor(252,221,222,100))
		elif tradeType == "stop":
			itemRow.insert(7, QtGui.QTableWidgetItem(str(tradeMessage["ratio_A"])))
			itemRow.insert(11, QtGui.QTableWidgetItem(str(tradeMessage["ratio_B"])))
			itemRow.insert(12, QtGui.QTableWidgetItem(str(tradeMessage["ratio"])))
			for item in itemRow:
				item.setBackground(QtGui.QColor(226,244,235,100))
		#stock_a_direction
		if tradeMessage["dirc_A"] == "buy":
			itemRow[5].setForeground(QtGui.QColor("red"))
			itemRow[6].setForeground(QtGui.QColor("red"))
		else:
			itemRow[5].setForeground(QtGui.QColor("green"))
			itemRow[6].setForeground(QtGui.QColor("green"))
		#stock_b_direction
		if tradeMessage["dirc_B"] == "buy":
			itemRow[9].setForeground(QtGui.QColor("red"))
			itemRow[10].setForeground(QtGui.QColor("red"))
		else:
			itemRow[9].setForeground(QtGui.QColor("green"))
			itemRow[10].setForeground(QtGui.QColor("green"))
		return itemRow
	#------------------------------
	#界面操控方法
	#------------------------------
	#显示选定配对参数
	def showSelectPairDetail(self, pairItem):
		pairKey = pairItem.text()
		self.setCurrentPair(pairKey)
	def setCurrentPair(self, pairKey):
		self.curPairKey = pairKey
		#显示参数
		self.openLabel.setText(str(self.pairPara[str(pairKey)]["open"]))
		self.closeLabel.setText(str(self.pairPara[str(pairKey)]["close"]))
		self.stopLabel.setText(str(self.pairPara[str(pairKey)]["stop"]))
		self.stockALabel.setText(str(self.pairPara[str(pairKey)]["stock_A"])+":")
		self.stockBLabel.setText(str(self.pairPara[str(pairKey)]["stock_B"])+":")
		#切换图形显示
		pass

