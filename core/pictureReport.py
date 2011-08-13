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

def findMismatchedCategories():
    """
    list of albums by name that exist both locally and on smug mug that have 
    different category and/or sub-category. 
    Columns: album name, local category, local sub-category, smug category, 
             smug sub-category
    """
    rows = db.findMismatchedCategories()
    report = (
              "The following table lists all the albums that are both located in SmugMug and Locally but their Category and/or sub-categories do not match.\n\n"
              "Album Name                      Local Category                  Local SubCategory               SmugMug Category                SmugMug Category\n"
              "---------------------------------------------------------------------------------------------------------------------------------------------------------------\n"
              )
    #print report
    reportRows = [report]
    for row in rows:
        line = row[0].ljust(32)+row[1].ljust(32)+row[2].ljust(32)+row[3].ljust(32)+row[4].ljust(32)+"\n"
        #print line
        reportRows.append(line)
    return ''.join(reportRows)

def findMisatchedFilenames():
    """
    list of local images that have the same md5sum as an image in smug mug, but they 
    have different filenames. 
    Columns: local category, local sub-category, local filename, 
             smug category, smug sub-category, smug filename
    """
    rows = db.findMisatchedFilenames()
    report = (
              "The following table lists all the local images that have the same MD5 Checksum as an image on SmugMug, but they have different filenames.\n\n"
              "Local File Name                 SmugMug File Name               Local Category                  Local Sub-Category              Local Album                     \n"
              "----------------------------------------------------------------------------------------------------------------------------------------------------------------\n"
              )
    #print report
    reportRows = [report]
    for row in rows:
        line = row[0].ljust(32)+row[1].ljust(32)+(row[2].ljust(32) if row[2] <> None else " ".ljust(32))+(row[3].ljust(32) if row[3] <> None else " ".ljust(32))+row[4].ljust(32)+"\n"
        #print line
        reportRows.append(line)
    return ''.join(reportRows)

def findMissingLocalAlbums():
    """
    list of albums that are on smug mug that are not found locally. This would
    exclude albums that are local but under different category and sub-category
    Columns: category, sub-category, smug album, number of photos
    """
    rows = db.findMissingLocalAlbums()
    report = (
              "The following table lists all the albums on SmugMug that could not be found locally. This does not include albums that are found\n"
              "locally under different category and/or sub-category.\n\n"
              "SmugMug Category                SmugMug Sub-Category            SmugMug Album                   # of Images                     \n"
              "--------------------------------------------------------------------------------------------------------------------------------\n"
              )
    #print report
    reportRows = [report]
    for row in rows:
        line = (row[0].ljust(32) if row[0] <> None else " ".ljust(32))+(row[1].ljust(32) if row[1] <> None else " ".ljust(32))+row[2].ljust(32)+str(row[3]).ljust(32)+"\n"
        #print line
        reportRows.append(line)
    return ''.join(reportRows)

def findMissingSmugMugAlbums():
    """
    list of albums that are found local but not found on smug mug. This would
    exclude albums that are local but under different category and sub-category
    Columns: category, sub-category, local album, number of photos    
    """
    rows = db.findMissingSmugMugAlbums()
    report = (
              "The following table lists all the albums found locally that could not be found on SmugMug. This does not include albums that are\n"
              "found locally under different category and/or sub-category.\n\n"
              "Local Category                  Local Sub-Category              Local Album                     # of Images                     \n"
              "--------------------------------------------------------------------------------------------------------------------------------\n"
              )
    #print report
    reportRows = [report]
    for row in rows:
        line = (row[0].ljust(32) if row[0] <> None else " ".ljust(32))+(row[1].ljust(32) if row[1] <> None else " ".ljust(32))+row[2].ljust(32)+str(row[3]).ljust(32)+"\n"
        #print line
        reportRows.append(line)
    return ''.join(reportRows)
 
def findMissingPictures():
    """
    list by album show the number of images that are not in both. This will
    only include albums that are in both
    Columns: album, different local photo count(need upload), different smug photo count(need download) 
    """
    rows = db.findMissingPictures()
    report = (
              "The following table lists the number of images that need to be uploaded or downloaded for albums\n"
              "that are found both locally and on SmugMug.\n\n"
              "Album                           Need Upload                     Need Download                   \n"
              "------------------------------------------------------------------------------------------------\n"
              )
    #print report
    reportRows = [report]
    for row in rows:
        line = row[0].ljust(32)+str(row[1]).ljust(32)+str(row[2]).ljust(32)+"\n"
        #print line
        reportRows.append(line)
    return ''.join(reportRows)

def findDuplicateLocalImage():
    rows = db.findDuplicateLocalImage()
    report = (
              "The following table lists the duplicate images found locally for an album. Note it does not include duplicates where the images are in different albums.\n"
              "that are found both locally and on SmugMug.\n\n"
              "First Filename                  Second Filename                 Album                           Sub-Category                    Category                        \n"
              "----------------------------------------------------------------------------------------------------------------------------------------------------------------\n"
              )
    #print report
    reportRows = [report]
    for row in rows:
        line = row[0].ljust(32)+row[1].ljust(32)+row[2].ljust(32)+(row[3].ljust(32) if row[3] <> None else " ".ljust(32))+(row[4].ljust(32) if row[4] <> None else " ".ljust(32))+"\n"
        #print line
        reportRows.append(line)
    return ''.join(reportRows)

def findDuplicateSmugMugImage():
    rows = db.findDuplicateSmugMugImage()
    report = (
              "The following table lists the duplicate images found on SmugMug for an album. Note it does not include duplicates where the images are in different albums.\n"
              "that are found both locally and on SmugMug.\n\n"
              "First Filename                  Second Filename                 Album                           Sub-Category                    Category                        \n"
              "----------------------------------------------------------------------------------------------------------------------------------------------------------------\n"
              )
    #print report
    reportRows = [report]
    for row in rows:
        line = row[0].ljust(32)+row[1].ljust(32)+row[2].ljust(32)+(row[3].ljust(32) if row[3] <> None else " ".ljust(32))+(row[4].ljust(32) if row[4] <> None else " ".ljust(32))+"\n"
        #print line
        reportRows.append(line)
    return ''.join(reportRows)

def findImagesinDbNotScannedThisRun():
    rows = db.findImagesinDbNotScannedThisRun()
    report = (
              "The following table lists all the local images that had been found on a previous scan, that were not found on the last scan.\n"
              "that are found both locally and on SmugMug.\n\n"
              "Last Scanned On                 Filename                        Album                           Sub-Category                    Category                        \n"
              "----------------------------------------------------------------------------------------------------------------------------------------------------------------\n"
              )
    #print report
    reportRows = [report]
    for row in rows:
        line = row[0].ljust(32)+row[1].ljust(32)+row[2].ljust(32)+(row[3].ljust(32) if row[3] <> None else " ".ljust(32))+(row[4].ljust(32) if row[4] <> None else " ".ljust(32))+"\n"
        #print line
        reportRows.append(line)
    return ''.join(reportRows)

def generateReports():
    sys.stdout.write('\rGenerating Reports: '.ljust(80))
    sys.stdout.flush()
    sys.stdout.write('\rGenerating Reports: Finding mismatched Categories'.ljust(80))
    sys.stdout.flush()
    mismatchedCategories = findMismatchedCategories()
    
    sys.stdout.write('\rGenerating Reports: '.ljust(80))
    sys.stdout.flush()
    sys.stdout.write('\rGenerating Reports: Finding mismatched Filenames'.ljust(80))
    sys.stdout.flush()
    mismatchedFilenames = findMisatchedFilenames()
    
    sys.stdout.write('\rGenerating Reports: '.ljust(80))
    sys.stdout.flush()
    sys.stdout.write('\rGenerating Reports: Finding Missing Local Albums'.ljust(80))
    sys.stdout.flush()
    missingLocal = findMissingLocalAlbums()
    
    sys.stdout.write('\rGenerating Reports: '.ljust(80))
    sys.stdout.flush()
    sys.stdout.write('\rGenerating Reports: Finding Missing SmugMug Albums'.ljust(80))
    sys.stdout.flush()
    missingSmug = findMissingSmugMugAlbums()
    
    sys.stdout.write('\rGenerating Reports: '.ljust(80))
    sys.stdout.flush()
    sys.stdout.write('\rGenerating Reports: Finding Missing Images'.ljust(80))
    sys.stdout.flush()
    missingImages = findMissingPictures()
    
    sys.stdout.write('\rGenerating Reports: '.ljust(80))
    sys.stdout.flush()
    sys.stdout.write('\rGenerating Reports: Finding Duplicate Local Images'.ljust(80))
    sys.stdout.flush()
    localDups = findDuplicateLocalImage()
    
    sys.stdout.write('\rGenerating Reports: '.ljust(80))
    sys.stdout.flush()
    sys.stdout.write('\rGenerating Reports: Finding Duplicate SmugMug Images'.ljust(80))
    sys.stdout.flush()
    smugDups = findDuplicateSmugMugImage()
    
    
    sys.stdout.write('\rGenerating Reports: '.ljust(80))
    sys.stdout.flush()
    sys.stdout.write('\rGenerating Reports: Finding Images Missing from Last Scan'.ljust(80))
    sys.stdout.flush()
    deletes = findImagesinDbNotScannedThisRun()
    
    sys.stdout.write('\rGenerating Reports: '.ljust(80))
    sys.stdout.flush()
    sys.stdout.write('\rGenerating Reports: Combining Reports'.ljust(80))
    sys.stdout.flush()
    report = [mismatchedCategories, "\n\n", 
              mismatchedFilenames, "\n\n", 
              missingLocal, "\n\n", 
              missingSmug, "\n\n",
              missingImages,"\n\n",
              localDups,"\n\n",
              smugDups, "\n\n",
              deletes]
    filename =core.DATA_DIR+'/report.txt'
    sys.stdout.write('\rGenerating Reports: '.ljust(80))
    sys.stdout.flush()
    sys.stdout.write('\rGenerating Reports: Writing Report to {0}'.format(filename).ljust(80))
    sys.stdout.flush()
    file = open(filename, 'w')
    file.write(''.join(report))
    file.close()
    sys.stdout.write('\rGenerating Reports: '.ljust(80))
    sys.stdout.flush()
    sys.stdout.write('\rGenerating Reports: Complete (Report written to {0})\n'.format(filename))
