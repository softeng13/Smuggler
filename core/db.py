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
        
        if params == None:
            myLogger.debug("query : '"+query+"'")
            result = self.connection.execute(query)
        else:
            myLogger.debug("query : '"+query+"' with params '",params,"'")
            result = self.connection.execute(query, params)
        self.connection.commit()
        return result


def executeSql(query, params = None):
    return core.conn.execute(query, params)    

def getDBVersion():
    result = core.conn.execute("SELECT number FROM version")
    version = result.fetchone()
    if version is not None:
        return int(version[0])
    else:
        return 0

def pictureExistsInDb(pathRoot, pictureFile, md5):
    sql = "SELECT COUNT(*) FROM pictures WHERE path_root = ? AND file_path = ? and md5 = ?"
    params = [pathRoot, pictureFile, md5]
    result = core.conn.execute(sql, params)
    count = result.fetchone()
    if count is not None:
        return int(count[0]) > 0
    else:
        return False


def insertPictureInDb(pathRoot, pictureFile, md5, gallery, subcat, cat):    
    sql = "INSERT INTO pictures(path_root, file_path, md5, gallery, sub_category, category) VALUES(?,?,?,?,?,?)"
    params = [pathRoot, pictureFile, md5, gallery, subcat, cat]
    core.conn.execute(sql, params)
