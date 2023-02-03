#
# Author: Kılıçarslan SIMSIKI
#

# 
# This class is for custom join operation on threads that optimizes speed. 
# Instead of main thread calling join on each thread, each thread calls wait and adds itself to the count of threads,
# and removes itself when the task is done. Improves speed. Initialized in main.py

from threading import Condition

class WaitGroup:
    wait_count = 0
    cv = Condition()
    
    def add(self, count):
        self.cv.acquire()
        self.wait_count += count
        self.cv.release()
        
    def done(self):
        self.cv.acquire()
        if self.wait_count > 0:
            self.wait_count -= 1
        if self.wait_count == 0:
            self.cv.notify_all()
        self.cv.release()
        
    def wait(self):
        self.cv.acquire()
        while self.wait_count > 0:
            self.cv.wait()
        self.cv.release()