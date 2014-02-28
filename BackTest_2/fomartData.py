#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, csv
import numpy as np

Plate = {}
RZRQ = []
BarData = {}
Results = {}
StockPrice = []

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
	list_dirs = os.walk("F:\\HistoryData\\60")
	for root, folders, files in list_dirs:
		for f in files:
			dataDate = float(f[:8])
			if dataDate > 20130924 and dataDate < 20131224:
				path = os.path.join(root, f)
				reader = csv.reader(open(path))
				print path
				for line in reader:
					if line:
						stock = line[0]
						if stock in RZRQ:
							if not BarData.has_key(stock):
								BarData[stock] = {}
							BarData[stock][int(line[1] + line[2])] = float(line[3])

def test():
	a = {"1":10,"2":5}
	b = {"2":25,"3":9,"4":7}
	print a, b
	pass

def main():
	test()
	#读取融资融券标的
	#loadRZRQStockFun()
	#读取bar数据
	#loadBarDataFun()


if __name__ == '__main__':
	main()