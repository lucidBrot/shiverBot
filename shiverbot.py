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
import shiroutine as SR

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
        global bot_g
        self.defSR = SR.DefaultShiroutine(self.setNextDefault, shiverbot=self, globalbot=bot_g ) # in order to only need one instance per chat. reuse this.
        self.default_choice = self.defSR.start # which function to proceed with if there was no new command entered
        # If a previous command is still running and you enter a new command, the new command will be executed (and will set default_choice either to itself again or to self.defSR.start (or .run) if it is done. This includes every command, because they might have aborted some previous command.
        # This is a function that returns the response to the next query
        # Tricky: it must be the method of a Shiroutine, because for images, we use its instance. Sorry for ugly.

        # prepare field for later use
        self.name = None

    def on_chat_message(self, msg):
        self.handle(msg)

    def handle(self, msg): # msg is an array that could be used e.g as msg['chat']['id']  to get the chat id
            global bot_g, logger_g
            # TODO: clean up global usage (no need for bot_g here for example)
            # TODO: handle all the other options http://telepot.readthedocs.io/en/latest/reference.html#telepot.Bot.sendPhoto

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
        content_type, chat_type, chat_id = telepot.glance(msg)
        logger_g.info('Received a Photo from chat_id {}'.format(chat_id))
        logger_g.debug('that photo is {}.'.format(msg))
        # hackish, but less effort than to replace default_choice with a shiroutine instead of a function
        result = self.default_choice.im_self.runImg(msg)
        logger_g.info("To {1}  sending <{0}>".format(result, chat_id))

        if result == None or result == "":
            pass
        else: # send message as specified in dictionary
            self.sender.sendMessage(result) # automatically selects chat_id

        return result 

    def handleDocument(self, msg):# TODO
            global logger_g
            logger_g.info('Received a Document. TODO: doc handling')

    # to be used to map messages to actions
    def txtMsgSwitch(self, msgtext, chat_id):
        global logger_g, bot_g

        # initializes a routine anew whenever this dictionary is used (i.e. when a message arrives) because otherwise multiple users would share the same state.
        messageChoices = { # dictionary functions are expected to take the message text as argument and return an answer that will be sent to the user
                '/test': self.choice('test'), # choice cleans the default routine and then calls the reply or a str
                '/help': self.choice('This is a very helpful message indeed.'), # TODO: better help message
                '/start': self.choice('Hey. I don\'t do stuff yet.'), # TODO: better start message
                '/mam':SR.MamShiroutine(self.setNextDefault, shiverbot=self, globalbot = bot_g).start, # not using choice by design: mam decides by itself when to clean the default value.
                '/rout':SR.TestShiroutine(self.setNextDefault, shiverbot=self, globalbot = bot_g).start,
                }

        # support message@botname
        if msgtext.endswith("@{}".format(bot_g.name)):
            msgtext = msgtext[:-len("@{}".format(bot_g.name))]
            #print('got rid of ending. now it\'s only {}'.format(msgtext)) 

        if msgtext.count(' ') > 0:
            [msgCommand, msgContent] = msgtext.split(' ',1) # split on first space
            if msgCommand not in messageChoices:
                msgContent = "{0} {1}".format(msgCommand, msgContent) # re-add space and make the whole thing content if it's not in the dict
                # leave msgCommand the same so that the next query will also decide that it is not in the dictionary and then forward the whole string in msgContent
        else:
            msgCommand = msgtext
            msgContent = None if msgtext in messageChoices else msgtext # set content to the whole message text if there's no mapping for it, because then we direct it on as a string in the next query (that will fail as well, because msgCommand is the same as msgtext.
        
        # default_choice is stored in self. Might be set by functions that want to form a conversation thread
        # If the new message is not a command, do not wipe the current state.
        result = messageChoices.get(msgCommand.lower(), self.choice(self.default_choice, reset_state=False))(msgContent)
        logger_g.info("To {1}  sending <{0}>".format(result, chat_id))

        if result == None or result == "":
            pass
        else: # send message as specified in dictionary
                self.sender.sendMessage(result) # automatically selects chat_id

        return result # Though I don't think this will be used anywhere

    # set the next default run function. If it is None, use the DefaultShiroutine.start instead.
    def setNextDefault(self, next_default_f):
        self.default_choice = next_default_f if next_default_f is not None else self.defSR.start

    # intended to be put into the messageChoices dictionary
    # returns a function that    sets the new default choice and returns the reply string
    # if you give no new default, it will use the function that returns none. This causes the current implementation of the txtMsgSwitch function to default to some default message.
    # set reset_state to false if you want to use this only as a wrapper function without a side-effect of cleaning the state variables
    def choice(self, reply, new_default=None, reset_state=True):
        # in order for the clean to not be applied every time the dictionary is initialized, we define a new function within this function
        if new_default is None: # if the new_default is none, the output should be default
            new_default = self.defSR.start

        def result_f(received_msg_text):
            if reset_state:
                self.default_choice = new_default
            return reply(received_msg_text) if callable(reply) else reply # if reply is a function, return that functions return value, otherwise return the reply (string assumingly)
        return result_f

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
	global bot_g, formatter_g, logger_g 
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

        # initialize own name
        bot_g.name = bot_g.getMe()['username']
        print 'I am {}'.format(bot_g.name)

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
	logger_g = setup_logger(name=__name__, log_file=LOGFILE, level=logging.DEBUG, formatter=formatter_g, printout=False)
