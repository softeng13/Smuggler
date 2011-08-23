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
import datetime
import multiprocessing
import thread
import threading
import time

import db
import messaging

myLogger = logging.getLogger('smugScan')

lock = threading.Lock()

class SmugMugScan(object):
    def __init__(self):
        self._process = None
    
    def start(self, smugmug, configobj, lock):
        lock.acquire()
        if self._process == None or not self._process.is_alive():
            myLogger.info("Starting smugmug scan.")
            messaging.messages.addInfo("SmugMug Scan has been Started.")
            self._process = multiprocessing.Process(target=_getAllPictureInfo, args=(smugmug, configobj, lock))
            self._process.start()
            thread.start_new_thread(_checkProcess,(self._process,))
        else:
            myLogger.info("Smugmug scan was already started.")
            messaging.messages.addInfo("SmugMug Scan had already been Started.") 
        lock.release()
    
    def finished(self):
        return self._process == None or not self._process.is_alive()


smugScan = SmugMugScan()

def _checkProcess(process):
    process.join()
    messaging.messages.addInfo('Finished Scanning SmugMug')
        
    
def _getAlbums(conn, smugmug, lock):
    albums = smugmug.albums_get(Extras="LastUpdated")
    
    for album in albums["Albums"]:
        myLogger.debug(album)
        title = album["Title"]
    
        cat = None
        catid = None
        subCat = None
        subCatid = None
        try:
            cat = album["Category"]["Name"]
            catid = album["Category"]["id"]
        except KeyError:
            cat = None
            catid = None
        try:
            subCat = album["SubCategory"]["Name"]
            subCatid = album["SubCategory"]["id"]
        except KeyError:
            subCat = None
            subCatid = None
        lock.acquire()
        db.addSmugAlbum(conn,cat, catid, subCat, subCatid, title, datetime.datetime.strptime(album["LastUpdated"],'%Y-%m-%d %H:%M:%S'), album["Key"], album["id"])
        lock.release() 
    return albums

def _getPictures(album, conn, smugmug, lock):
    pictures = smugmug.images_get(AlbumID=album["id"], AlbumKey=album["Key"], Extras="MD5Sum,LastUpdated,FileName")
    albumId = pictures["Album"]["id"]
    for picture in pictures["Album"]["Images"]:
        lock.acquire()
        db.addSmugImage(conn,albumId, datetime.datetime.strptime(picture["LastUpdated"],'%Y-%m-%d %H:%M:%S'), picture["MD5Sum"], picture["Key"], picture["id"], picture["FileName"])
        lock.release() 
    

def _emptySmugMugTables(conn, lock):
    lock.acquire()
    db.execute(conn,"DELETE FROM smug_album")
    db.execute(conn,"DELETE FROM smug_image")
    lock.release()

def _getAllPictureInfo(smugmug, configobj, lock):
    conn = db.getConn(configobj)
    #start fresh on this
    myLogger.debug("Emptying smugmug tables.")
    _emptySmugMugTables(conn, lock)
    
    #now get the albums 
    myLogger.debug("Getting album info from smugmug.")
    albums = _getAlbums(conn, smugmug, lock)
    for album in albums["Albums"]:
        #and the pictures in each album
        myLogger.debug("geting picture info for album '%s'", album["Title"])
        _getPictures(album, conn, smugmug, lock)
    conn.close()
    myLogger.info('Finished Scanning SmugMug')
