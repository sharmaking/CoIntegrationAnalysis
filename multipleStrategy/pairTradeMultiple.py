#!/usr/bin/python
# -*- coding: utf-8 -*-
#pairTradeMultiple.py
import baseMultiple
import csv, copy, numpy as np

class CPairTradeMultiple(baseMultiple.CBaseMultiple):
	#------------------------------
	#继承重载函数
	#------------------------------
	#自定义初始化函数
	def customInit(self):
		self.name = "pairTradeMultiple"
		self.pairDict = {}
		self.pairTradeStatus = {}
		self.loadPairPara()
	#行情数据触发函数
	def onRtnMarketData(self, data):
		self.sendMessage((1, data["dateTime"]))
		self.strategyEntrance(data)
	def dayEnd(self):
		pass
	#自动保存缓存触发函数
	def autosaveCache(self):
		#self.saveCache(data = self.data)
		pass
	#------------------------------
	#执行策略方法
	#------------------------------
	#读取配对参数
	def loadPairPara(self):
		reader = csv.reader(open("filtPara.csv"))
		for line in reader:
			if line:
				self.pairDict[line[0]] = {
					"stock_A" : line[0][:6],
					"stock_B" : line[0][7:15],
					"beta"	: float(line[1]), 
					"mean"	: float(line[2]), 
					"std"	: float(line[3]),
					"open"	: float(line[4]),	
					"close" : float(line[5]),
					"stop"	: float(line[6])}
				self.pairTradeStatus[line[0]] = {}
		self.sendMessage((0, self.pairDict))
	#活动股票价格
	def getStockCurPrice(self, stockCode):
		if self.actuatorDict[stockCode].signalObjDict["baseSignal"].MDList:
			return copy.copy(self.actuatorDict[stockCode].signalObjDict["baseSignal"].MDList[-1]["close"])
		return None
	#策略主入口
	def strategyEntrance(self, data):
		for pairKey, pairPara in self.pairDict.items():
			pa, pb = self.getStockCurPrice(pairPara["stock_A"]), self.getStockCurPrice(pairPara["stock_B"])
			if pa and pb:
				self.pairTradeStatus[pairKey]["pa"], self.pairTradeStatus[pairKey]["pb"] = pa, pb
				value = self.getPairValue(pa, pb, pairPara)
				#发送参数信号
				self.sendMessage((2, (pairKey, data["dateTime"],pa, pb, value)))
				self.getTradeMessage(data, value, pairPara, self.pairTradeStatus[pairKey])
			pass
		pass
	#计算配对策略值
	def getPairValue(self, pa, pb, para):
		St = np.log(pa) - para["beta"]*np.log(pb)
		S = (St - para["mean"])/para["std"]
		return S
	#计算开平仓信号
	def getTradeMessage(self, data, value, para, status):
		pass
