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
import core
import db
import datetime

myLogger = logging.getLogger('smugScan')

def getAlbums():
    albums = core.smugmug.albums_get(Extras="LastUpdated")
    
    for album in albums["Albums"]:
        try:
            cat = album["Category"]["Name"]
        except KeyError:
            cat = None
        try:
            subCat = album["SubCategory"]["Name"]
        except KeyError:
            subCat = None
        db.addSmugAlbum(cat, subCat, album["Title"], datetime.datetime.strptime(album["LastUpdated"],'%Y-%m-%d %H:%M:%S'), album["Key"], album["id"])
    return albums

def getPictures(album):
    pictures = core.smugmug.images_get(AlbumID=album["id"], AlbumKey=album["Key"], Extras="MD5Sum,LastUpdated,FileName")
    #print pictures
    albumId = pictures["Album"]["id"]
    for picture in pictures["Album"]["Images"]:
        db.addSmugImage(albumId, datetime.datetime.strptime(picture["LastUpdated"],'%Y-%m-%d %H:%M:%S'), picture["MD5Sum"], picture["Key"], picture["id"], picture["FileName"])

def emptySmugMugTables():
    db.executeSql("DELETE FROM smug_album")
    db.executeSql("DELETE FROM smug_image")

def getAllPictureInfo():
    #start fresh on this
    emptySmugMugTables()
    
    #now get the albums 
    albums = getAlbums()
    for album in albums["Albums"]:
        #and the pictures in each album
        getPictures(album)
    