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
import db
import fileScan


myLogger = logging.getLogger('fileUtil')

def fileRenamer():
    files = db.findSameFilesWithDifferentName()
    runScan = False
    for file in files:
        runScan = True
        original = None
        new = None
        original = file[2]+"/"+file[3]
        new = original.replace(file[0], file[1])
        myLogger.info("Renaming '%s' to '%s' rowid '%s'", original, new, file[4])
        try:
            os.rename(original, new)
        except OSError:
            #I know I feel wrong about this too, but after some thought,
            #I realized that if the file is not found who cares, they
            #For some reason it just kept running through the same 
            #row twice. Couldn't think of anything else. If you have
            #an idea let me know.
            myLogger.error("File '%s' was not there when we went to rename it", original)
            pass
        db.deleteLocalImage(file[4])
    #Kick off another file scan to pick them back up
    if runScan:
        myLogger.info("Finished renaming files, starting another file scan to pick them back up.")
        fileScan.findPictures()
        
