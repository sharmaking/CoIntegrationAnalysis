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
		QtCore.QObject.connect(timer, QtCore.SIGNAL("timeout()"), self.update_figure)
		timer.start(1000)
		
	def compute_initial_figure(self):
		pass

	def update_figure(self):
		pass
		#data = zip(*self.QMain.standardPriceDeviation[0])
		#self.axes.plot_date(pylab.date2num(data[0]), data[1], "-", label='line 1', linewidth=1)
		#self.setXYlim(data)

		#self.draw()

	def setXYlim(self, data):
		#self.axes.axis(ymin=-2.7, ymax=2.7)
		self.axes.axhline(y = 1.6, linestyle = "--", linewidth = 0.5, color = "red")
		self.axes.axhline(y = 0.06, linestyle = "--", linewidth = 0.5, color = "green")
		for label in self.axes.get_xaxis().get_ticklabels():
			label.set_rotation(20)
			label.set_fontsize(9)

		self.axes.set_xlabel('time (s)', fontdict=self.font)
		self.axes.set_ylabel('voltage (mV)', fontdict=self.font)

		thisDate = copy.copy(data[0][-1])
		if data[0][-1].time() <= datetime.time(11,30,0):
			self.axes.axis(xmin=pylab.date2num(thisDate.replace(hour=9,minute=30)), xmax=pylab.date2num(thisDate.replace(hour=11,minute=30)))
		else:
			self.axes.axis(xmin=pylab.date2num(thisDate.replace(hour=13,minute=0)), xmax=pylab.date2num(thisDate.replace(hour=15,minute=0)))
		pass