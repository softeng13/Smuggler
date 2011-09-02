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
import os

import db

myLogger = logging.getLogger('smugScan')

def getAllPictureInfo(configobj, smugmug, lock):
    myLogger.info("getAllPictures() parent process:'{0}' process id:'{1}".format(os.getppid(),os.getpid()))
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
    
    #get categories
    ids = _getUserCategories(conn, smugmug, lock)
    _getUserSubCategories(conn, smugmug, lock, ids)
    conn.close()
    myLogger.info('Finished Scanning SmugMug')

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

def _getUserCategories(conn, smugmug, lock):
    result = smugmug.categories_get()
    categories = result["Categories"]
    ids = []
    for category in categories:
        ids.append(category["id"])
        lock.acquire()
        db.addUserCategory(conn,category["Type"],category["id"],category["NiceName"],category["Name"])
        lock.release()  
    return ids  

def _getUserSubCategories(conn, smugmug, lock, ids):
    for categoryid in ids:
        result = smugmug.subcategories_get(CategoryID=categoryid)
        subcategories = result["SubCategories"]
        for subcategory in subcategories:
            lock.acquire()
            db.addUserSubCategory(conn,subcategory["id"],subcategory["NiceName"],subcategory["Name"], categoryid)
            lock.release() 

def _emptySmugMugTables(conn, lock):
    lock.acquire()
    db.execute(conn,"DELETE FROM smug_album")
    db.execute(conn,"DELETE FROM smug_image")
    db.execute(conn,"DELETE FROM user_category")
    db.execute(conn,"DELETE FROM user_subcategory")
    lock.release()
