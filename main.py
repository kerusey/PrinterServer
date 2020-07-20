#!/usr/bin/python3
import cups
import os

baseDir = os.path.dirname(os.path.abspath(__file__)) + "/"

def printServer(fullFileNameToBePrinted:str, description:str = "maintance"): # 
	connection = cups.Connection()
	printerName = [item for item in connection.getPrinters()][0]

	connection.printFile(printerName, fullFileNameToBePrinted, description, {})

printServer(baseDir + "name.txt")
