class SideEffect (object):
    '''
    Base class of side effects.
    '''

    def trigger(self, message):
        raise Exception('Not implemented')
