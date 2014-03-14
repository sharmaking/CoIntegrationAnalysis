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
		self.messageTableWidget.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
		self.messageTableWidget.resizeColumnsToContents()
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
			self.pairTradeStatus[key] = {"datas":[]}
		self.pairNumLabel.setText(str(len(self.pairPara)))
		time.sleep(1)
		self.setCurrentPair(self.pairPara.items()[0][0])
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
			self.updateCanvas()
	def updateCanvas(self):
		self.dc.update_figure(self.pairTradeStatus[str(self.curPairKey)]["datas"], self.pairPara[str(self.curPairKey)])
		pass
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

