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

import datetime
import logging

import db

myLogger = logging.getLogger('dbSchema')

def upgradeSchema(conn):
    schema = UserSubCategorySchema()
    schema.upgrade(conn)

class BaseSchema():
    """
    This is just the base class to place any common methods that all the 
    schema upgrades may or may not need. 
    """
    def incrementDBVerson(self, conn):
        """
        Increments the version of the database by one.
        """
        version = db.getDBVersion(conn)
        db.execute(conn, "UPDATE version SET number = ?", [version+1])
        
class InitialSchema(BaseSchema):
    """
    This is what the initial schema looks like, I am sure there will be many
    changes as things progress.
    """
    def upgrade(self, conn):
        """
        If the database version is not at least one, it will upgrade it to the 
        version one database
        """
        self._upgrade(db.getDBVersion(conn), conn)
        
    def _upgrade(self, version, conn):
        if version < 1:
            db.execute(conn, "INSERT INTO version(number) VALUES (0)")
            db.execute(conn, "CREATE TABLE local_image (sub_category TEXT, category TEXT, album TEXT, last_updated TIMESTAMP, md5_sum TEXT, path_root TEXT, file_path TEXT, filename TEXT, modified BOOLEAN, PRIMARY KEY (path_root, file_path))")
            self.incrementDBVerson(conn)
        

class OAuthSchema(InitialSchema):
    """
    This will add the necessary tables to store the needed information
    to log in using OAuth
    """
    def upgrade(self, conn):
        self._upgrade(db.getDBVersion(conn), conn)
    
    def _upgrade(self, version, conn):
        """
        If the database version is not at least two, it will upgrade it to the 
        version one database
        """
        InitialSchema._upgrade(self,version, conn)
        if version < 2:
            db.execute(conn, "CREATE TABLE oauth (token TEXT, secret TEXT)")
            self.incrementDBVerson(conn)
            
class SmugMugAlbumSchema(OAuthSchema):
    """
    """
    def upgrade(self, conn):
        self._upgrade(db.getDBVersion(conn), conn)
    
    def _upgrade(self, version, conn):
        """
        """
        OAuthSchema._upgrade(self,version, conn)
        if version < 3:
            db.execute(conn, "CREATE TABLE smug_album (category TEXT, sub_category TEXT, title TEXT, last_updated TIMESTAMP, key TEXT, id TEXT, PRIMARY KEY (id))")
            self.incrementDBVerson(conn)

class SmugMugImageSchema(SmugMugAlbumSchema):
    """
    """
    def upgrade(self, conn):
        self._upgrade(db.getDBVersion(conn), conn)
    
    def _upgrade(self, version, conn):
        """
        """
        SmugMugAlbumSchema._upgrade(self,version, conn)
        if version < 4:
            db.execute(conn, "CREATE TABLE smug_image (album_id TEXT, last_updated TIMESTAMP, md5_sum TEXT, key TEXT, id TEXT, filename TEXT, PRIMARY KEY (id), FOREIGN KEY (album_id) REFERENCES smug_album(id))")
            self.incrementDBVerson(conn)


class LocalImageSchema(SmugMugImageSchema):
    """
    """ 
    def upgrade(self, conn):
        self._upgrade(db.getDBVersion(conn), conn)
    
    def _upgrade(self, version, conn):
        """
        """
        SmugMugImageSchema._upgrade(self,version, conn)
        if version < 5:
            db.execute(conn, "ALTER TABLE local_image ADD last_scanned TIMESTAMP")
            params = [datetime.datetime(1960, 1,1,1,1,1,1)]
            db.execute(conn, "UPDATE local_image SET last_scanned = ?", params)
            self.incrementDBVerson(conn)

class CategorySchema(LocalImageSchema):
    """
    """ 
    def upgrade(self, conn):
        self._upgrade(db.getDBVersion(conn), conn)
    
    def _upgrade(self, version, conn):
        """
        """
        LocalImageSchema._upgrade(self,version, conn)
        if version < 6:
            db.execute(conn, "ALTER TABLE smug_album ADD category_id TEXT")
            db.execute(conn, "ALTER TABLE smug_album ADD sub_category_id TEXT")
            self.incrementDBVerson(conn)
            

class SyncLogSchema(CategorySchema):
    """
    """ 
    def upgrade(self, conn):
        self._upgrade(db.getDBVersion(conn), conn)
    
    def _upgrade(self, version, conn):
        """
        """
        CategorySchema._upgrade(self,version, conn)
        if version < 7:
            db.execute(conn, "CREATE TABLE category_log (category_id, category TEXT, scan TIMESTAMP)")
            db.execute(conn, "CREATE TABLE sub_category_log (sub_id, sub_category TEXT, category TEXT, scan TIMESTAMP)")
            db.execute(conn, "CREATE TABLE album_log (album_id, name TEXT, category TEXT, sub_category TEXT, scan TIMESTAMP)")
            db.execute(conn, "CREATE TABLE image_log (image_id, filename TEXT, album TEXT, category TEXT, sub_category TEXT, scan TIMESTAMP)")
            self.incrementDBVerson(conn)

class UserCategorySchema(SyncLogSchema):
    """
    """ 
    def upgrade(self, conn):
        self._upgrade(db.getDBVersion(conn), conn)
    
    def _upgrade(self, version, conn):
        """
        """
        SyncLogSchema._upgrade(self,version, conn)
        if version < 8:
            db.execute(conn, "CREATE TABLE user_category (type TEXT, id TEXT, nicename TEXT, name TEXT, PRIMARY KEY (id))")
            db.execute(conn, "CREATE TABLE user_subcategory (id TEXT, nicename TEXT, name TEXT, PRIMARY KEY (id))")
            self.incrementDBVerson(conn)
            
class UserSubCategorySchema(UserCategorySchema):
    """
    """ 
    def upgrade(self, conn):
        self._upgrade(db.getDBVersion(conn), conn)
    
    def _upgrade(self, version, conn):
        """
        """
        UserCategorySchema._upgrade(self,version, conn)
        if version < 9:
            db.execute(conn, "ALTER TABLE user_subcategory ADD category_id TEXT")
            self.incrementDBVerson(conn)