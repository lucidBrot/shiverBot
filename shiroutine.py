# Copyright (C) Eric Mink 2018

# import makeAboveMeme either from subdirectory or from global installation.
# Thus, it would be possible to use the global version if no subdir version is installed.
try:
    from MakeAboveMeme.mAm import makeAboveMeme as mAm
except ImportError:
    import mAm

# A Shiroutine is a function with a state, which can be cleaned from any other function, resetting the Shiroutine to a default state.
class Shiroutine(object):
    # self.state is a dictionary with whatever state the Shiroutine needs
    # self.setNextDefaultRoutine is a function to set the global variable for the next Shiroutine to execute
    # self.counter is the number of times this routine was called in succession (without restarting it by typing the same command again)

    def __init__(self, setNextDefault, initialState={}):
        self.state = initialState
        self.initialState = initialState
        self.setNextDefaultRoutine = setNextDefault
        self._counter = 0

    # reset to a clean state on receival of a new command
    def cleanup(self):
        self.counter = 0
        self.state = initialState

    # a function that every Shiroutine needs to provide
    # Called from the next_Default routine setting
    def run(self, msgtext):
        pass

    # start the shiroutine anew because a new command for it was received.
    # Called from the command-mapping dictionary
    def start(self, msgtext):
        self.cleanup()
        return self.run(msgtext)

    # playing around with the property decorator
    @property
    def counter(self):
        return self._counter

    @counter.setter
    def counter(self, value):
        self._counter = value

''' Requirements for the function passed in as setNextDefault:
        must take a function as an argument
        must accept None as a valid input argument => set next routine to default'''


# Make Above Meme
class MamShiroutine(Shiroutine):
    # INHERITED:
    # dict self.state
    # dict self.initialState
    # func self.setNextDefaultRoutine
    # int  self.counter
    
    def __init__(self, setNextDefault, initialState={}):
        super(MamShiroutine, self).__init__(setNextDefault, initialState)

    def cleanup(self):
        # super resets the counter
        super(MamShiroutine, self)

    def run(self, msgtext):
        super(MamShiroutine, self).run(msgtext)
        mamList = [
            "Please choose a title",
            "You set the title to {0}. Please enter some text.".format(msgtext),
            "Please choose an image",
                ]
        # TODO: store inputs in self.state and reset them in cleanup
        # TODO: actually use them to call makeAboveMeme
        self.counter += 1
        i = self.counter - 1
        # if the next message would be out of bounds, reset the default choice and my state. Otherwise make sure that we are called again.
        if self.counter < len(mamList):
            self.setNextDefaultRoutine(self.run) # We want to be called again on the next message
        else:
            self.setNextDefaultRoutine(None)
            self.cleanup() # reset counter and state
        return mamList[i]

    def callMam():
        # TODO: temporary output file
        # TODO: actually use this function, pass it some params
        arguments = {
            '--comments': None,
            '--help': False,
            '--image': None,
            '--link': None,
            '--out': './aboveMeme.png',
            '--points': None,
            '--tag': [],
            '--text': None,
            '--title': None,
            '--version': False,
            '-C': None,
            '-X': False
        }
        mAm.main(arguments)


# Testroutine
class TestShiroutine(Shiroutine):
    def run(self, msgtext):
        super(TestShiroutine, self).run(msgtext)
        return "testroutine works! {0}".format(msgtext)
