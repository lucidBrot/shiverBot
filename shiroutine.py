# Copyright (C) Eric Mink 2018
# This file is an attempt at getting rid of my ugly stateful functions


# A Shiroutine is a function with a state, which can be cleaned from any other function, resetting the Shiroutine to a default state.
class Shiroutine(Object):
    # self.state is a dictionary with whatever state the Shiroutine needs
    # self.setNextDefaultRoutine is a function to set the global variable for the next Shiroutine to execute

    def __init__(self, setNextDefault, initialState={}):
        self.state = initialState
        self.setNextDefaultRoutine = setNextDefault

    # reset to a clean state
    def reset(self, initialState={}):
        pass

    # a function that every Shiroutine needs to provide
    def run(self, msgtext):
        pass



class MamShiroutine(Shiroutine):
    
    def __init__(self, setNextDefault, initialState={}):
        super(Shiroutine, self, setNextDefault, initialState)

    def reset(self, initialState={}):
        self.state = initialState

    def run(self, msgtext):
        pass # TODO: paste mam function here, and add a list of functions that might need to be reset in the global class

