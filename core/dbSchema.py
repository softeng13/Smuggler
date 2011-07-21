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


myLogger = logging.getLogger('dbSchema')

class BaseSchema():
    """
    This is just the base class to place any common methods that all the 
    schema upgrades may or may not need. 
    """
    def incrementDBVerson(self):
        """
        Increments the version of the database by one.
        """
        version = db.getDBVersion()
        db.executeSql("UPDATE version SET number = ?", [version+1])
        
class InitialSchema(BaseSchema):
    """
    This is what the initial schema looks like, I am sure there will be many
    changes as things progress.
    """
    def test(self):
        """
        Checks to make sure the database version is at least 1
        """
        return db.getDBVersion() >= 1
    
    def upgrade(self):
        """
        If the database version is not at least one, it will upgrade it to the 
        version one database
        """
        if not self.test():
            db.executeSql("INSERT INTO version(number) VALUES (0)")
            db.executeSql("CREATE TABLE pictures (path_root TEXT, file_path TEXT, md5 TEXT, category TEXT, sub_category TEXT, gallery TEXT, uploaded_date TIMESTAMP)")
            self.incrementDBVerson()