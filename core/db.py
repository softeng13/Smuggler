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

import errno
import logging
import os
import sqlite3
import core

myLogger = logging.getLogger('db')
        
class DBConnection():
    def __init__(self):
        self.connection = None
        
    def delayedInit(self):
        try:
            myLogger.debug("making sure that the data dir exists")
            os.makedirs(core.DATA_DIR)
            myLogger.debug("data dir must not have existed since there was no error thrown, but it does now")
        except OSError, e:
            if e.errno != errno.EEXIST:
                raise
        dbLocation = core.DATA_DIR+'/smuggler.db'
        myLogger.debug("db location is :"+dbLocation)
        if not os.path.isfile(dbLocation):
            myLogger.debug("database did not exist, so creating empty version table")
            conn = sqlite3.connect(dbLocation)
            #get the cursor
            c = conn.cursor()
            #Create version table
            c.execute('''create table version (number integer)''')
            conn.commit()
            c.close()
            conn.close()
        self.connection = sqlite3.connect(dbLocation)
    
    def execute(self, query, params = None):
        if self.connection == None:
            self.delayedInit()
        result = None
        if query == None:
            myLogger.warning("Execute was called without a query being passed in. Weird")
            return
        cursor = self.connection.cursor()
        if params == None:
            myLogger.debug("query : '%s'",query)
            result = cursor.execute(query)
        else:
            myLogger.debug("query : '%s' with params '%s'", query, params)
            result = cursor.execute(query, params)
        self.connection.commit()
        return result.fetchall()


def executeSql(query, params = None):
    return core.conn.execute(query, params)    

def getDBVersion():
    result = core.conn.execute("SELECT number FROM version")
    if result is not None and len(result) > 0:
        return int(result[0][0])
    else:
        return 0

def getOAuthConnectionDetails():
    sql = "SELECT token, secret FROM oauth"
    result = core.conn.execute(sql)
    if result is not None and len(result) > 0:
        return result[0]
    else:
        return None
def setOAuthConnectionDetails(token, secret):
    sql = "INSERT INTO oauth(token, secret) VALUES(?,?)"
    params = [token, secret]
    core.conn.execute(sql, params)

def addLocalImage(sub_category, category, album, last_updated, md5_sum, path_root, file_name, file_path, scan_time):    
    
    params = [sub_category, category, album, last_updated, md5_sum, path_root, file_name, file_path, scan_time]
    sql = "INSERT INTO local_image(sub_category, category, album, last_updated, md5_sum, path_root, filename, modified, file_path, last_scanned) VALUES (:1,:2,:3,:4,:5,:6,:7,1, :8, :9)"
    try:
        core.conn.execute(sql, params)
    except sqlite3.IntegrityError:
        sql = ("UPDATE local_image "
               "SET sub_category = :1, "
               "    category = :2, "
               "    album = :3, "
               "    last_updated = :4, "
               "    md5_sum = :5, "
               "    path_root = :6, "
               "    filename = :7, "
               "    modified = ((SELECT md5_sum FROM local_image WHERE path_root = :6 AND sub_category = :1 and category = :2 and album = :3 and  filename = :7) = :5), "
               "    file_path = :8 ,"
               "    last_scanned = :9 "
               "WHERE  path_root = :6 "
               "    AND (:1 IS NULL OR sub_category = :1) "
               "    AND (:2 IS NULL OR category = :2) "
               "    AND album = :3 "
               "    AND filename = :7")
        core.conn.execute(sql, params)
    
    
    
def addSmugAlbum(category, sub_category, title, last_updated, key, id):
    sql ="INSERT OR REPLACE INTO smug_album (category, sub_category, title, last_updated, key, id) VALUES (?,?,?,?,?,?)"
    params = [category, sub_category, title, last_updated, key, id]
    core.conn.execute(sql, params)
    
def addSmugImage(album_id, last_updated, md5_sum, key, id, filename):
    sql = "INSERT OR REPLACE INTO smug_image (album_id, last_updated, md5_sum, key, id, filename) VALUES (?,?,?,?,?,?)"
    params = [album_id, last_updated, md5_sum, key, id, filename]
    core.conn.execute(sql, params)
    
def findSameFilesWithDifferentName():
    sql = (
           "SELECT DISTINCT li.filename, si.filename, li.path_root, li.file_path, li.rowid  " 
           "FROM local_image li "
           "  INNER JOIN smug_image si on li.md5_sum = si.md5_sum " 
           "  INNER JOIN smug_album sa on si.album_id = sa.id "
           "WHERE li.filename <> si.filename"
           "  AND li.album = sa.title"
          )
    result = core.conn.execute(sql)
    return result

def deleteLocalImage(rowid):
    sql = "delete from local_image where rowid = ?"
    params = [rowid]
    core.conn.execute(sql, params)  
    
#
# Report Queries
#  
def findMismatchedCategories():
    """
    list of albums by name that exist both locally and on smug mug that have 
    different category and/or sub-category. 
    Columns: album name, local category, local sub-category, smug category, 
             smug sub-category
    """
    sql = (
           "SELECT li.album, li.category as local_category, li.sub_category as local_sub_category, sa.category as smug_category, sa.sub_category as smug_sub_category "
           "FROM local_image li "
           "  INNER JOIN smug_album sa ON sa.title = li.album "
           "WHERE li.category <> sa.category "
           "   OR li.sub_category <> sa.sub_category"
          )
    result = core.conn.execute(sql)
    return result

def findMisatchedFilenames():
    """
    list of local images that have the same md5sum as an image on SmugMug, but they 
    have different filenames. Note this will only list the files if they are in the 
    same album 
    Columns: local category, local sub-category, local filename, 
             smug category, smug sub-category, smug filename
    """
    sql = (
           "SELECT li.filename as local_name, si.filename as smug_name, li.category, li.sub_category, li.album " 
           "FROM local_image li "
           "  INNER JOIN smug_image si on li.md5_sum = si.md5_sum " 
           "  INNER JOIN smug_album sa on si.album_id = sa.id "
           "WHERE li.filename <> si.filename"
           "  AND li.album = sa.title"
          )
    result = core.conn.execute(sql)
    return result

def findMissingLocalAlbums():
    """
    list of albums that are on smug mug that are not found locally. This would
    exclude albums that are local but under different category and sub-category
    Columns: category, sub-category, smug album, number of photos
    """
    sql = (
           "SELECT sa.category as category, sa.sub_category as sub_category, sa.title as album, count(si.id) as image_count "
            "FROM smug_album sa "
            "  INNER JOIN smug_image si ON sa.id = si.album_id "
            "WHERE sa.title NOT IN (SELECT distinct album FROM local_image) "
            "GROUP BY sa.category, sa.sub_category, sa.title"
           )
    result = core.conn.execute(sql)
    return result

def findMissingSmugMugAlbums():
    """
    list of albums that are found local but not found on smug mug. This would
    exclude albums that are local but under different category and sub-category
    Columns: category, sub-category, local album, number of photos    
    """
    sql = (
           "SELECT li.category as category, li.sub_category as sub_category, li.album as album, count(*) as image_count "
           "FROM local_image li "
           "WHERE li.album NOT IN (SELECT distinct title FROM smug_album) "
           "GROUP BY li.category, li.sub_category, li.album"
          )
    result = core.conn.execute(sql)
    return result

 
def findMissingPictures():
    """
    list by album show the number of images that are not in both. This will
    only include albums that are in both
    Columns: album, different local photo count(need upload), different smug photo count(need download) 
    """
    sql = (
           "SELECT li.album as album, "
           "    ( "
           "    SELECT COUNT(*) "
           "    FROM local_image "
           "    WHERE album = li.album "
           "      AND li.md5_sum NOT IN (SELECT md5_sum FROM smug_image) "
           "    ) as need_upload, "
           "    ( "
           "    SELECT COUNT(*) "
           "    FROM smug_album sa "
           "        INNER JOIN smug_image si ON si.album_id = sa.id " 
           "    WHERE sa.title = li.album "
           "      AND si.md5_sum NOT IN (SELECT md5_sum FROM local_image) "
           "    ) as need_download "
           "FROM local_image li "
           "    INNER JOIN smug_album on title = li.album "
           "GROUP BY li.album "
           "ORDER BY need_upload desc, need_download desc"
          ) 
    result = core.conn.execute(sql)
    return result

def findDuplicateLocalImage():
    sql = (
          "SELECT li.filename, li2.filename, li.album, li.sub_category, li.category "
          "FROM local_image li "
          "  INNER JOIN local_image li2 on li.md5_sum = li2.md5_sum AND li.rowid < li2.rowid "
          "WHERE li.album = li2.album"
         )     
    result = core.conn.execute(sql)
    return result

def findDuplicateSmugMugImage():
    sql = (
           "SELECT si.filename, si2.filename, sa.title, sa.sub_category, sa.category "
           "FROM smug_image si "
           "   INNER JOIN smug_album sa on si.album_id = sa.id "
           "   INNER JOIN smug_image si2 on si.md5_sum = si2.md5_sum AND si.rowid < si2.rowid "
           "   INNER JOIN smug_album sa2 on si2.album_id = sa2.id "
           "WHERE sa.id = sa2.id"
          )
    result = core.conn.execute(sql)
    return result

        
def findImagesinDbNotScannedThisRun():
    sql = (
           " SELECT li.last_scanned, li.filename, li.album, li.sub_category, li.category" 
           " FROM local_image li"
           " WHERE li.last_scanned < (select max(last_scanned) from local_image)"
          )
    result = core.conn.execute(sql)
    return result
    