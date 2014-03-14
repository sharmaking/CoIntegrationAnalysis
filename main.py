#!/usr/bin/python
# -*- coding: utf-8 -*-
import multiprocessing
import controller, windowController

def main():
	messageBox = multiprocessing.Queue()
	#窗口进程
	wController = windowController.QWindowsController(messageBox)
	wController.start()
	#策略主进程
	controller.main(messageBox)

if __name__ == '__main__':
	main()