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
import db
import datetime
import threading
import messaging
import core

myLogger = logging.getLogger('smugScan')

threadLock = threading.Lock()

class SmugMugScan(object):
    def __init__(self):
        self._thread = None
    
    def start(self):
        threadLock.acquire()
        if self._thread == None or not self._thread.isAlive():
            messaging.messages.addInfo("SmugMug Scan has been Started.")
            self._thread = _SmugScan()
            self._thread.start()
        else:
            messaging.messages.addInfo("SmugMug Scan had already been Started.") 
        threadLock.release()
    
    def finished(self):
        return self._thread == None or not self._thread.isAlive()
    
class _SmugScan(threading.Thread):
    def run(self):
        self._getAllPictureInfo()

    def _getAlbums(self):
        albums = core.smugmug.albums_get(Extras="LastUpdated")
        
        for album in albums["Albums"]:
            title = album["Title"]
            try:
                cat = album["Category"]["Name"]
            except KeyError:
                cat = None
            try:
                subCat = album["SubCategory"]["Name"]
            except KeyError:
                subCat = None
            db.addSmugAlbum(cat, subCat, title, datetime.datetime.strptime(album["LastUpdated"],'%Y-%m-%d %H:%M:%S'), album["Key"], album["id"])
        return albums
    
    def _getPictures(self,album):
        pictures = core.smugmug.images_get(AlbumID=album["id"], AlbumKey=album["Key"], Extras="MD5Sum,LastUpdated,FileName")
        albumId = pictures["Album"]["id"]
        for picture in pictures["Album"]["Images"]:
            db.addSmugImage(albumId, datetime.datetime.strptime(picture["LastUpdated"],'%Y-%m-%d %H:%M:%S'), picture["MD5Sum"], picture["Key"], picture["id"], picture["FileName"])
        
    
    def _emptySmugMugTables(self):
        db.executeSql("DELETE FROM smug_album")
        db.executeSql("DELETE FROM smug_image")
    
    def _getAllPictureInfo(self):
        #start fresh on this
        self._emptySmugMugTables()
        
        #now get the albums 
        albums = self._getAlbums()
        for album in albums["Albums"]:
            #and the pictures in each album
            self._getPictures(album)
        messaging.messages.addInfo('Finished Scanning SmugMug')

smugScan = SmugMugScan()        