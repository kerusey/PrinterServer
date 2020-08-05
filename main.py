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
EmailCredits = json.load(open(baseDir + "EmailCredits.json"))
ignoredExtensions = ["html", "css", "pyc"]

# Setting up email server
casheFolder = "CasheEmailFolder"
if not os.path.isdir(casheFolder):
	os.mkdir(casheFolder)
imap = imaplib.IMAP4_SSL("imap.gmail.com")
imap.login(EmailCredits['login'], EmailCredits['password']) # loggining
# Setting up email server

print("Server has been configured!\nProcessing listening to your mail...")

def genRandomString(length:int=15):
	return ''.join(choice(ascii_lowercase) for i in range(length))

def printServer(fullFileNameToBePrinted:str, description:str = "maintance"): # Works pretty fine
	connection = cups.Connection()
	printerName = [item for item in connection.getPrinters()][0]

	connection.printFile(printerName, fullFileNameToBePrinted, description, {})

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
	while(True):
		currentNumberQueue = int(open(baseDir + "settings.txt").read())
		messagesInMail = int(imap.select("INBOX")[1][0])

		if (currentNumberQueue <= messagesInMail):
			for message in range(currentNumberQueue, messagesInMail + 1):
				currentMessageObject = getMessageObject(message)
				if ('destinationPath' in currentMessageObject):
					fileList = os.listdir(currentMessageObject['destinationPath'])
					for item in fileList:
						try:
							if (not item.split(".")[1] in ignoredExtensions):
								print(item)
								printServer(currentMessageObject['destinationPath'] + "/" + item)
						except Exception:
							pass
		else:
			time.sleep(60)

		shutil.rmtree(casheFolder)
		os.mkdir(casheFolder)
		open(baseDir + "settings.txt", "w").write(str(messagesInMail + 1))

main()
