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
	reader = csv.reader(open("results2.csv"))
	for line in reader:
		if line[0][:6] != "601169" and line[0][7:15] != "601169":
			PairParas[line[0]] = [float(line[1]),float(line[2])]
			AllStock.append(line[0][:6])
			AllStock.append(line[0][7:15])
	AllStock = list(set(AllStock))
#读取bar数据
def loadBarDataFun():
	global BarData
	list_dirs = os.walk("F:\\testData")
	for root, folders, files in list_dirs:
		for f in files:
			if f[:6] in AllStock:
				path = os.path.join(root, f)
				reader = csv.reader(open(path))
				print path
				BarData[f[:6]] = {}
				for data in reader:
					if len(data) > 1:
						if int(data[0]) > 20140101:
							BarData[f[:6]][int(data[0] + data[1])] = float(data[5])
	pass
#回测配对股票
def backTestPairFun():
	global ResultsPairPara
	for pairKey, pairPara in PairParas.items():
		series = formatSeriesFun(BarData[pairKey[:6]], BarData[pairKey[7:15]])
		_open, _close, _stopLoss = getSeriesSFun(pairKey, series, pairPara)
		ResultsPairPara[pairKey] = {
			"stocks"	: [pairKey[:6], pairKey[7:15]],
			"Beta"		: pairPara[0],
			"Mean"		: pairPara[2],
			"STD"		: pairPara[1],
			"OPEN"		: _open,
			"CLOSE"		: _close,
			"ODD"		: _stopLoss
		}
		
		logFile = open("resultsPairPara.csv", "a")
		content = "%s,%f,%f,%f,%f,%f,%f\n" %(pairKey, pairPara[0], pairPara[2], pairPara[1], _open, _close, _stopLoss)
		logFile.write(content)
		logFile.close()
	pass
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
	newSeries = zip(*series)
	pairPara.append(np.mean(newSeries[3]))
	for data in series:
		s = (data[3] - pairPara[2])/pairPara[1]
		data.append(s)
	newSeries = zip(*series)
	test = np.abs(list(newSeries[4]))
	test.sort()
	getTradePointFun(pairKey, series, pairPara[0], test[len(test)*0.90], test[len(test)*0.04], test[-1])
	return test[len(test)*0.90], test[len(test)*0.04], test[-1]+0.01
#计算交易点
def getTradePointFun(pairKey, series, beta, _open, _close, _stopLoss):
	opened = False
	direction = "None"
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

				logFile = open("tradePoints.csv", "a")
				content = "%s,OpenTime,%d,CloseTime,%d,Sell:%s,%f,%f,earnings:,%f,Buy:%s,%f,%f,earnings:,%f,all earnings, %f\n" %(
					pairKey, tradePoints[-2][1], _time,
					pairKey[:6], tradePoints[-2][3], pa, ratioA,
					pairKey[7:15], tradePoints[-2][5], pb, ratioB,
					(ratioA + ratioB)/(1+beta))
				logFile.write(content)
				logFile.close()

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

				logFile = open("tradePoints.csv", "a")
				content = "%s,OpenTime,%d,CloseTime,%d,Buy:%s,%f,%f,earnings:,%f,Sell:%s,%f,%f,earnings:,%f,all earnings, %f\n" %(
					pairKey, tradePoints[-2][1], _time,
					pairKey[:6], tradePoints[-2][3], pa, ratioA,
					pairKey[7:15], tradePoints[-2][5], pb, ratioB,
					(ratioA + ratioB)/(1+beta))
				logFile.write(content)
				logFile.close()

		

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