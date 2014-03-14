#!/usr/bin/python
# -*- coding: utf-8 -*-
#pairTradeMultiple.py
import baseMultiple

class CPairTradeMultiple(baseMultiple.CBaseMultiple):
	#------------------------------
	#继承重载函数
	#------------------------------
	#自定义初始化函数
	def customInit(self):
		self.name = "pairTradeMultiple"
		self.loadPairPara()
	#行情数据触发函数
	def onRtnMarketData(self, data):
		self.sendMessage((1, data["dateTime"]))
		pass
	def dayEnd(self):
		pass
	#自动保存缓存触发函数
	def autosaveCache(self):
		#self.saveCache(data = self.data)
		pass
	#------------------------------
	#执行策略方法
	#------------------------------
	def loadPairPara(self):
		pass
