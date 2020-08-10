#!/usr/bin/python3
import cups
import os
import subprocess
import imaplib
import email
from json import load
from time import sleep
from email.header import decode_header
from shutil import rmtree
from random import choice
from string import ascii_lowercase

baseDir = os.path.dirname(os.path.abspath(__file__)) + "/"
EmailCredits = load(open(baseDir + "EmailCredits.json"))
ignoredExtensions = ["html", "css", "pyc"]
allowedHosts = ["danila.lihh@gmail.com"]

# Setting up email server
casheFolder = baseDir + "CasheEmailFolder"
if not os.path.isdir(casheFolder):
	os.mkdir(casheFolder)
imap = imaplib.IMAP4_SSL("imap.gmail.com")
imap.login(EmailCredits['login'], EmailCredits['password']) # loggining
# Setting up email server

def genRandomString(length:int=15):
	return ''.join(choice(ascii_lowercase) for i in range(length))

def converter(path:str): # TODO remove primary file
	parentPath = ''.join(name + '/' for name in path.split("/")[:-1])
	subprocess.run(["libreoffice", "--headless", "--convert-to", "pdf", "--outdir", parentPath, path],
				   stdout = subprocess.DEVNULL,
				   stderr = subprocess.STDOUT)

	return parentPath

def printServer(fullFileNameToBePrinted:str, description:str = "maintance"): # Works pretty fine
	connection = cups.Connection()
	printerName = [item for item in connection.getPrinters()][0]

	connection.printFile(printerName, fullFileNameToBePrinted, description, {}) # TODO DOCX, DOC, DOCS converter to cups-supportable formats

def getMessageObject(number:int):
	messageObject = {}
	messagesNumber = int(imap.select("INBOX")[1][0])
	status, message = imap.fetch(str(number), "(RFC822)")
	for resource in message:
		if isinstance(resource, tuple):
			message = email.message_from_bytes(resource[1])
			messageObject['topic'] = decode_header(message["Subject"])[0][0] # decoding header of the message
			if isinstance(messageObject['topic'], bytes): # if sender is dummy and wrote a shit in the header
				messageObject['topic'] = messageObject['topic'].decode()
			senderInfo = message.get("From")
			messageObject['senderName'] = senderInfo.split('<')[0][:-1]
			messageObject['senderEmail'] = senderInfo.split('<')[1][:-1]
			messageObject['destinationPath'] = casheFolder + "/" + genRandomString()
			if message.is_multipart():
				for part in message.walk():
					contentType = part.get_content_type()
					contentDisposition = str(part.get("Content-Disposition"))
					try:
						body = part.get_payload(decode=True).decode()
					except Exception:
						pass
					if ("attachment" in contentDisposition):
						filename = part.get_filename() # download attachment
						if (filename):
							if not os.path.isdir(messageObject['destinationPath']):
								os.mkdir(messageObject['destinationPath']) # make a folder for this email (named after the subject)
							filepath = os.path.join(messageObject['destinationPath'], filename)
							open(filepath, "wb").write(part.get_payload(decode=True)) # download attachment and save it
	return messageObject

def main():
	currentNumberQueue = int(open(baseDir + "settings.txt").read())
	messagesInMail = int(imap.select("INBOX")[1][0])
	if (currentNumberQueue <= messagesInMail):
		for message in range(currentNumberQueue, messagesInMail + 1):
			currentMessageObject = getMessageObject(message)
			if (currentMessageObject['senderEmail'] in allowedHosts):
				if ('destinationPath' in currentMessageObject):
					files = os.listdir(currentMessageObject['destinationPath'])
					for index in range(len(files)):
						files[index] = currentMessageObject['destinationPath'] + '/' + files[index]
					for file in files:
						for extension in ['docs', 'doc', 'docx']:
							if (file.find(extension) != -1):
								currentMessageObject['destinationPath'] = converter(file)
								os.remove(file)
								break
					fileList = os.listdir(currentMessageObject['destinationPath'])
					for item in fileList:
						if (not item in ignoredExtensions):
							printServer(currentMessageObject['destinationPath'] + "/" + item)
			else:
				print("spam")
	sleep(20)

	rmtree(casheFolder)
	os.mkdir(casheFolder)
	open(baseDir + "settings.txt", "w").write(str(messagesInMail + 1))

while(True):
	main()
