# -*- coding: utf-8 -*-
import numpy as np
from scipy.optimize import leastsq
import pylab as pl
import csv

data = {}

"""
reader = csv.reader(open("data3.csv"))
for linedata in reader:
	data1, data2 = np.log(float(linedata[2])), np.log(float(linedata[3]))
	if data.has_key(data1):
		data[data1].append(data2)
	else:
		data[data1] = [data2]

Data = []

for x, ys in data.items():
	ave = 0
	for y in ys:
		ave = ave + y
	ave = ave/len(ys)
	Data.append((x, ave))
"""

Data = []
reader = csv.reader(open("data3.csv"))
for linedata in reader:
	Data.append((np.log(float(linedata[2])), np.log(float(linedata[3]))))

print len(Data)

Data = Data[-500:-100]

data = sorted(Data, key=lambda d:d[0])
data = zip(*data)


x = data[0]
y1 = data[1]


def func(x, p):
	beta, A = p
	a = []
	for i in x:
		a.append(beta*i + A)
	return a

def residuals(p, y, x):
	"""
	实验数据x, y和拟合函数之间的差，p为拟合需要找到的系数
	"""
	fx = func(x, p)
	newY = []
	for i in xrange(len(x)):
		newY.append(y[i]-fx[i])
	return newY

#print "-----------------"
#
#x = np.linspace(0, 1000)
#
#y1 = 2 * np.random.randn(len(x)) # 加入噪声之后的实验数据 
#
#print x
#print y1

p0 = [1.6,0.1] # 第一次猜测的函数拟合参数

# 调用leastsq进行数据拟合
# residuals为计算误差的函数
# p0为拟合参数的初始值
# args为需要拟合的实验数据
plsq = leastsq(residuals, p0, args=(y1, x))

y2 = np.multiply(y1,plsq[0][0])
diff = np.subtract(x,y2)
STD = np.std(diff)


print u"拟合参数", plsq, STD

pl.plot(x, y1, label=u"带噪声的实验数据")
#pl.plot(x, func(x, p0), label=u"元素数据")
pl.plot(x, func(x, plsq[0]), label=u"拟合数据")
pl.legend()
pl.show()