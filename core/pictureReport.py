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
import sys

import db
import core

"""
SELECT sa. category, sa.sub_category, sa.title, si.filename, si.md5_sum, si.id
FROM smug_image si
  INNER JOIN smug_album sa on sa.id = si.album_id
where si.md5_sum NOT  IN (select md5 from pictures)


select * from pictures where md5 not in (select md5_sum from smug_image)


select distinct items.album,
          (select count(*) from smug_album where title = items.album) as album_smug, 
          count(items.filename) as local_image_count,
          (select count(*) from smug_image i inner join smug_album a on a.id = i.album_id where a.title = items.album) as smug_image_count          
from (SELECT category, sub_category, album, filename
from local_image
except
select a.category, a.sub_category, a.title, i.filename
from smug_image  i
  inner join smug_album a on i.album_id = a.id) as items
group by items.album
"""

myLogger = logging.getLogger('pictureReport')

def getCountOfSameFilesWithDifferentName():
    files = db.findSameFilesWithDifferentName()
    for file in files:
        myLogger.debug(file)
    return len(files)


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
        add = "<td>"+column+"</td>"
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

def findMismatchedCategoriesHtml():
    """
    list of albums by name that exist both locally and on smug mug that have 
    different category and/or sub-category. 
    Columns: album name, local category, local sub-category, smug category, 
             smug sub-category
    """
    rows = db.findMismatchedCategories()
    columns = ["Album Name","Local Category","Local SubCategory","SmugMug Category","SmugMug SubCategory"]
    return getTable(columns, rows)

def findMisatchedFilenamesHtml():
    """
    list of local images that have the same md5sum as an image in smug mug, but they 
    have different filenames. 
    Columns: local category, local sub-category, local filename, 
             smug category, smug sub-category, smug filename
    """
    rows = db.findMisatchedFilenames()
    columns = ["Local File Name","SmugMug File Name","Local Category","Local SubCategory","Local Album"]
    return getTable(columns, rows)

def findMissingLocalAlbumsHtml():
    """
    list of albums that are on smug mug that are not found locally. This would
    exclude albums that are local but under different category and sub-category
    Columns: category, sub-category, smug album, number of photos
    """
    rows = db.findMissingLocalAlbums()
    columns = ["SmugMug Category","SmugMug SubCategory","SmugMug Album","# of Images"]
    return getTable(columns, rows)

def findMissingSmugMugAlbumsHtml():
    """
    list of albums that are found local but not found on smug mug. This would
    exclude albums that are local but under different category and sub-category
    Columns: category, sub-category, local album, number of photos    
    """
    rows = db.findMissingSmugMugAlbums()
    columns = ["Local Category","Local SubCategory","Local Album","# of Images"]
    return getTable(columns, rows)
 
def findMissingPicturesHtml():
    """
    list by album show the number of images that are not in both. This will
    only include albums that are in both
    Columns: album, different local photo count(need upload), different smug photo count(need download) 
    """
    rows = db.findMissingPictures()
    columns = ["Album","Need Upload","Need Download"]
    return getTable(columns, rows)

def findDuplicateLocalImageHtml():
    rows = db.findDuplicateLocalImage()
    columns = ["First Filename","Second Filename","Album","SubCategory","Category"]
    return getTable(columns, rows)

def findDuplicateSmugMugImageHtml():
    rows = db.findDuplicateSmugMugImage()
    columns = ["First Filename","Second Filename","Album","SubCategory","Category"]
    return getTable(columns, rows)

def findImagesinDbNotScannedThisRunHtml():
    rows = db.findImagesinDbNotScannedThisRun()
    columns = ["Last Scanned On","Filename","Album","SubCategory","Category"]
    return getTable(columns, rows)
