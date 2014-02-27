#!/usr/bin/python
# -*- coding: utf-8 -*-
#backTestPair.py
import os, csv
import numpy as np

AllStock = []
PairParas = {}
BarData = {}

ResultsPairPara = {}

#读取配对参数
def loadPairFun():
	global PairParas, AllStock
	reader = csv.reader(open("filtPara.csv"))
	for line in reader:
		#if line[0][:6] != "601169" and line[0][7:15] != "601169":
		PairParas[line[0]] = [
			float(line[1]), 
			float(line[2]), 
			float(line[3]),
			float(line[5]),	
			float(line[6]), float(line[7])]
		AllStock.append(line[0][:6])
		AllStock.append(line[0][7:15])
	AllStock = list(set(AllStock))
#读取bar数据
def loadBarDataFun():
	global BarData
	list_dirs = os.walk("F:\\HistoryData\\60")
	for root, folders, files in list_dirs:
		for f in files:
			dataDate = float(f[:8])
			if dataDate > 20131223 and dataDate < 20140122:
				path = os.path.join(root, f)
				reader = csv.reader(open(path))
				print path
				for line in reader:
					if line:
						stock = line[0]
						if stock in AllStock:
							if not BarData.has_key(stock):
								BarData[stock] = {}
							BarData[stock][int(line[1] + line[2])] = float(line[3])
	pass
#回测配对股票
def backTestPairFun():
	global ResultsPairPara
	for pairKey, pairPara in PairParas.items():
		series = formatSeriesFun(BarData[pairKey[:6]], BarData[pairKey[7:15]])
		getSeriesSFun(pairKey, series, pairPara)
#格式化bar序列
def formatSeriesFun(barData1, barData2):
	barDataList1 = sorted(barData1.iteritems(), key=lambda d:d[0])
	barDataList2 = sorted(barData2.iteritems(), key=lambda d:d[0])
	allDateKey = list(set(zip(*barDataList1)[0]+zip(*barDataList2)[0]))
	allDateKey.sort()
	resulteSeries = []
	for dateKey in allDateKey:
		if barData1.has_key(dateKey) and barData2.has_key(dateKey):
			resulteSeries.append([dateKey, barData1[dateKey], barData2[dateKey]])
	return resulteSeries
def getSeriesSFun(pairKey, series, pairPara):
	for data in series:
		s = np.log(data[1]) - pairPara[0]*np.log(data[2])
		data.append(s)
	for data in series:
		s = (data[3] - pairPara[1])/pairPara[2]
		data.append(s)
	newSeries = zip(*series)
	test = np.abs(list(newSeries[4]))
	test.sort()
	getTradePointFun(pairKey, series, pairPara[0], pairPara[3], pairPara[4], pairPara[5])
#计算交易点
def getTradePointFun(pairKey, series, beta, _open, _close, _stopLoss):
	opened = False
	tradePoints = []
	for _time, pa, pb, st, S in series:
		if not opened:	#还没开仓
			if S > _open:
				tradePoints.append(("开仓:", _time, "Sell:", pa, "buy:", pb))
				opened = True
		else:
			if S < _close:
				ratioA = (tradePoints[-1][3] - pa)/tradePoints[-1][3]
				ratioB = (pb - tradePoints[-1][5])/tradePoints[-1][5]
				ratioB = beta*ratioB
				tradePoints.append(("平仓:", _time, "Buy:", pa, "Sell:", pb, "收益:", ratioA, ratioB))
				print tradePoints[-1]
				opened = False

				logFile = open("tradePointsFinal.csv", "a")
				content = "%s,Close,OpenTime,%d,CloseTime,%d,Sell:%s,%f,%f,earnings:,%f,Buy:%s,%f,%f,earnings:,%f,all earnings, %f\n" %(
					pairKey, tradePoints[-2][1], _time,
					pairKey[:6], tradePoints[-2][3], pa, ratioA,
					pairKey[7:15], tradePoints[-2][5], pb, ratioB,
					(ratioA + ratioB)/(1+beta))
				logFile.write(content)
				logFile.close()

			if S > _stopLoss:
				ratioA = (tradePoints[-1][3] - pa)/tradePoints[-1][3]
				ratioB = (pb - tradePoints[-1][5])/tradePoints[-1][5]
				ratioB = beta*ratioB
				tradePoints.append(("止损:", _time, "Buy:", pa, "Sell:", pb, "收益:", ratioA, ratioB))
				print tradePoints[-1]
				opened = False

				logFile = open("tradePointsFinal.csv", "a")
				content = "%s,StopLoss,OpenTime,%d,CloseTime,%d,Sell:%s,%f,%f,earnings:,%f,Buy:%s,%f,%f,earnings:,%f,all earnings, %f\n" %(
					pairKey, tradePoints[-2][1], _time,
					pairKey[:6], tradePoints[-2][3], pa, ratioA,
					pairKey[7:15], tradePoints[-2][5], pb, ratioB,
					(ratioA + ratioB)/(1+beta))
				logFile.write(content)
				logFile.close()

				break

	for _time, pa, pb, st, S in series:
		if not opened:	#还没开仓
			if S < -_open:
				tradePoints.append(("开仓:", _time, "Buy:", pa, "Sell:", pb))
				opened = True
		else:
			if S > -_close:
				ratioA = (pa - tradePoints[-1][3])/tradePoints[-1][3]
				ratioB = (tradePoints[-1][5] - pb)/tradePoints[-1][5]
				ratioB = beta*ratioB
				tradePoints.append(("平仓:", _time, "Sell:", pa, "Buy:", pb, "收益:", ratioA, ratioB))
				print tradePoints[-1]
				opened = False

				logFile = open("tradePointsFinal.csv", "a")
				content = "%s,Close,OpenTime,%d,CloseTime,%d,Buy:%s,%f,%f,earnings:,%f,Sell:%s,%f,%f,earnings:,%f,all earnings, %f\n" %(
					pairKey, tradePoints[-2][1], _time,
					pairKey[:6], tradePoints[-2][3], pa, ratioA,
					pairKey[7:15], tradePoints[-2][5], pb, ratioB,
					(ratioA + ratioB)/(1+beta))
				logFile.write(content)
				logFile.close()

			if S < -_stopLoss:
				ratioA = (pa - tradePoints[-1][3])/tradePoints[-1][3]
				ratioB = (tradePoints[-1][5] - pb)/tradePoints[-1][5]
				ratioB = beta*ratioB
				tradePoints.append(("止损:", _time, "Sell:", pa, "Buy:", pb, "收益:", ratioA, ratioB))
				print tradePoints[-1]
				opened = False

				logFile = open("tradePointsFinal.csv", "a")
				content = "%s,StopLoss,OpenTime,%d,CloseTime,%d,Buy:%s,%f,%f,earnings:,%f,Sell:%s,%f,%f,earnings:,%f,all earnings, %f\n" %(
					pairKey, tradePoints[-2][1], _time,
					pairKey[:6], tradePoints[-2][3], pa, ratioA,
					pairKey[7:15], tradePoints[-2][5], pb, ratioB,
					(ratioA + ratioB)/(1+beta))
				logFile.write(content)
				logFile.close()

				break

		

def main():
	#读取配对股票参数
	loadPairFun()
	print len(AllStock)
	#读取bar数据
	loadBarDataFun()
	#回测配对股票
	backTestPairFun()

if __name__ == '__main__':
	main()