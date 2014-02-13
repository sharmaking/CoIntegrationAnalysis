# -*- coding: utf-8 -*-
import os, csv, datetime

Files = []
Data = {}	#key = 

#创建文件访问列表
def creatReadingFileList():
	global Files
	list_dirs = os.walk("E:\Workspace\Wang\PyWork\sample\\60")
	for root, folders, files in list_dirs:
		for f in files:
			if f[-3:] == "csv":
				path = os.path.join(root, f)
				Files.append(path)

def readFile():
	global Data
	for File in Files:
		reader = csv.reader(open(File))
		print File
		for data in reader:
			key = datetime.datetime.strptime(data[1]+data[2], "%Y%m%d%H%M%S")
			if Data.has_key(key):
				if data[0] == "600000":
					Data[key][0] = float(data[3])
				elif data[0] == "601169":
					Data[key][1] = float(data[3])
				elif data[0] == "600648":
					Data[key][2] = float(data[3])
				elif data[0] == "600663":
					Data[key][3] = float(data[3])
				elif data[0] == "600839":
					Data[key][4] = float(data[3])
				elif data[0] == "600868":
					Data[key][5] = float(data[3])
			else:
				Data[key] = [0,0,0,0,0,0]
				if data[0] == "600000":
					Data[key][1] = float(data[3])
				elif data[0] == "601169":
					Data[key][2] = float(data[3])
				elif data[0] == "600648":
					Data[key][3] = float(data[3])
				elif data[0] == "600663":
					Data[key][4] = float(data[3])
				elif data[0] == "600839":
					Data[key][4] = float(data[3])
				elif data[0] == "600868":
					Data[key][5] = float(data[3])
	pass

def writeFile():
	logFile = open("data3.csv", "w")
	content = ""
	for key, value in Data.items():
		content = content + "%f,%f,%f,%f,%f,%f\n"%(value[0], value[1], value[2], value[3], value[4], value[5])
	logFile.write(content)
	logFile.close()
	pass

def main():
	creatReadingFileList()
	readFile()
	writeFile()
	pass

if __name__ == '__main__':
	main()