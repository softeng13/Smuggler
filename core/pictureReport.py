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

myLogger = logging.getLogger('pictureReport')

def getHeaderRow(columns):
    result = "<thead><tr>"
    for column in columns:
        add = "<th>"+column+"</th>"
        result = result + add
    result = result + "</tr></thead>"
    return result

def getResultRow(columns, css):
    result = "<tr  class=\""+css+"\">"
    for column in columns:
        add = "<td>"+str(column)+"</td>"
        result = result + add
    result = result + "</tr>"
    return result

def getTable(columns, rows):
    table = "<table>"
    table = table + getHeaderRow(columns) + "<tbody>"
    css = 'odd'
    for row in rows:
        table = table + getResultRow(row,css)
        if (css == 'odd'):
            css = 'even'
        else:
            css ='odd'
    
    table = table + "</tbody></table>"
    myLogger.debug(table)
    return table

def findMismatchedCategoriesHtml(conn):
    """
    list of albums by name that exist both locally and on smug mug that have 
    different category and/or sub-category. 
    """
    rows = db.findMismatchedCategories(conn)
    columns = ["Album Name","Local Category","Local SubCategory","SmugMug Category","SmugMug SubCategory"]
    return getTable(columns, rows)

def findMisatchedFilenamesHtml(conn):
    """
    list of local images that have the same md5sum as an image in smug mug, but they 
    have different filenames. 
    """
    rows = db.findMisatchedFilenames(conn)
    columns = ["Local File Name","SmugMug File Name","Local Category","Local SubCategory","Local Album"]
    return getTable(columns, rows)

def findMissingLocalAlbumsHtml(conn):
    """
    list of albums that are on smug mug that are not found locally. This would
    exclude albums that are local but under different category and sub-category
    """
    rows = db.findMissingLocalAlbums(conn)
    columns = ["SmugMug Category","SmugMug SubCategory","SmugMug Album","# of Images"]
    return getTable(columns, rows)

def findMissingSmugMugAlbumsHtml(conn):
    """
    list of albums that are found local but not found on smug mug. This would
    exclude albums that are local but under different category and sub-category
    """
    rows = db.findMissingSmugMugAlbums(conn)
    columns = ["Local Category","Local SubCategory","Local Album","# of Images"]
    return getTable(columns, rows)
 
def findMissingPicturesHtml(conn):
    """
    list by album show the number of images that are not in both. This will
    only include albums that are in both
    """
    rows = db.findMissingPictures(conn)
    columns = ["Album","Need Upload","Need Download"]
    return getTable(columns, rows)

def findDuplicateLocalImageHtml(conn):
    """
    list duplicate files found in a local album.
    """
    rows = db.findDuplicateLocalImage(conn)
    columns = ["First Filename","Second Filename","Album","SubCategory","Category"]
    return getTable(columns, rows)

def findDuplicateSmugMugImageHtml(conn):
    """
    list duplicate files found in a SmugMug album.
    """
    rows = db.findDuplicateSmugMugImage(conn)
    columns = ["First Filename","Second Filename","Album","SubCategory","Category"]
    return getTable(columns, rows)

def findImagesinDbNotScannedThisRunHtml(conn):
    """
    Finds the images that where found on previous scans that was not
    found in the latest scan.
    """
    rows = db.findImagesinDbNotScannedThisRun(conn)
    columns = ["Last Scanned On","Filename","Album","SubCategory","Category"]
    return getTable(columns, rows)
