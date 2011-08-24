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
import multiprocessing

import db
import messaging
import thread
import webUtil

myLogger = logging.getLogger('syncUtil')

###############################################################################
#                                                                             #
#    Below are used to generate some info for the frontend.                   #
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
    #columnsclass = [None, None, "hidden", None, "hidden"]
    columnsclass = [None, None, None, None, None]
    if len(rows) == 0:
        return ""
    else:
        return webUtil.getTable(columns, rows, columnsclass)


###############################################################################
#                                                                             #
#    Below actually do the work.                                              #
#                                                                             #
###############################################################################

class SmugMugSync(object):
    def __init__(self):
        self._process = None
    
    def start(self, smugmug, configobj, lock):
        lock.acquire()
        if self._process == None or not self._process.is_alive():
            myLogger.info("Starting smugmug sync.")
            messaging.messages.addInfo("SmugMug Sync has been Started.")
            self._process = multiprocessing.Process(target=sync, args=(configobj, smugmug, lock))
            self._process.start()
            thread.start_new_thread(_checkProcess,(self._process,))
        else:
            myLogger.info("SmugMug sync was already started.")
            messaging.messages.addInfo("SmugMug Sync had already been Started.") 
        lock.release()

smugmugsync = SmugMugSync()

def _checkProcess(process):
    process.join()
    messaging.messages.addInfo('Finished Sync with SmugMug')

def sync(configobj, smugmug, lock):
    conn = db.getConn(configobj)
    sync = datetime.now()
    _createMissingContainers(conn, smugmug,sync,lock)

def _createMissingContainers(conn,smugmug, sync, lock):
    _createMissingCategories(conn,smugmug, sync, lock)
    _createMissingSubCategories(conn,smugmug, sync, lock)
    _createMissingAlbums(conn,smugmug, sync, lock)

def _createMissingCategories(conn,smugmug, sync, lock):
    categories = db.missingSmugMugCategories(conn)
    for category in categories:
        result = smugmug.categories_create(Name=category[0])
        id = result["Category"]["id"]
        myLogger.debug("Category created: '%s' and id '%s'", category[0], id)
        lock.acquire()
        db.insertCategoryLog(conn, id, category[0], sync)
        lock.release()
    
def _createMissingSubCategories(conn,smugmug, sync, lock):
    subcategories = db.missingSmugMugSubCategories(conn)
    for subcategory in subcategories:
        result = smugmug.subcategories_create(Name=subcategory[0], CategoryID=subcategory[2])
        id = result["SubCategory"]["id"]
        myLogger.debug("SubCategory created: '%s' and id '%s'", subcategory[0], id)
        lock.acquire()
        db.addUserSubCategory(conn,id,"",subcategory[0], subcategory[2])
        db.insertSubCategoryLog(conn, id, subcategory[0],subcategory[1], sync)
        lock.release()
    

def _createMissingAlbums(conn,smugmug, sync, lock):
    albums = db.missingSmugMugAlbums(conn)
    for album in albums:
        if album[2] == None: #no category or subcaategory
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
        