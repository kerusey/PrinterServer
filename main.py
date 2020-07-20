#!/usr/bin/python3
import cups
import os
import imaplib
import email
from email.header import decode_header
import webbrowser
import json
import shutil
import time
from random import choice
from string import ascii_lowercase


baseDir = os.path.dirname(os.path.abspath(__file__)) + "/"



	connection = cups.Connection()
	printerName = [item for item in connection.getPrinters()][0]

	connection.printFile(printerName, fullFileNameToBePrinted, description, {})


