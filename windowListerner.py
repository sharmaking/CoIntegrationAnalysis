#!/usr/bin/python
# -*- coding: utf-8 -*-
#windowListerner.py
from PyQt4 import QtCore

class QWindowListerner(QtCore.QThread):
	def __init__(self, Qmain, messageBox):
		super(QWindowListerner,self).__init__()
		self.Qmain = Qmain
		self.messageBox = messageBox

	def __del__(self):
		self.wait()

	def run(self):
		while True:
			if not self.messageBox.empty():
				systemMessage = self.messageBox.get()
				print systemMessage
			pass
		pass
 		self.terminate()