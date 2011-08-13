'''
Copyright (c) 2011 Jacob K. Schoen (jacob.schoen@gmail.com)

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in 
the Software without restriction, including without limitation the rights to 
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies 
of the Software, and to permit persons to whom the Software is furnished to do 
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all 
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE 
SOFTWARE.
'''
import threading

INFO = 'info'
ERROR = 'error'

threadLock = threading.Lock()

class MessageQueue(object):
    def __init__(self):
        self._queue = []
        
    def addInfo(self, message):
        threadLock.acquire()
        self._queue.append(Message(message, INFO))
        threadLock.release()
    
    def addError(self, message):
        threadLock.acquire()
        self._queue.append(Message(message, ERROR))
        threadLock.release()
    
    def getMessages(self):
        threadLock.acquire()
        #make a copy of the queue
        copy = self._queue[:]
        #reset the queue to be empty
        self._queue = []
        threadLock.release()
        return copy

messages = MessageQueue()

class Message(object):
    def __init__(self, message, type):
        self.message = message
        self.type = type
        

    
    
        