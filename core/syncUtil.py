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
from datetime import datetime
import logging
import os
import threading
import urllib2
import Queue

import db
import fileUtil
import webUtil

myLogger = logging.getLogger('syncUtil')

###############################################################################
#                                                                             #
#    Below are used to generate some Tables for the frontend.                 #
#                                                                             #
###############################################################################

def missingSmugMugCategoriesHTML(conn):
    rows = db.missingSmugMugCategories(conn)
    columns = ["Category"]
    if len(rows) == 0:
        return ""
    else:
        return webUtil.getTable(columns, rows)

def missingSmugMugSubCategoriesHTML(conn):
    rows = db.missingSmugMugSubCategories(conn)
    columns = ["SubCategory", "Category", "Category Id"]
    columnsclass = [None, None, "hidden"]
    if len(rows) == 0:
        return ""
    else:
        return webUtil.getTable(columns, rows, columnsclass)

def missingSmugMugAlbumsHTML(conn):
    rows = db.missingSmugMugAlbums(conn)
    columns = ["Album", "Category", "Category Id", "SubCategory", "SubCategory Id"]
    columnsclass = [None, None, "hidden", None, "hidden"]
    if len(rows) == 0:
        return ""
    else:
        return webUtil.getTable(columns, rows, columnsclass)

###############################################################################
#                                                                             #
#     All the action methods are below. They will cause changes locally       #
#     and/or on SmugMug.                                                      #
#                                                                             #
###############################################################################

def sync(configobj, smugmug, lock):
    """
    Does the whole thing, scans, uploads, downloads, etc.  
    """
    myLogger.debug('sync - parent process: %s  process id: %s', os.getppid(), os.getpid())
    conn = db.getConn(configobj)
    sync = datetime.now()
    createMissingContainers(conn, smugmug,sync,lock)

def createMissingContainers(configobj, smugmug, lock):
    """
    This method will create all the missing Categories, SubCategories and Albums
    that were found locally, but not on SmugMug.
    """
    myLogger.debug('createMissingContainers - parent process: %s  process id: %s', os.getppid(), os.getpid())
    conn = db.getConn(configobj)
    sync = datetime.now()
    createMissingCategories(conn,smugmug, sync, lock)
    createMissingSubCategories(conn,smugmug, sync, lock)
    createMissingAlbums(conn,smugmug, sync, lock)

def createMissingCategories(configobj, smugmug, lock):
    """
    Will create any missing Categories on SmugMug that have been found locally,
    but not on SmugMug.
    """
    myLogger.debug('createMissingCategories - parent process: %s  process id: %s', os.getppid(), os.getpid())
    conn = db.getConn(configobj)
    sync = datetime.now()
    categories = db.missingSmugMugCategories(conn)
    for category in categories:
        result = smugmug.categories_create(Name=category[0])
        id = result["Category"]["id"]
        myLogger.debug("Category created: '%s' and id '%s'", category[0], id)
        lock.acquire()
        db.insertCategoryLog(conn, id, category[0], sync)
        lock.release()

def createMissingSubCategories(configobj, smugmug, lock):
    """
    Will create any missing SubCategories on SmugMug that have been found locally,
    but not on SmugMug.
    """
    myLogger.debug('createMissingSubCategories - parent process: %s  process id: %s', os.getppid(), os.getpid())
    conn = db.getConn(configobj)
    sync = datetime.now()
    subcategories = db.missingSmugMugSubCategories(conn)
    for subcategory in subcategories:
        result = smugmug.subcategories_create(Name=subcategory[0], CategoryID=subcategory[2])
        id = result["SubCategory"]["id"]
        myLogger.debug("SubCategory created: '%s' and id '%s'", subcategory[0], id)
        lock.acquire()
        db.addUserSubCategory(conn,id,"",subcategory[0], subcategory[2])
        db.insertSubCategoryLog(conn, id, subcategory[0],subcategory[1], sync)
        lock.release()

def createMissingAlbums(configobj, smugmug, lock):
    """
    Will create any albums on SmugMug that have been found locally, but not on SmugMug.
    Currently uses the SmugMug defaults for the album properties.
    """
    myLogger.debug('createMissingAlbums - parent process: %s  process id: %s', os.getppid(), os.getpid())
    conn = db.getConn(configobj)
    sync = datetime.now()
    albums = db.missingSmugMugAlbums(conn)
    for album in albums:
        if album[2] == None: #no category or subcategory
            result = smugmug.albums_create(Title=album[0])
        elif album[4] == None: # category but no subcategory
            result = smugmug.albums_create(Title=album[0], CategoryID=album[2])
        else: #has category and subcategory
            result = smugmug.albums_create(Title=album[0], CategoryID=album[2],SubCategoryID=album[4])
        id = result["Album"]["id"]
        key = result["Album"]["Key"]
        myLogger.debug("Album created: '%s' and id '%s' and key '%s'", album[0], id, key)
        lock.acquire()
        db.addSmugAlbum(conn,album[1], album[2], album[3], album[4], album[0], sync, key, id)
        db.insertAlbumLog(conn, id, album[0], album[1], album[3], sync)
        lock.release()

def download(downloadImages, configobj, smugmug, lock):
    """
    This method will download all the missing files 5 at a time.
    """
    myLogger.debug('download - parent process: %s  process id: %s', os.getppid(), os.getpid())
    conn = db.getConn(configobj)
    sync = datetime.now()
    myLogger.debug("getting images to download")
    downloadImages = db.imagesToDownload(conn)
    myLogger.debug("Have list of images that need to be downloaded.")
    #Loop through the images and download them 
    queue = Queue.Queue()
    #spawn a pool of threads, and pass them queue instance 
    for i in range(5):
        t = DownloadThread(queue, conn, configobj, smugmug, lock)
        t.start()
    
    #populate queue with data   
    for downloadImage in downloadImages:
        queue.put(downloadImage)
    
    #wait on the queue until everything has been processed     
    queue.join()    
    myLogger.debug("finished downloading images")
    
class DownloadThread(threading.Thread):
    def __init__(self, queue, conn, configobj, smugmug, lock):
        threading.Thread.__init__(self)
        self._queue = queue
        self._conn = conn
        self._configobj = configobj
        self._smugmug = smugmug
        self._lock = lock
  
    def run(self):
        while True:
            #grabs host from queue
            downloadImage = self._queue.get()
            
            category = downloadImage[0]
            subcategory = downloadImage[1]
            album = downloadImage[2]
            filename = downloadImage[3]
            id = downloadImage[4]
            key = downloadImage[5]
            
            myLogger.debug("going to smugmug to get image url for %s", filename)
            response = self._smugmug.images_getURLs(ImageID=id, ImageKey=key)
            url = response["Image"]["OriginalURL"]
            myLogger.info("Downloading image from '%s'", url)
            filepath = fileUtil.buildfilePath(self._configobj.picture_root, category, subcategory, album)
            fileUtil.mkdir(filepath)
            filepath = filepath+filename
            myLogger.info("Saving downloaded image to '%s'", filepath)
            
            file = urllib2.urlopen(url)
            output = open(filepath,'wb')
            output.write(file.read())
            output.close()
    
            self._lock.acquire()
            db.addLocalImage(self._conn, subcategory, category, album, sync, fileUtil.md5(filepath), self._configobj.picture_root, filename, format(filepath.lstrip(self._configobj.picture_root)), sync)
            self._lock.release() 
        
            #signals to queue job is done
            self._queue.task_done()
