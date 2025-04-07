class StateMachine:
    def __init__(self, initialState):
        self._prevState = initialState
        self._currentState = initialState

	#maybe add in? currently problems w/ idle publishing in enter() before main()
        #self._currentState.enter()
        #self._currentState.run()

    def run(self, state_publisher=None):
        self._prevState = self._currentState
        self._currentState = self._currentState.next()

        if self._prevState != self._currentState:
            self._currentState.enter()

        # check if state publisher is set
        if state_publisher != None:
            message = str(self._currentState)
            # current state when converted looks like: "NAMEState.NAME object at ADDRESS"
            # splitting message until we get NAME
            message = message.split(' ')    #NAMEState.NAME
            message = message[0].split('.') #NAME

            state_publisher.publish(message[1])

        self._currentState.run()

class State:
    def enter(self):
        pass

    def run(self):
        pass

    def next(self):
        pass
