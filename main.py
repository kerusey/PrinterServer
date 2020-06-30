#!/usr/bin/python3
from escpos.printer import Usb
import subprocess
import os

def getPrinterInfo(model:str="HP"):
	usbDevices = str(subprocess.check_output(['lsusb'])).split("\\n")
	usbDevices[0] = usbDevices[0][2:]
	del usbDevices[-1]
	for device in usbDevices:
		if (device.find(model) != -1):
			return [int(pole, 16) for pole in device.split("ID")[1].split(model)[0][1:-1].split(":")]

p = Usb(*getPrinterInfo(), 0)
p.text("Hello World\n")
p.cut()