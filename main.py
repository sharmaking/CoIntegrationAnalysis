#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt4 import QtGui
import controller, mainWindow, sys

def main():
	app = QtGui.QApplication(sys.argv)
	QMain = mainWindow.QMainWindow()
	controller.main(QMain)
	#显示主窗口
	QMain.show()
	sys.exit(app.exec_())
	

if __name__ == '__main__':
	main()