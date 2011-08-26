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
import hashlib
import os

import db

myLogger = logging.getLogger('fileUtil')

def md5(file):
    f = open(file,'rb')
    m = hashlib.md5()
    while True:
        data = f.read(10240)
        if len(data) == 0:
            break
        m.update(data)
    return m.hexdigest()

def mkdir(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST:
            pass
        else: raise

def buildfilePath(root, category, subcategory, album):
    path = root
    if category <> None:
        path = path + '/' + category
    if subcategory <> None:
        path = path + '/' + subcategory
    path = path + '/' + album + '/'
    return path 

def fileRenamer(conn):
    """
    I wrote this but am not using it yet, as I am not sure how I feel about 
    doing this for them. Especially if I screw it somehow. So this may go away.
    """
    files = db.findSameFilesWithDifferentName(conn)
    for file in files:
        original = None
        new = None
        original = file[2]+"/"+file[3]
        new = original.replace(file[0], file[1])
        myLogger.info("Renaming '%s' to '%s' rowid '%s'", original, new, file[4])
        try:
            myLogger.debug("calling os.rename(%s, %s)",original, new)
            os.rename(original, new)
        except OSError:
            #I know I feel wrong about this too, but after some thought,
            #I realized that if the file is not found who cares, they
            #For some reason it just kept running through the same 
            #row twice. Couldn't think of anything else. If you have
            #an idea let me know.
            myLogger.error("File '%s' was not there when we went to rename it", original)
            pass
        db.deleteLocalImage(conn, file[4])
        
