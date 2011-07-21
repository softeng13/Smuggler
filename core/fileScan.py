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
import os
import hashlib
import core
import db

myLogger = logging.getLogger('fileScan')


def md5(file):
    f = open(file,'rb')
    m = hashlib.md5()
    while True:
        data = f.read(10240)
        if len(data) == 0:
            break
        m.update(data)
    return m.hexdigest()

def findPictures():
    count = 0
    directories = [core.PICTURE_ROOT]
    while len(directories)>0:
        directory = directories.pop()
        myLogger.info("Checking directory: "+directory)
        for name in os.listdir(directory):
            fullpath = os.path.join(directory,name)
            basename, extension = os.path.splitext(name)
            if os.path.isfile(fullpath) and extension in core.EXTENSIONS:
                count = count +1
                myLogger.debug(format(fullpath.lstrip(core.PICTURE_ROOT)))
                processFoundFile(LocalFile(fullpath, md5(fullpath)))
            elif os.path.isdir(fullpath):
                directories.append(fullpath)
    myLogger.info('Total picture files found := {0}'.format(count))

def processFoundFile(localFile):
    #check if file is in the database by file name, path and md5. Can't just do 
    #md5 since it is possible it is intended for the same picture to be in 
    #multiple galleries
    if not db.pictureExistsInDb(localFile.pathRoot, localFile.pictureFile, localFile.md5):
        myLogger.info('Picture not found in db. Going to add it for later: {0}, {1}, {2}'.format(localFile.pathRoot, localFile.pictureFile, localFile.md5))
        db.insertPictureInDb(localFile.pathRoot, localFile.pictureFile, localFile.md5, localFile.gallery, localFile.subcat, localFile.cat)

class LocalFile():
    def __init__(self, pictureFile, md5):
        self.md5 = md5
        self.pathRoot = core.PICTURE_ROOT
        self.pictureFile = format(pictureFile.lstrip(core.PICTURE_ROOT))
        self.fileName = os.path.basename(self.pictureFile)
        self.gallery = os.path.basename(os.path.dirname(self.pictureFile))
        self.subcat = os.path.basename(os.path.dirname(os.path.dirname(self.pictureFile)))
        self.cat = os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(self.pictureFile))))
        if self.cat == None:
            self.cat = self.subcat
            self.subcat = None
        