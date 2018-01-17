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
BOT = None

# config files
SECRET_CONFIG_FILE = './secret_config.yml'
GENERAL_CONFIG_FILE = './config.yml'

# -------------------------------------------------------
# These settings are ignored unless main() is not called
# setup logger - outside of main() because it should also log when this file was loaded in an other way
LOGFILE = './log.shiver'
FORMATTER = logging.Formatter('%(asctime)s %(levelname)s %(message)s') # Formatter for the logger
'''LOGGER = setup_logger(name=__name__, log_file=LOGFILE, level=logging.DEBUG, formatter=FORMATTER)''' # This is done further down where setup_logger is defined
# -------------------------------------------------------

def handle(msg): # msg is an array that could be used e.g as msg['chat']['id']  to get the chat id
	global helpMessage, startMessage, BOT

	content_type, chat_type, chat_id = telepot.glance(msg)
	print 'Received ({}, {}, {})'.format(content_type, chat_type, chat_id)
	logging.info('Received ({}, {}, {})'.format(content_type, chat_type, chat_id))
	# testing the other logger
	LOGGER.info('Received ({}, {}, {})'.format(content_type, chat_type, chat_id))

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

# setup a new logger
def setup_logger(name, log_file, formatter, level=logging.INFO):
	handler = logging.FileHandler(log_file)        
	handler.setFormatter(formatter)

	logger = logging.getLogger(name)
	logger.setLevel(level)
	logger.addHandler(handler)

	return logger

def main(): # starts everything
	global BOT, FORMATTER
	# prepare log formatter
	f = open(GENERAL_CONFIG_FILE)
	try:
		config = yaml.safe_load(f)
	finally:
		f.close()
	log_format = config['logger']['format']
	FORMATTER = logging.Formatter(log_format) # '%(asctime)s %(levelname)s %(message)s' or similar
	# set logger to file from config
	LOGFILE = config['logger']['log_file']

	# load token from config file and set global BOT variable
	f = open(SECRET_CONFIG_FILE) # close file in case of crash
	try:
		secret_config = yaml.safe_load(f)
	finally:
		f.close()
	token = secret_config['mainconfig']['token']
	BOT = telepot.Bot(token)
	# run listener
	telepot.loop.MessageLoop(BOT, handle).run_as_thread()
	print 'I am listening...'

	while 1:
		time.sleep(10)

# ----------------------------------------------
# Here is where things are done that were not possible at the top
LOGGER = setup_logger(name=__name__, log_file=LOGFILE, level=logging.DEBUG, formatter=FORMATTER)
# used to ignore "forward declaration" needs
if __name__=="__main__":
	main()
