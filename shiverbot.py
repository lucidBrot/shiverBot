# shi_ver_BOT BOT
import sys
import time
import random
import datetime
import telepot
import telepot.loop
import yaml
import logging

# global variable for the BOT. Using secret token from config file. That is loaded in main.
# IF YOU'RE IMPORTING THIS FILE, MAKE SURE TO SET BOT

#TODO: find out how to set which logs should appear from imported packages

BOT = None

def handle(msg): # msg is an array that could be used e.g as msg['chat']['id']  to get the chat id
	global helpMessage, startMessage, BOT

	content_type, chat_type, chat_id = telepot.glance(msg)
	print 'Received ({}, {}, {})'.format(content_type, chat_type, chat_id)
	logging.info('Received ({}, {}, {})'.format(content_type, chat_type, chat_id))

	if content_type == 'text':
		handleText(msg)	
	elif content_type == 'document':
		handleDocument(msg)
	elif content_type == 'photo':
		handlePhoto


# what should be done if a text message is received
# msg is the whole message object, but assumed to be of content type text
def handleText(msg):
	global BOT, helpMessage, startMessage
	msgtext = msg['text']
	content_type, chat_type, chat_id = telepot.glance(msg)
	print 'Got message <{}> from chat_id {}'.format(msgtext, chat_id)
	logging.info('Got message <{}> from chat_id {}'.format(msgtext, chat_id))
	txtMsgSwitch(msgtext, chat_id) # find out what to do with the text message

def handlePhoto(msg):# TODO
	print 'Received a Photo. TODO: image handling'

def handleDocument(msg):# TODO
	print 'Received a Document. TODO: doc handling'

# TODO: support message@BOTname
# to be used to map messages to actions
def txtMsgSwitch(msgtext, chat_id):
	global BOT
	messageChoices = {
		'/test':'test',
		'/help':'This is a very helpful message indeed.',
		'/start':'Hey. I don\'t do stuff yet.'
	}
	result = messageChoices.get(msgtext, 'default')

	if result == 'default':
		BOT.sendMessage(chat_id, 'defaulting to default message')
	# elif any cases that should be handled elsewhere
	else: # send message as specified in dictionary
		BOT.sendMessage(chat_id, result)

	return result

def main(): # starts everything
	global BOT
	# load token from config file and set global BOT variable
	config = yaml.safe_load(open('./config.yml'))
	token = config['mainconfig']['token']
	BOT = telepot.Bot(token)
	# run listener
	telepot.loop.MessageLoop(BOT, handle).run_as_thread()
	print 'I am listening...'

	while 1:
		time.sleep(10)


# used to ignore "forward declaration" needs
if __name__=="__main__":
	logging.basicConfig(level=logging.DEBUG, filename="logfile.txt", filemode="a+",
						format="%(asctime)-15s %(levelname)-8s %(message)s")
						#TODO: find out how this works
	logging.info("Starting logging...")
	main()
