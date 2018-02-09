# shi_ver_bot_g bot_g
import sys
import time
import random
import datetime
import telepot
import telepot.loop
import telepot.delegate # delegate bot spawning for consistent threads of conversation
import yaml
import logging
import re # regex
import os # current directory

# global variable for the bot_g. Using secret token from config file. That is loaded in main.
# IF YOU'RE IMPORTING THIS FILE, MAKE SURE TO SET bot_g
bot_g = None

# config files
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SECRET_CONFIG_FILE = os.path.join(SCRIPT_DIR, './secret_config.yml')
GENERAL_CONFIG_FILE = os.path.join(SCRIPT_DIR, './config.yml')

# -------------------------------------------------------
# These settings are ignored unless main() is not called
# setup logger - outside of main() because it should also log when this file was loaded in an other way
LOGFILE = './log.shiver'
formatter_g = logging.Formatter('%(asctime)s %(levelname)s %(message)s') # Formatter for the logger
logger_g = None # defined in main / on module import
# -------------------------------------------------------

class ShiverBot(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(ShiverBot, self).__init__(*args, **kwargs)
        self.mam_counter = 0 # which mam message to send next
        self.default_choice = lambda: None # which function to proceed with if there was no new command entered
        # If a previous command is still running and you enter a new command, the new command will be executed (and will set default_choice either to itself again or to None if it is done. This includes every command, because they might have aborted some previous command. To make this easy, just call self.cleanDefaultChoice()
        # This is a function that returns the response to the next query

    def on_chat_message(self, msg):
        self.handle(msg)

    def handle(self, msg): # msg is an array that could be used e.g as msg['chat']['id']  to get the chat id
            global bot_g, logger_g

            content_type, chat_type, chat_id = telepot.glance(msg)
            logger_g.info('Received ({}, {}, {})'.format(content_type, chat_type, chat_id))

            if content_type == 'text':
                    self.handleText(msg)	
            elif content_type == 'document':
                    self.handleDocument(msg)
            elif content_type == 'photo':
                    self.handlePhoto


    # what should be done if a text message is received
    # msg is the whole message object, but assumed to be of content type text
    def handleText(self, msg):
            global logger_g
            msgtext = msg['text']
            content_type, chat_type, chat_id = telepot.glance(msg)
            logger_g.info('Got message <{}> from chat_id {}'.format(msgtext, chat_id))
            self.txtMsgSwitch(msgtext, chat_id) # find out what to do with the text message

    def handlePhoto(self, msg):# TODO
            global logger_g
            logger_g.info('Received a Photo. TODO: image handling')

    def handleDocument(self, msg):# TODO
            global logger_g
            logger_g.info('Received a Document. TODO: doc handling')

    # to be used to map messages to actions
    def txtMsgSwitch(self, msgtext, chat_id):
        global logger_g, bot_g, botname_g # TODO: move the global botname_g to within the bot instance

        # support message@botname
        if msgtext.endswith("@{}".format(botname_g)):
            msgtext = msgtext[:-len("@{}".format(botname_g))]
            #print('got rid of ending. now it\'s only {}'.format(msgtext))

        messageChoices = {
                '/test': self.choice('test'), # TODO: use this function for the other strings as well. # TODO: fix it first. currently, it's being called when the dictionary is initialized... we don't want that. see https://stackoverflow.com/questions/13783211/python-how-to-pass-an-argument-to-a-function-pointer-parameter
                '/help': lambda: 'This is a very helpful message indeed.',
                '/start':lambda: 'Hey. I don\'t do stuff yet.',
                '/func':self.msgIn_testfunction,
                '/mam':self.msgIn_mam
        }
        # default_choice is stored in self. Might be set by functions that want to form a conversation thread
        result = messageChoices.get(msgtext.lower(), self.default_choice)()
        logger_g.info("To {1}  sending <{0}>".format(result, chat_id))

        if result == None:
                self.sender.sendMessage('defaulting to default message')
        elif result == "":
            pass
        else: # send message as specified in dictionary
                self.sender.sendMessage(result) # automatically selects chat_id

        return result

    # set default choice to None or the given choice and clean up any previously running command that was aborted
    # it was aborted if the default choice was not None, because every command must set that to None after it's done.
    def cleanDefaultChoice(self, new_choice=lambda:None):
        #TODO: clean up previous state if needed
        if self.default_choice == self.msgIn_mam:
            self.mam_counter = 0
            print("the previous command was mam. it has been aborted and now cleaned up.")
        self.default_choice = new_choice

    # intended to be put into the messageChoices dictionary
    # returns a function that    sets the new default choice and returns the reply string
    # if you give no new default, it will use the function that returns none. This causes the current implementation of the txtMsgSwitch function to default to some default message.
    def choice(self, reply, new_default=lambda:None):
        # in order for the clean to not be applied every time the dictionary is initialized, we define a new function within this function
        def result_f():
            self.cleanDefaultChoice(new_default)
            return reply() if callable(reply) else lambda : reply # if reply is a function, return that functions return value, otherwise return the reply (string assumingly)
        return result_f

    # Any functions starting with msgIn_ are called when the respective message was received
    # The functions used in txtMsgSwitch are expected to return a reply string. If the reply string is the empty string, no reply will be sent.
    def msgIn_testfunction(self):
        return "testfunction works!"

    def msgIn_mam(self):
        # TODO: start a dialog
        mamList=["Please choose a title",
                "Please enter some text",
                "Please choose an image"]
        # plase call this function again when the user replies with something that is not a command (unless we're done)
        if self.mam_counter < len(mamList)-1: # TODO: fix this logic
            self.default_choice = self.msgIn_mam
        else:
            self.cleanDefaultChoice()
        self.mam_counter = 0 if self.mam_counter==len(mamList)-1 else self.mam_counter+1
        return mamList[self.mam_counter]

# setup a new logger
def setup_logger(name, log_file, formatter, level=logging.INFO, printout=True):
	handler = logging.FileHandler(log_file)        
	handler.setFormatter(formatter)

	logger = logging.getLogger(name)
	logger.setLevel(level)
	logger.addHandler(handler)

	# print to stdout
	if printout:
		out = logging.StreamHandler(sys.stdout)
		out.setLevel(level)
		out.setFormatter(formatter)
		logger.addHandler(out)

	return logger

def main(): # starts everything
	global bot_g, formatter_g, logger_g, botname_g
	# prepare log formatter
	f = open(GENERAL_CONFIG_FILE)
	try:
		config = yaml.safe_load(f)
	finally:
		f.close()
	log_format = config['logger']['format']
	formatter_g = logging.Formatter(log_format) # '%(asctime)s %(levelname)s %(message)s' or similar
	# set logger to file from config
	LOGFILE = config['logger']['log_file']
	logger_g = setup_logger(name=__name__, log_file=LOGFILE, level=logging.DEBUG, formatter=formatter_g, printout=True)
	print 'set logfile to {}'.format(LOGFILE)

	# load token from config file and set global bot_g variable
	f = open(SECRET_CONFIG_FILE) # close file in case of crash
	try:
		secret_config = yaml.safe_load(f)
	finally:
		f.close()
	token = secret_config['mainconfig']['token']
	bot_g = telepot.DelegatorBot(token, [
            telepot.delegate.pave_event_space()(
                    telepot.delegate.per_chat_id(),
                    telepot.delegate.create_open,
                    ShiverBot,
                    timeout=600 # 10 minutes
                ),
            ])
        # store username of the bot
        botname_g = bot_g.getMe()['username']
        print 'I am {}'.format(botname_g)

	# run listener
	telepot.loop.MessageLoop(bot_g).run_as_thread()
	print 'I am listening...'

	while 1:
		time.sleep(10)

# ----------------------------------------------
# Here is where things are done that were not possible at the top
# used to ignore "forward declaration" needs
if __name__=="__main__":
	main()
else:
	logger_g = setup_logger(name=__name__, log_file=LOGFILE, level=logging.DEBUG, formatter=formatter_g)
