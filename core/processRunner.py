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

import logging
import multiprocessing
import thread

import messaging

myLogger = logging.getLogger("processRunner")

class Runner(object):
    """
    This class is used to facilitate forking a given action into another process.
    It will pass along a message to the message handler when it starts and 
    finishes the given action. It ensures that the given action is not currently
    running in another process, before starting it again.
    """
    def __init__(self, action, startMessage, finishedMessage, alreadyMessage):
        self._process = None
        self._action = action
        self._startMessage = startMessage
        self._finishedMessage = finishedMessage
        self._alreadyMessage = alreadyMessage
    
    def start(self, smugmug, configobj, lock):
        lock.acquire()
        if self._process == None or not self._process.is_alive():
            myLogger.info(self._startMessage)
            messaging.messages.addInfo(self._startMessage)
            self._process = multiprocessing.Process(target=self._action, args=(configobj, smugmug, lock))
            self._process.start()
            thread.start_new_thread(self._checkProcess,(self._process,self._finishedMessage))
        else:
            myLogger.info(self._alreadyMessage)
            messaging.messages.addInfo(self._alreadyMessage) 
        lock.release()

    def _checkProcess(self, process, message):
        process.join()
        messaging.messages.addInfo(message)