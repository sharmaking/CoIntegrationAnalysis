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
		self.baseVol	= 200		#基本开仓量 200手
		self.outputFile = ".\\log\\tradPoint.csv"
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
				self.getTradeMessage(pairKey, data, value, pairPara, self.pairTradeStatus[pairKey])
			pass
		pass
	#计算配对策略值
	def getPairValue(self, pa, pb, para):
		St = np.log(pa) - para["beta"]*np.log(pb)
		S = (St - para["mean"])/para["std"]
		return S
	#计算开平仓信号
	def getTradeMessage(self, pairKey, data, value, para, status):
		if not status.has_key("tradPoint"):
			status["tradPoint"] = []
			status["direction"]	= 0 	# 0 未开仓, 1 正方向, 2 负方向, -1 不要做了
		if not status["direction"]:
			if value > para["open"]:	#正方向
				status["preOpenTime"] = copy.copy(data["dateTime"])
				status["tradPoint"].append({
					"type"		: "open",
					"pairKey"	: pairKey,
					"stock_A"	: pairKey[:6],
					"stock_B"	: pairKey[7:15],
					"beta"		: para["beta"],
					"dateTime"	: data["dateTime"],
					"direction"	: 1,
					"dirc_A"	: "sell",
					"dirc_B"	: "buy",
					"pa"		: status["pa"],
					"pb"		: status["pb"],
					"vol_a"		: self.baseVol,
					"vol_b"		: self.baseVol*status["pa"]*para["beta"]/status["pb"]
					})
				if para["beta"] < 0:
					status["tradPoint"][-1]["dirc_B"]	= status["tradPoint"][-1]["dirc_A"]
				self.sendMessage((3, status["tradPoint"][-1]))
				status["direction"] = 1
			if value < -para["open"]:	#负
				status["preOpenTime"] = copy.copy(data["dateTime"])
				status["tradPoint"].append({
					"type"		: "open",
					"pairKey"	: pairKey,
					"stock_A"	: pairKey[:6],
					"stock_B"	: pairKey[7:15],
					"beta"		: para["beta"],
					"dateTime"	: data["dateTime"],
					"direction"	: 1,
					"dirc_A"	: "buy",
					"dirc_B"	: "sell",
					"pa"		: status["pa"],
					"pb"		: status["pb"],
					"vol_a"		: self.baseVol,
					"vol_b"		: self.baseVol*status["pa"]*para["beta"]/status["pb"]
					})
				if para["beta"] < 0:
					status["tradPoint"][-1]["dirc_B"]	= status["tradPoint"][-1]["dirc_A"]
				self.sendMessage((3, status["tradPoint"][-1]))
				status["direction"] = 2
		elif status["direction"] == 1:	#正方向
			if value < para["close"]:	#平仓
				ratio_A = (status["tradPoint"][-1]["pa"] - status["pa"])*0.9992/status["tradPoint"][-1]["pa"]
				ratio_B = (status["pb"] - status["tradPoint"][-1]["pb"])*0.9992/status["tradPoint"][-1]["pb"]
				ratio 	= (ratio_A+ratio_B*np.abs(para["beta"]))/(1+np.abs(para["beta"]))
				status["tradPoint"].append({
					"type"		: "close",
					"pairKey"	: pairKey,
					"stock_A"	: pairKey[:6],
					"stock_B"	: pairKey[7:15],
					"beta"		: para["beta"],
					"dateTime"	: data["dateTime"],
					"direction"	: 1,
					"dirc_A"	: "buy",
					"dirc_B"	: "sell",
					"pa"		: status["pa"],
					"pb"		: status["pb"],
					"ratio_A"	: ratio_A,
					"ratio_B"	: ratio_B,
					"ratio"		: ratio
					})
				self.creatTradingLog(status["tradPoint"][-1], status["tradPoint"][-2])
				self.sendMessage((3, status["tradPoint"][-1]))
				status["direction"] = 0
			if value > para["stop"]:	#止损
				ratio_A = (status["tradPoint"][-1]["pa"] - status["pa"])*0.9992/status["tradPoint"][-1]["pa"]
				ratio_B = (status["pb"] - status["tradPoint"][-1]["pb"])*0.9992/status["tradPoint"][-1]["pb"]
				ratio 	= (ratio_A+ratio_B*np.abs(para["beta"]))/(1+np.abs(para["beta"]))
				status["tradPoint"].append({
					"type"		: "stop",
					"pairKey"	: pairKey,
					"stock_A"	: pairKey[:6],
					"stock_B"	: pairKey[7:15],
					"beta"		: para["beta"],
					"dateTime"	: data["dateTime"],
					"direction"	: 1,
					"dirc_A"	: "buy",
					"dirc_B"	: "sell",
					"pa"		: status["pa"],
					"pb"		: status["pb"],
					"ratio_A"	: ratio_A,
					"ratio_B"	: ratio_B,
					"ratio"		: ratio
					})
				self.creatTradingLog(status["tradPoint"][-1], status["tradPoint"][-2])
				self.sendMessage((3, status["tradPoint"][-1]))
				status["direction"] = -1
		elif status["direction"] == 2:	#负方向
			if value > -para["close"]:	#平仓
				ratio_A = (status["pa"] - status["tradPoint"][-1]["pa"])*0.9992/status["tradPoint"][-1]["pa"]
				ratio_B = (status["tradPoint"][-1]["pb"] - status["pb"])*0.9992/status["tradPoint"][-1]["pb"]
				ratio 	= (ratio_A+ratio_B*np.abs(para["beta"]))/(1+np.abs(para["beta"]))
				status["tradPoint"].append({
					"type"		: "close",
					"pairKey"	: pairKey,
					"stock_A"	: pairKey[:6],
					"stock_B"	: pairKey[7:15],
					"beta"		: para["beta"],
					"dateTime"	: data["dateTime"],
					"direction"	: 2,
					"dirc_A"	: "sell",
					"dirc_B"	: "buy",
					"pa"		: status["pa"],
					"pb"		: status["pb"],
					"ratio_A"	: ratio_A,
					"ratio_B"	: ratio_B,
					"ratio"		: ratio
					})
				self.creatTradingLog(status["tradPoint"][-1], status["tradPoint"][-2])
				self.sendMessage((3, status["tradPoint"][-1]))
				status["direction"] = 0
			if value < -para["stop"]:	#止损
				ratio_A = (status["pa"] - status["tradPoint"][-1]["pa"])*0.9992/status["tradPoint"][-1]["pa"]
				ratio_B = (status["tradPoint"][-1]["pb"] - status["pb"])*0.9992/status["tradPoint"][-1]["pb"]
				ratio 	= (ratio_A+ratio_B*np.abs(para["beta"]))/(1+np.abs(para["beta"]))
				status["tradPoint"].append({
					"type"		: "stop",
					"pairKey"	: pairKey,
					"stock_A"	: pairKey[:6],
					"stock_B"	: pairKey[7:15],
					"beta"		: para["beta"],
					"dateTime"	: data["dateTime"],
					"direction"	: 2,
					"dirc_A"	: "sell",
					"dirc_B"	: "buy",
					"pa"		: status["pa"],
					"pb"		: status["pb"],
					"ratio_A"	: ratio_A,
					"ratio_B"	: ratio_B,
					"ratio"		: ratio
					})
				self.creatTradingLog(status["tradPoint"][-1], status["tradPoint"][-2])
				self.sendMessage((3, status["tradPoint"][-1]))
				status["direction"] = -1
		pass

	def creatTradingLog(self, closeTrade, openTrade):
		if closeTrade["beta"] < 0:
			openTrade["dirc_B"]	= openTrade["dirc_A"]
			closeTrade["dirc_B"] = closeTrade["dirc_A"]
			closeTrade["ratio_B"] = -1*closeTrade["ratio_B"]
			closeTrade["ratio"]	= (closeTrade["ratio_A"] + closeTrade["ratio_B"]*np.abs(closeTrade["beta"]))/(1+np.abs(closeTrade["beta"]))
		outputFile = open(self.outputFile, "a")
		content = "%s,%s,openTime,%s,closeTime,%s,%s,%s,%s,%s,ratio_A,%s,%s,%s,%s,%s,ratio_B,%s,all_ratio,%s\n"%(
			closeTrade["pairKey"], closeTrade["type"], str(openTrade["dateTime"]), str(closeTrade["dateTime"]),
			closeTrade["stock_A"], openTrade["dirc_A"], openTrade["pa"], closeTrade["pa"],closeTrade["ratio_A"],
			closeTrade["stock_B"], openTrade["dirc_B"], openTrade["pb"], closeTrade["pb"],closeTrade["ratio_B"],
			closeTrade["ratio"])
		outputFile.write(content)
		outputFile.close()
		pass