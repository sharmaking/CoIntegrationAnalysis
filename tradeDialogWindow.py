#!/usr/bin/python
# -*- coding: utf-8 -*-
#tradeDialogWindow.py
import copy, numpy as np
from PyQt4 import QtGui, QtCore, uic

class QTradeDialogWindow(QtGui.QDialog):
	def __init__(self, QMain, pairKey, pairPara, tradePoint):
		super(QTradeDialogWindow,self).__init__(parent = QMain)
		self.QMain = QMain
		self.pairKey, self.pairPara, self.tradePoint = pairKey, pairPara, tradePoint
		self.initUI()
		self.initEventConnection()
		timer = QtCore.QTimer(self)
		timer.setInterval(1000)
		QtCore.QObject.connect(timer, QtCore.SIGNAL("timeout()"), self.updateVol)
		timer.start()
	#初始化窗口布局
	def initUI(self):
		uic.loadUi('ui/tradeDialog.ui', self)
		self.setWindowTitle(u'记录开平仓')
		self.initTable()
		self.initPara()
	def initTable(self):
		#stock_A_10档行情
		self.stock_A_tableWidget.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
		self.stock_A_tableWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)	#设置选择行为，以行为单位
		self.stock_A_tableWidget.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)		#禁止编辑
		#stock_B_10档行情
		self.stock_B_tableWidget.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
		self.stock_B_tableWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)	#设置选择行为，以行为单位
		self.stock_B_tableWidget.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)		#禁止编辑
		#初始空值
		for i in range(10):
			for j in range(2):
				newItem1 = QtGui.QTableWidgetItem("")
				self.stock_A_tableWidget.setItem(i,j,newItem1)
				newItem2 = QtGui.QTableWidgetItem("")
				self.stock_B_tableWidget.setItem(i,j,newItem2)
				if not j:
					if i <= 4:
						newItem1.setForeground(QtGui.QColor("red"))
						newItem2.setForeground(QtGui.QColor("red"))
					else:
						newItem1.setForeground(QtGui.QColor("green"))
						newItem2.setForeground(QtGui.QColor("green"))
				if i == 4:
					newItem1.setBackground(QtGui.QColor(226,244,235,100))
					newItem2.setBackground(QtGui.QColor(226,244,235,100))
				if i == 5:
					newItem1.setBackground(QtGui.QColor(252,221,222,100))
					newItem2.setBackground(QtGui.QColor(252,221,222,100))
	#初始化窗口元件事件关联
	def initEventConnection(self):
		#计算配对系数
		self.stock_A_Price_doubleSpinBox.valueChanged.connect(self.getPairValue)
		self.stock_B_Price_doubleSpinBox.valueChanged.connect(self.getPairValue)
		#打开交易对话框
		self.stock_A_tableWidget.cellDoubleClicked.connect(self.updatePriceA)
		self.stock_B_tableWidget.cellDoubleClicked.connect(self.updatePriceB)
		#对话提交
		self.buttonBox.accepted.connect(self.accept) # 确定
		self.buttonBox.rejected.connect(self.reject) # 取消
	def initPara(self):
		self.pairKey_label.setText(self.pairKey)
		self.trade_Type_label.setText(self.tradePoint["type"])
		self.dealTime_dateTimeEdit.setDateTime(self.tradePoint["dateTime"])

		self.stock_A_List_label.setText(self.tradePoint["stock_A"])
		self.stock_A_label.setText(self.tradePoint["stock_A"])
		self.stock_A_Direction_label.setText(self.tradePoint["dirc_A"])
		self.stock_A_Price_doubleSpinBox.setValue(self.tradePoint["pa"])
		self.stock_A_Price_doubleSpinBox.setSingleStep(0.01)
		self.stock_A_Vol_spinBox.setSingleStep(100)
		self.stock_A_Vol_spinBox.setRange(100,1000)

		self.stock_B_List_label.setText(self.tradePoint["stock_B"])
		self.stock_B_label.setText(self.tradePoint["stock_B"])
		self.stock_B_Direction_label.setText(self.tradePoint["dirc_B"])
		self.stock_B_Price_doubleSpinBox.setValue(self.tradePoint["pb"])
		self.stock_B_Price_doubleSpinBox.setSingleStep(0.01)
		self.stock_B_Vol_spinBox.setSingleStep(100)
		self.stock_B_Vol_spinBox.setRange(100,1000)
		#获得量
		if self.tradePoint["type"] == "open":
			self.stock_A_Vol_spinBox.setValue(self.tradePoint["vol_a"])
			self.stock_B_Vol_spinBox.setValue(self.tradePoint["vol_b"])
		else:
			try:
				openPoint = self.QMain.positionsPair[self.pairKey][-1]
				self.stock_A_Vol_spinBox.setValue(openPoint["vol_a"])
				self.stock_B_Vol_spinBox.setValue(openPoint["vol_b"])
			except Exception:
				pass			
		#计算配对系数
		self.getPairValue(0)
		#设置阈值
		self.open_label.setText(str(self.pairPara["open"]))
		self.close_label.setText(str(self.pairPara["close"]))
		self.stop_label.setText(str(self.pairPara["stop"]))
	#计算配对系数
	def getPairValue(self,value):
		St = np.log(self.stock_A_Price_doubleSpinBox.value()) - self.pairPara["beta"]*np.log(self.stock_B_Price_doubleSpinBox.value())
		S = (St - self.pairPara["mean"])/self.pairPara["std"]
		self.pair_Value_label.setText(str(S))
	#获得单数据
	def updateVol(self):
		volList_A = self.QMain.pairTradeStatus[self.pairKey]["volList_A"]
		volList_B = self.QMain.pairTradeStatus[self.pairKey]["volList_B"]
		for i in xrange(10):
			for j in xrange(2):
				self.stock_A_tableWidget.item(i,j).setText(str(volList_A[i][j]))
				self.stock_B_tableWidget.item(i,j).setText(str(volList_B[i][j]))
	#更新保单价格
	def updatePriceA(self, row, column):
		newPrice = self.stock_A_tableWidget.item(row, 0).text()
		self.stock_A_Price_doubleSpinBox.setValue(float(newPrice))
	def updatePriceB(self, row, column):
		newPrice = self.stock_B_tableWidget.item(row, 0).text()
		self.stock_B_Price_doubleSpinBox.setValue(float(newPrice))
	#得到真实交易点
	def getTrueTradePoint(self):
		tradePoint = copy.copy(self.tradePoint)
		tradePoint["dateTime"] = self.dealTime_dateTimeEdit.dateTime().toPyDateTime()
		tradePoint["pa"] = self.stock_A_Price_doubleSpinBox.value()
		tradePoint["vol_a"] = self.stock_A_Vol_spinBox.value()
		tradePoint["pb"] = self.stock_B_Price_doubleSpinBox.value()
		tradePoint["vol_b"] = self.stock_B_Vol_spinBox.value()
		return tradePoint