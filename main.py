#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, csv
from scipy.optimize import leastsq
import numpy as np

Plate = {}
RZRQ = []
BarData = {}
Results = {}

#读取板块
def loadPlateFun():
	global Plate
	reader = csv.reader(open("plate.csv"))
	for line in reader:
		num = 0
		plateName = ""
		for data in line:
			if not num:
				plateName = data
				Plate[plateName] = []
			else:
				if data:
					Plate[plateName].append(data)
			num = num + 1
#读取融资融券标的
def loadRZRQStockFun():
	global RZRQ
	reader = csv.reader(open("rzrq.csv"))
	for line in reader:
		for data in line:
			if data:
				RZRQ.append(data)
#判断是否在同一板块
def isInTheSamePlateFun(stock1,stock2):
	if stock1 == stock2:
		return False
	for plateName, stocks in Plate.items():
		if (stock1 in stocks) and (stock2 in stocks):
			print "%s and %s is in the same Plate '%s'" %(stock1, stock2,plateName[:-1])
			return True
	return False
#读取分钟线数据
def loadBarDataFun():
	global BarData
	list_dirs = os.walk("F:\\testData")
	for root, folders, files in list_dirs:
		for f in files:
			if f[:6] in RZRQ:
				path = os.path.join(root, f)
				reader = csv.reader(open(path))
				print path
				BarData[f[:6]] = {}
				for data in reader:
					if len(data) > 1:
						if int(data[0]) > 20140101:
							BarData[f[:6]][int(data[0] + data[1])] = float(data[5])
#筛选配对股票
def stockPairSelectFun():
	global Results
	for stock1, barData1 in BarData.items():
		for stock2, barData2 in BarData.items():
			if isInTheSamePlateFun(stock1, stock2):	#如果在同一个板块
				key, series = getPairKeyFun(stock1, stock2, barData1, barData2)
				if stock1 != stock2 and not Results.has_key(key):
					p, STD = fittingSeriesFun(series)
					Results[key] = p, STD
					print key, p, STD
					logFile = open("results.csv", "a")
					content = "%s,%f,%s\n"%(key, p[0], STD)
					logFile.write(content)
					logFile.close()
	pass
def getPairKeyFun(stock1, stock2, barData1, barData2):
	if stock1 > stock2:
		series = formatSeriesFun(barData1, barData2)
		return "%s-%s"%(stock1, stock2), series
	if stock1 < stock2:
		series = formatSeriesFun(barData2, barData1)
		return "%s-%s"%(stock2, stock1), series
def formatSeriesFun(barData1, barData2):
	barDataList1 = sorted(barData1.iteritems(), key=lambda d:d[0])
	barDataList2 = sorted(barData2.iteritems(), key=lambda d:d[0])
	allDateKey = list(set(zip(*barDataList1)[0]+zip(*barDataList2)[0]))
	allDateKey.sort()
	resulteSeries = []
	for dateKey in allDateKey:
		if barData1.has_key(dateKey) and barData2.has_key(dateKey):
			resulteSeries.append((barData1[dateKey], barData2[dateKey]))
	return resulteSeries
def fittingSeriesFun(series):
	x, y = zip(*series)
	x = np.log(x)
	y = np.log(y)
	p0 = [1.6,0] # 第一次猜测的函数拟合参数
	plsq = leastsq(residuals, p0, args=(y, x))
	y2 = np.multiply(y,plsq[0][0])
	diff = np.subtract(x,y2)
	STD = np.std(diff)
	return plsq[0], STD
def func(x, p):
	beta, A = p
	a = []
	for i in x:
		a.append(beta*i + A)
	return a
def residuals(p, y, x):
	fx = func(x, p)
	newY = []
	for i in xrange(len(x)):
		newY.append(y[i]-fx[i])
	return newY


def main():
	#读取板块
	loadPlateFun()
	#读取融资融券标的
	loadRZRQStockFun()
	#读取bar数据
	loadBarDataFun()
	#筛选股票对
	stockPairSelectFun()


if __name__ == '__main__':
	main()