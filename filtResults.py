#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, csv

Results = []
StockPrice = []

def loadStockPrice():
	global StockPrice
	reader = csv.reader(open("20140218.csv"))
	for line in reader:
		if line:
			if float(line[3]) > 5:
				StockPrice.append(line[0])

def loadResultsFun():
	global Results
	reader = csv.reader(open("results.csv"))
	for line in reader:
		key = line[0]
		stock1 = key[0:6]
		stock2 = key[7:13]
		if stock1 in StockPrice and stock2 in StockPrice:
			Results.append(line)
def main():
	#读取价格
	loadStockPrice()
	#读取分析结果
	loadResultsFun()
	
	logFile = open("results2.csv", "a")
	content = ""
	for result in Results:
		content = content + "%s,%s,%s\n"%(result[0], result[1], result[2])
	logFile.write(content)
	logFile.close()


if __name__ == '__main__':
	main()