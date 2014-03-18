#!/usr/bin/python
# -*- coding: utf-8 -*-
#tradeDialogWindow.py
import copy, numpy as np
from PyQt4 import QtGui, QtCore, uic

class QTradeDialogWindow(QtGui.QDialog):
	def __init__(self, QMain, pairKey, pairPara, tradePoint):
		super(QTradeDialogWindow,self).__init__(parent = QMain)
		self.pairKey, self.pairPara, self.tradePoint = pairKey, pairPara, tradePoint
		self.initUI()
		self.initEventConnection()
	#初始化窗口布局
	def initUI(self):
		uic.loadUi('ui/tradeDialog.ui', self)
		self.setWindowTitle(u'记录开平仓')
		self.initPara()
	#初始化窗口元件事件关联
	def initEventConnection(self):
		#计算配对系数
		self.stock_A_Price_doubleSpinBox.valueChanged.connect(self.getPairValue)
		self.stock_B_Price_doubleSpinBox.valueChanged.connect(self.getPairValue)
		self.buttonBox.accepted.connect(self.accept) # 确定
		self.buttonBox.rejected.connect(self.reject) # 取消
	def initPara(self):
		self.pairKey_label.setText(self.pairKey)
		self.trade_Type_label.setText(self.tradePoint["type"])
		self.dealTime_dateTimeEdit.setDateTime(self.tradePoint["dateTime"])

		self.stock_A_label.setText(self.tradePoint["stock_A"])
		self.stock_A_Direction_label.setText(self.tradePoint["dirc_A"])
		self.stock_A_Price_doubleSpinBox.setValue(self.tradePoint["pa"])
		self.stock_A_Price_doubleSpinBox.setSingleStep(0.01)
		self.stock_A_Vol_spinBox.setSingleStep(100)
		self.stock_A_Vol_spinBox.setRange(100,1000)

		self.stock_B_label.setText(self.tradePoint["stock_B"])
		self.stock_B_Direction_label.setText(self.tradePoint["dirc_B"])
		self.stock_B_Price_doubleSpinBox.setValue(self.tradePoint["pb"])
		self.stock_B_Price_doubleSpinBox.setSingleStep(0.01)
		self.stock_B_Vol_spinBox.setSingleStep(100)
		self.stock_B_Vol_spinBox.setRange(100,1000)
		#
		if self.tradePoint["type"] == "open":
			self.stock_A_Vol_spinBox.setValue(self.tradePoint["vol_a"])
			self.stock_B_Vol_spinBox.setValue(self.tradePoint["vol_b"])
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
	#得到真实交易点
	def getTrueTradePoint(self):
		tradePoint = copy.copy(self.tradePoint)
		tradePoint["dateTime"] = self.dealTime_dateTimeEdit.dateTime().toPyDateTime()
		tradePoint["pa"] = self.stock_A_Price_doubleSpinBox.value()
		tradePoint["vol_a"] = self.stock_A_Vol_spinBox.value()
		tradePoint["pb"] = self.stock_B_Price_doubleSpinBox.value()
		tradePoint["vol_b"] = self.stock_B_Vol_spinBox.value()
		return tradePoint