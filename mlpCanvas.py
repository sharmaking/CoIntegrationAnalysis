#!/usr/bin/python
# -*- coding: utf-8 -*-
#mlpCanvas.py
import random, datetime, copy
from PyQt4 import QtGui, QtCore

import pylab
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class MyMplCanvas(FigureCanvas):
	"""Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
	def __init__(self):
		fig = Figure(figsize=(500, 400), dpi=100, facecolor="#ffffff")

		self.axes = fig.add_subplot(111)
		# We want the axes cleared every time plot() is called
		self.axes.hold(False)
		self.axes.set_ymargin(0)
		self.axes.set_xmargin(0)

		self.compute_initial_figure()
		#
		FigureCanvas.__init__(self, fig)
		self.setParent(None)

		FigureCanvas.setSizePolicy(self,
			QtGui.QSizePolicy.Expanding,
			QtGui.QSizePolicy.Expanding)
		FigureCanvas.updateGeometry(self)

	def compute_initial_figure(self):
		pass

class MLPDynamicMplCanvas(MyMplCanvas):
	"""A canvas that updates itself every second with a new plot."""
	def __init__(self, QMain):
		super(MLPDynamicMplCanvas,self).__init__()
		self.QMain = QMain
		timer = QtCore.QTimer(self)
		timer.setInterval(1000)
		QtCore.QObject.connect(timer, QtCore.SIGNAL("timeout()"), self.update_figure)
		timer.start()

	def compute_initial_figure(self):
		pass

	def update_figure(self):
		try:
			datas, para = self.QMain.pairTradeStatus[str(self.QMain.curPairKey)]["datas"], self.QMain.pairPara[str(self.QMain.curPairKey)]
			if datas and para:
				data = zip(*datas)
				self.axes.plot_date(pylab.date2num(data[0]), data[1], "-", label='line 1', linewidth=1)
				self.setXYlim(data, para)
				self.draw()
		except Exception:
			pass

	def setXYlim(self, data, para):
		for label in self.axes.get_xaxis().get_ticklabels():
			label.set_fontsize(9)

		if data[1][-1] > 0: 	#正
			if data[1][-1] > para["open"]*0.75:
				self.axes.axhline(y = para["open"], linestyle = "--", linewidth = 0.5, color = "gray")
			if data[1][-1] > para["stop"]*0.85:
				self.axes.axhline(y = para["stop"], linestyle = "--", linewidth = 0.5, color = "red")
			if data[1][-1] < para["close"]*1.15:
				self.axes.axhline(y = para["close"], linestyle = "--", linewidth = 0.5, color = "green")
		else: 					#反
			if data[1][-1] < -para["open"]*0.75:
				self.axes.axhline(y = -para["open"], linestyle = "--", linewidth = 0.5, color = "gray")
			if data[1][-1] < -para["stop"]*0.85:
				self.axes.axhline(y = -para["stop"], linestyle = "--", linewidth = 0.5, color = "red")
			if data[1][-1] > -para["close"]*1.15:
				self.axes.axhline(y = -para["close"], linestyle = "--", linewidth = 0.5, color = "green")

		thisDate = copy.copy(data[0][-1])
		if data[0][-1].time() <= datetime.time(11,30,0):
			self.axes.axis(xmin=pylab.date2num(thisDate.replace(hour=9,minute=30,second=0)), xmax=pylab.date2num(thisDate.replace(hour=11,minute=30)))
		else:
			self.axes.axis(xmin=pylab.date2num(thisDate.replace(hour=13,minute=0,second=0)), xmax=pylab.date2num(thisDate.replace(hour=15,minute=0)))
		pass