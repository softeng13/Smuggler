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

import datetime
import hashlib
import logging
import multiprocessing
import thread
import threading
import time
import os


import core
import db
import messaging

myLogger = logging.getLogger('fileScan')

lock = threading.Lock()

class LocalScan(object):
    def __init__(self):
        self._process = None
    
    def start(self, configobj, lock):
        lock.acquire()
        if self._process == None or not self._process.is_alive():
            messaging.messages.addInfo("Local Scan has been Started.")
            self._process = multiprocessing.Process(target=_findPictures, args=(configobj,lock))
            self._process.start()
            myLogger.info("Local File Scan has been started. isAlive: %s", self._process.is_alive())
            thread.start_new_thread(_checkProcess,(self._process,))
        else:
            messaging.messages.addInfo("Local Scan had already been Started.") 
        lock.release()
    
    def finished(self):
        return self._process == None or not self._process.is_alive()


localScan = LocalScan()

def _checkProcess(process):
    while (process.is_alive()):
        myLogger.debug("Local Scan process is still running. Sleeping for 30.")
        time.sleep(30)
    messaging.messages.addInfo('Finished Scanning Local Files.')

def _md5(file):
    f = open(file,'rb')
    m = hashlib.md5()
    while True:
        data = f.read(10240)
        if len(data) == 0:
            break
        m.update(data)
    return m.hexdigest()

def _findPictures(configobj, lock):
    conn = db.getConn(configobj)
    myLogger.info("Starting file scan at => %s", configobj.picture_root)
    now = datetime.datetime.now()
    for root, dirs, files in os.walk(configobj.picture_root):
        for name in files:
            fullname = os.path.join(root, name)
            basename, extension = os.path.splitext(fullname)
            if extension.lower() in core.EXTENSIONS:
                myLogger.debug("FileName: %s", fullname)
                _processFoundFile(conn, configobj.picture_root, fullname, now, lock)
    #cleanup what we can, for images that have been moved            
    _cleanup(conn, lock)
    conn.close()

def _processFoundFile(conn, picture_root, pictureFile, timestamp, lock):
    myLogger.debug("_processFoundFile(%s,%s)", picture_root, pictureFile)
    last_updated = datetime.datetime.fromtimestamp(os.path.getmtime(pictureFile))
    md5_sum = _md5(pictureFile)
    pictureFile = format(pictureFile.lstrip(picture_root))
    
    path_root = picture_root
    album = os.path.basename(os.path.dirname(pictureFile))
    file_name = os.path.basename(pictureFile)
    sub_category = os.path.basename(os.path.dirname(os.path.dirname(pictureFile)))
    category = os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(pictureFile))))
    if category == "" or category == None:
        category = sub_category
        sub_category = None

    myLogger.debug("path_root: '%s', album: '%s', last_updated: '%s', md5_sum: '%s', file_name: '%s', sub_category: '%s', category: '%s', file_path: '%s', timestamp: '%s'", path_root, album ,last_updated,md5_sum,file_name,sub_category,category,pictureFile, timestamp)
    lock.acquire()
    db.addLocalImage(conn, sub_category, category, album, last_updated, md5_sum, path_root, file_name, pictureFile, timestamp)
    lock.release() 
    myLogger.debug("_processFoundFile(%s,%s) completed", picture_root, pictureFile)


def _cleanup(conn, lock):
    """
    We need to try to identify albums, or pictures that were not found during 
    the scan, and remove them form the db so they do not show up in the reports
    causing confusion. We will not remove items that have could not be found,
    just the ones that were found somewhere else.
    """
    sql = (
           "DELETE FROM local_image "
            "WHERE rowid IN (SELECT li2.rowid "
            "FROM local_image li "
            " INNER JOIN local_image li2 on li.md5_sum = li2.md5_Sum and li.last_scanned > li2.last_scanned)"
           )
    lock.acquire()
    db.execute(conn, sql)
    lock.release() 
        
