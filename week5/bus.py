from readerwriterlock import rwlock

class Bus:
    def __init__(self, message=None):
        self.message = message
        self.lock = rwlock.RWLockWriteD()

    def write(self, message):
        with self.lock.gen_wlock():
            self.message = message

    def read(self):
        with self.lock.gen_rlock():
            return self.message