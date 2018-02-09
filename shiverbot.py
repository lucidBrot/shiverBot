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
        self.default_choice = self.choice(None, reset_state=False, new_default=lambda msgtext:None) # which function to proceed with if there was no new command entered
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
                    self.handlePhoto(msg)


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

        messageChoices = { # dictionary functions are expected to take the message text as argument and return an answer that will be sent to the user
                '/test': self.choice('test'),
                '/help': self.choice('This is a very helpful message indeed.'),
                '/start': self.choice('Hey. I don\'t do stuff yet.'),
                '/func': self.choice(self.msgIn_testfunction),
                '/mam':self.msgIn_mam # not using choice by design: msgIn_mam decides by itself when to clean the default value.
        }

        [msgCommand, msgContent] = msgtext.split(' ',1) # split on first space
        if msgCommand not in messageChoices:
            msgContent = "{0} {1}".format(msgCommand, msgContent) # re-add space and make the whole thing content if it's not in the dict
            # leave msgCommand the same so that the next query will also decide that it is not in the dictionary and then forward the whole string in msgContent
        
        # default_choice is stored in self. Might be set by functions that want to form a conversation thread
        # If the new message is not a command, do not wipe the current state.
        result = messageChoices.get(msgCommand.lower(), self.choice(self.default_choice, reset_state=False))(msgContent)
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
    def cleanDefaultChoice(self, new_choice=lambda msgtext:None):
        # TODO: clean the state of function-specific variables. Maybe use a dictionary for that. Or better, a mam object that features a cleanMyState function? No that would be difficult because we have a common default value that we want to access. a dict should suffice.
        # clean up previous state if needed
        if self.default_choice == self.msgIn_mam:
            self.mam_counter = 0
            print("the previous command was mam. it has been aborted and now cleaned up.")
        self.default_choice = new_choice

    # intended to be put into the messageChoices dictionary
    # returns a function that    sets the new default choice and returns the reply string
    # if you give no new default, it will use the function that returns none. This causes the current implementation of the txtMsgSwitch function to default to some default message.
    # set reset_state to false if you want to use this only as a wrapper function without a side-effect of cleaning the state variables
    def choice(self, reply, new_default=lambda msgtext:None, reset_state=True):
        # in order for the clean to not be applied every time the dictionary is initialized, we define a new function within this function
        def result_f(received_msg_text):
            if reset_state:
                self.cleanDefaultChoice(new_default)
            return reply(received_msg_text) if callable(reply) else reply # if reply is a function, return that functions return value, otherwise return the reply (string assumingly)
        return result_f

    # Any functions starting with msgIn_ are called when the respective message was received
    # The functions used in txtMsgSwitch are expected to return a reply string. If the reply string is the empty string, no reply will be sent.
    def msgIn_testfunction(self, msgtext):
        return "testfunction works! {0}".format(msgtext)

    def msgIn_mam(self, message_text):
        # TODO: start a dialog
        mamList=["Please choose a title",
                "Please enter some text",
                "Please choose an image"]

        self.mam_counter += 1
        # "please call this function again when the user replies with something that is not a command"
        # if the next message would be out of bounds, reset the default choice and my state. otherwise make sure that we are called again.
        if self.mam_counter < len(mamList):
            self.default_choice = self.msgIn_mam
        else:
            self.cleanDefaultChoice() # do that at the end of this function, because it resets mams state also.
            # This already does mam_counter = 0
        
        return mamList[self.mam_counter-1] # current message

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
