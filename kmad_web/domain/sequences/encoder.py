

def SequencesEncoder(object):
    def __init__(self):
        self._sequences = []

    def encode(self, sequences):
        self._sequences = sequences
