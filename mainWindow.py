#!/usr/bin/python
# -*- coding: utf-8 -*-
#mainWindow.py
from PyQt4 import QtGui, QtCore, uic
import tradeDialogWindow, pairDetailDialogWindow
import datetime, sys, os, time, copy

class QMainWindow(QtGui.QMainWindow):
	def __init__(self):
		super(QMainWindow,self).__init__()
		self.initUI()
		self.initEventConnection()
		self.curPairKey = ""
		self.pairPara = {}			#配对参数
		self.pairTradeStatus = {}	#配对交易状态
		#真实交易记录
		self.tureTradePoint = {}
		self.positionsPair = {}
		#缓存初始化
		self.initCashe()
	#初始化窗口布局
	def initUI(self):
		uic.loadUi('ui/mainWindows.ui', self)
		self.setWindowTitle(u'统计套利信号客户端')
		self.statusBar().showMessage(u'已连接服务器')
		#设置表格
		#信号表格
		self.messageTableWidget.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)	#自动设置宽度
		self.messageTableWidget.horizontalHeader().setStretchLastSection(True)
		self.messageTableWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)	#设置选择行为，以行为单位
		self.messageTableWidget.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)		#禁止编辑
		#持仓表格
		self.positionsPairTableWidget.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)	#自动设置宽度
		self.positionsPairTableWidget.horizontalHeader().setStretchLastSection(True)
		self.positionsPairTableWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)	#设置选择行为，以行为单位
		self.positionsPairTableWidget.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)		#禁止编辑
		#真实交易历史记录
		self.tureTradeTableWidget.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)	#自动设置宽度
		self.tureTradeTableWidget.horizontalHeader().setStretchLastSection(True)
		self.tureTradeTableWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)	#设置选择行为，以行为单位
		self.tureTradeTableWidget.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)		#禁止编辑
		# 创建QMenu
		self.messageTableContextMenu = QtGui.QMenu(self)
		self.showDetailDialogAction = self.messageTableContextMenu.addAction(u'显示详情')
	#初始化窗口元件事件关联
	def initEventConnection(self):
		#打开交易对话框
		self.messageTableWidget.cellDoubleClicked.connect(self.makeADeal)
		#排序事件
		self.messageTableWidget.horizontalHeader().sectionClicked.connect(self.messageTableWidget.sortItems)
		self.positionsPairTableWidget.horizontalHeader().sectionClicked.connect(self.positionsPairTableWidget.sortItems)
		self.tureTradeTableWidget.horizontalHeader().sectionClicked.connect(self.tureTradeTableWidget.sortItems)
		#弹出右键菜单事件
		self.messageTableWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		self.messageTableWidget.customContextMenuRequested.connect(self.showContextMenu)
		#右键菜单事件
		self.showDetailDialogAction.triggered.connect(self.showDetailDialog)
	#------------------------------
	#cache 相关函数
	#------------------------------
	def initCashe(self):
		self.cacheFilePath = "log/tureTrade.log"
		self.loadCache()
	#读取缓存
	def loadCache(self):
		if not os.path.isfile(self.cacheFilePath):
			self.cacheFile = open(self.cacheFilePath, "w")
			self.cacheFile.close
		execfile(self.cacheFilePath)
		for key, value in self.positionsPair.items():
			if value:
				self.recordTrueTradePoint(key, value[-1]["type"], value[-1])
	#保存缓存
	def saveCache(self, **objDict):
		self.cacheFile = open(self.cacheFilePath, "w")
		content = ""
		for key, value in objDict.items():
			_value = self.dislodgeObj(value)
			content += "self.%s = %s\n" %(key, str(_value))
		self.cacheFile.write(content)
		self.cacheFile.close()
	#格式化保存数据
	def dislodgeObj(self, value):
		newValue = {}
		for _key, _list in value.items():
			newList = []
			for _item in _list:
				newItem = {}
				for _para, _value in _item.items():
					if _para != "gain_A" and _para != "gain_B" and _para != "gain_All" and _para != "cur_pa" and _para != "cur_pb":
						newItem[_para] = _value
				newList.append(newItem)
			newValue[_key] = newList
		return newValue
	#------------------------------
	#后台策略方法
	#------------------------------
	#显示行情时间
	def showMarketTime(self, marketTime):
		self.marketTimeLabel.setText(marketTime)
	#显示本地时间
	def showLocalTime(self, localTime):
		self.localTimeLabel.setText(localTime)
	#获取参数表
	def getPairPara(self, pairPara):
		self.pairPara = pairPara
		for key, para in sorted(self.pairPara.items(), key=lambda d:d[0]):
			#self.pairlistWidget.addItem(key)
			self.pairTradeStatus[key] = {"datas":[], "tradPoint":[]}
		self.pairNumLabel.setText(str(len(self.pairPara)))
	#获得配对参数
	def getPairValue(self, pairValue):
		pairKey, valuetime, pa, pb, value, volList_A, volList_B = pairValue
		self.pairTradeStatus[pairKey]["pa"] = pa
		self.pairTradeStatus[pairKey]["pb"] = pb
		self.pairTradeStatus[pairKey]["datas"].append((valuetime, value))
		self.pairTradeStatus[pairKey]["volList_A"] = volList_A
		self.pairTradeStatus[pairKey]["volList_B"] = volList_B
		if len(self.pairTradeStatus[pairKey]["datas"]) > 6000:
			del self.pairTradeStatus[pairKey]["datas"][0]
		#显示参数
		if pairKey == self.curPairKey:
			self.stockAPriceLabel.setText(str(pa))
			self.stockBPriceLabel.setText(str(pb))
			self.valueLabel.setText(str(value))
		self.updatePositionGain(pairKey, pa, pb)
	#更新持仓盈亏
	def updatePositionGain(self, pairKey, pa, pb):
		if self.tabWidget.currentIndex() == 1 and self.positionsPair.has_key(pairKey) and self.positionsPair[pairKey]:
			openTradePoint = self.positionsPair[pairKey][-1]
			para = self.pairPara[pairKey]

			ratio_A = (openTradePoint["pa"] - pa - openTradePoint["pa"]*0.0008)*openTradePoint["vol_a"]
			ratio_B = (openTradePoint["pb"] - pb - openTradePoint["pb"]*0.0008)*openTradePoint["vol_b"]

			if openTradePoint["dirc_A"] == "buy":
				ratio_A = -1*ratio_A
			if openTradePoint["dirc_B"] == "buy":
				ratio_B = -1*ratio_B

			ratio 	= ratio_A + ratio_B

			if ratio_A > 0 :
				openTradePoint["gain_A"].setForeground(QtGui.QColor("red"))
			else:
				openTradePoint["gain_A"].setForeground(QtGui.QColor("green"))
			if ratio_B > 0 :
				openTradePoint["gain_B"].setForeground(QtGui.QColor("red"))
			else:
				openTradePoint["gain_B"].setForeground(QtGui.QColor("green"))
			if ratio > 0 :
				openTradePoint["gain_All"].setForeground(QtGui.QColor("red"))
			else:
				openTradePoint["gain_All"].setForeground(QtGui.QColor("green"))

			openTradePoint["cur_pa"].setText(str(pa))
			openTradePoint["cur_pb"].setText(str(pb))

			openTradePoint["gain_A"].setText(str(ratio_A))
			openTradePoint["gain_B"].setText(str(ratio_B))
			openTradePoint["gain_All"].setText(str(ratio))
		pass
	#显示开平仓信号
	def getTradeMessage(self, tradeMessage):
		self.messageTableWidget.setRowCount(self.messageTableWidget.rowCount() + 1)
		self.pairTradeStatus[tradeMessage["pairKey"]]["tradPoint"].append(tradeMessage)
		if tradeMessage["type"] == "open":
			itemRow = self.formartTradeMessage(tradeMessage, "open")
			if self.positionsPair.has_key(tradeMessage["pairKey"]) and self.positionsPair[tradeMessage["pairKey"]]:
				if self.positionsPair[tradeMessage["pairKey"]][-1]["direction"] == tradeMessage["direction"]:
					itemRow[0].setText("Check")
			for i in xrange(len(itemRow)):
				self.messageTableWidget.setItem(self.messageTableWidget.rowCount()-1,i,itemRow[i])
		elif tradeMessage["type"] == "close":
			itemRow = self.formartTradeMessage(tradeMessage, "close")
			if not(self.positionsPair.has_key(tradeMessage["pairKey"]) and self.positionsPair[tradeMessage["pairKey"]]):
				itemRow[0].setText("X")
			for i in xrange(len(itemRow)):
				self.messageTableWidget.setItem(self.messageTableWidget.rowCount()-1,i,itemRow[i])
		elif tradeMessage["type"] == "stop":
			itemRow = self.formartTradeMessage(tradeMessage, "stop")
			if not(self.positionsPair.has_key(tradeMessage["pairKey"]) and self.positionsPair[tradeMessage["pairKey"]]):
				itemRow[0].setText("X")
			for i in xrange(len(itemRow)):
				self.messageTableWidget.setItem(self.messageTableWidget.rowCount()-1,i,itemRow[i])
		pass
	#格式化交易信号
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
		itemRow.insert(0, QtGui.QTableWidgetItem(""))
		return itemRow
	#------------------------------
	#界面操控方法
	#------------------------------
	#显示右键菜单
	def showContextMenu(self):
		if self.messageTableContextMenu.exec_(QtGui.QCursor().pos()):
			pass
	#显示配对详情
	def showDetailDialog(self):
		pairDetailDialog = pairDetailDialogWindow.QPairDetailDialogWindow(self)
		if pairDetailDialog.exec_():
			pass
		pairDetailDialog.destroy()
	#显示对话框
	def makeADeal(self, row, column):
		pairKey = self.messageTableWidget.item(row, 1).text()
		tradeType = self.messageTableWidget.item(row, 2).text()
		dialog = tradeDialogWindow.QTradeDialogWindow(self, str(pairKey), self.pairPara[str(pairKey)], self.pairTradeStatus[str(pairKey)]["tradPoint"][-1])
		if dialog.exec_():
			tradePoint = dialog.getTrueTradePoint()
			self.recordTrueTradePoint(str(pairKey), tradeType, tradePoint)
			self.messageTableWidget.item(row, 0).setText("Check")
			#保存交易信息
			self.saveCache(
				positionsPair = self.positionsPair,
				tureTradePoint = self.tureTradePoint)
		dialog.destroy()
	#记录真实交易记录
	def recordTrueTradePoint(self, pairKey, tradeType, tradePoint):
		tradePoint = copy.copy(tradePoint)
		#真实交易记录
		self.tureTradeTableWidget.setRowCount(self.tureTradeTableWidget.rowCount() + 1)
		itemRow = self.formartTrueTradeMessage(tradePoint, tradeType)
		if not self.tureTradePoint.has_key(pairKey):
			self.tureTradePoint[pairKey] = []
		try:
			while self.tureTradePoint[pairKey][-1]["direction"] == tradePoint["direction"]:
				del self.tureTradePoint[pairKey][-1]
		except Exception:
			pass		
		self.tureTradePoint[pairKey].append(tradePoint)
		for i in xrange(len(itemRow)):
			self.tureTradeTableWidget.setItem(self.tureTradeTableWidget.rowCount()-1,i,itemRow[i])
		#持仓记录
		if tradeType == "open":
			self.positionsPairTableWidget.setRowCount(self.positionsPairTableWidget.rowCount() + 1)
			itemRow = self.formartTrueTradeMessage(tradePoint, tradeType)
			tradePoint["gain_A"] = QtGui.QTableWidgetItem(str(0))
			tradePoint["gain_B"] = QtGui.QTableWidgetItem(str(1))
			tradePoint["gain_All"] = QtGui.QTableWidgetItem(str(2))
			itemRow.insert(8, tradePoint["gain_A"])
			itemRow.insert(13, tradePoint["gain_B"])
			itemRow.insert(14, tradePoint["gain_All"])
			tradePoint["cur_pa"] = QtGui.QTableWidgetItem(str(tradePoint["pa"]))
			tradePoint["cur_pb"] = QtGui.QTableWidgetItem(str(tradePoint["pb"]))
			itemRow.insert(8, tradePoint["cur_pa"])
			itemRow.insert(14, tradePoint["cur_pb"])
			for i in xrange(len(itemRow)):
				self.positionsPairTableWidget.setItem(self.positionsPairTableWidget.rowCount()-1,i,itemRow[i])
			if not self.positionsPair.has_key(pairKey):
				self.positionsPair[pairKey] = []
			try:
				while self.positionsPair[pairKey][-1]["direction"] == tradePoint["direction"]:
					del self.positionsPair[pairKey][-1]
			except Exception:
				pass		
			self.positionsPair[pairKey].append(tradePoint)
			#更新持仓数目
			self.positionslabel.setText(str(int(self.positionslabel.text())+1))
		else:
			item = self.positionsPairTableWidget.findItems(QtCore.QString(pairKey), QtCore.Qt.MatchFlags(0))
			#显示平仓盈亏
			_openPrice_A, _openVol_A, _openPrice_B, _openVol_B = float(item[6].text()), float(item[7].text()), float(item[12].text()), float(item[13].text())
			_gain_All = float(item[17].text())
			_gain_All_raito = _gain_All/(_openPrice_A*_openVol_A + _openPrice_B*_openVol_B)
			self.tureTradeTableWidget.setItem(self.tureTradeTableWidget.rowCount()-1,12,QtGui.QTableWidgetItem(str(_gain_All)))
			self.tureTradeTableWidget.setItem(self.tureTradeTableWidget.rowCount()-1,13,QtGui.QTableWidgetItem(str(_gain_All_raito)))
			tradePoint["earnings_All"] = _gain_All
			tradePoint["earnings_All_raito"] = _gain_All_raito
			#清除持仓列表
			self.positionsPair[pairKey] = []
			row = self.positionsPairTableWidget.row(item[0])
			self.positionsPairTableWidget.removeRow(row)
			self.positionslabel.setText(str(int(self.positionslabel.text())-1))
	#格式化真实交易点
	def formartTrueTradeMessage(self, tradeMessage, tradeType):
		itemRow = [
			QtGui.QTableWidgetItem(str(tradeMessage["pairKey"])),
			QtGui.QTableWidgetItem(str(tradeMessage["type"])),
			QtGui.QTableWidgetItem(str(tradeMessage["dateTime"])[:19]),
			QtGui.QTableWidgetItem(str(tradeMessage["beta"])),
			#------stock_a
			QtGui.QTableWidgetItem(str(tradeMessage["stock_A"])),
			QtGui.QTableWidgetItem(str(tradeMessage["dirc_A"])),
			QtGui.QTableWidgetItem(str(tradeMessage["pa"])),
			QtGui.QTableWidgetItem(str(tradeMessage["vol_a"])),
			#------stock_b
			QtGui.QTableWidgetItem(str(tradeMessage["stock_B"])),
			QtGui.QTableWidgetItem(str(tradeMessage["dirc_B"])),
			QtGui.QTableWidgetItem(str(tradeMessage["pb"])),
			QtGui.QTableWidgetItem(str(tradeMessage["vol_b"]))
			]
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
		#
		if tradeType == "close":
			for item in itemRow:
				item.setBackground(QtGui.QColor(252,221,222,100))
		elif tradeType == "stop":
			for item in itemRow:
				item.setBackground(QtGui.QColor(226,244,235,100))
		return itemRow


