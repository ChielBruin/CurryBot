class Filter (object):
    def __init__(self, id):
        self._id = id

    def update(self):
        pass

    def filter(self, message):
        raise Exception('Filter not implemented')
