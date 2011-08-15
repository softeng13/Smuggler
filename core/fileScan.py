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
import os
import hashlib
import core
import db
import datetime
import threading

import messaging

myLogger = logging.getLogger('fileScan')

threadLock = threading.Lock()

class LocalScan(object):
    def __init__(self):
        self._scanThread = None
    
    def start(self):
        threadLock.acquire()
        if self._scanThread == None or not self._scanThread.isAlive():
            messaging.messages.addInfo("Local Scan has been Started.")
            self._scanThread = _FileScan()
            self._scanThread.start()
            myLogger.info("Local File Scan has been started. isAlive: %s", self._scanThread.isAlive())
        else:
            messaging.messages.addInfo("!!! Local Scan had already been Started.") 
        threadLock.release()
    
    def finished(self):
        return self._scanThread == None or not self._scanThread.isAlive()
        
class _FileScan(threading.Thread):
    def run(self):
        self._findPictures()

    def _md5(self,file):
        f = open(file,'rb')
        m = hashlib.md5()
        while True:
            data = f.read(10240)
            if len(data) == 0:
                break
            m.update(data)
        return m.hexdigest()

    def _findPictures(self):
        myLogger.info("_FileScan Started. %s",self.getName())
        now = datetime.datetime.now()
        for root, dirs, files in os.walk(core.PICTURE_ROOT):
            for name in files:
                fullname = os.path.join(root, name)
                myLogger.debug("FileName: %s", fullname)
                basename, extension = os.path.splitext(fullname)
                if extension.lower() in core.EXTENSIONS:
                    myLogger.debug(format(fullname.lstrip(core.PICTURE_ROOT)))
                    self._processFoundFile(fullname, now)
        #cleanup what we can, for images that have been moved            
        self._cleanup()
        messaging.messages.addInfo('Finished Scanning Local Files.')
    
    def _processFoundFile(self,pictureFile, timestamp):
        last_updated = datetime.datetime.fromtimestamp(os.path.getmtime(pictureFile))
        md5_sum = self._md5(pictureFile)
        pictureFile = format(pictureFile.lstrip(core.PICTURE_ROOT))
        
        path_root = core.PICTURE_ROOT
        album = os.path.basename(os.path.dirname(pictureFile))
        file_name = os.path.basename(pictureFile)
        sub_category = os.path.basename(os.path.dirname(os.path.dirname(pictureFile)))
        category = os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(pictureFile))))
        if category == "" or category == None:
            category = sub_category
            sub_category = None
    
        myLogger.debug("path_root: '%s', album: '%s', last_updated: '%s', md5_sum: '%s', file_name: '%s', sub_category: '%s', category: '%s', file_path: '%s', timestamp: '%s'", path_root, album ,last_updated,md5_sum,file_name,sub_category,category,pictureFile, timestamp)
        db.addLocalImage(sub_category, category, album, last_updated, md5_sum, path_root, file_name, pictureFile, timestamp)
    
    
    def _cleanup(self):
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
        db.executeSql(sql)
        
localScan = LocalScan()
