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
import os
import errno
import logging.handlers

import core
from core import fileScan
from core import smugScan
from core import dbSchema
from core import fileUtil
from core import pictureReport

myLogger = logging.getLogger('Smuggler')


def logSetup():
    """
    Setting up the logging the way we want it. Basically we will log to both
    the console and to a log file. The log files will max out at 10 megabytes
    and be rotated out. Keeping 5 at a time. This should be reasonable in the
    case we need to do debugging in the future.
    """
    
    #make sure there is a log directory to write to
    try:
        os.makedirs(core.LOG_DIR)
    except OSError, e:
        if e.errno != errno.EEXIST:
            raise
    
    #for now this is just going to be hard coded to log to a certain location
    #will need to later add a config file for this, or maybe can just create a 
    #folder where it is being ran from. Doesn't seem right
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    
    #File Handler Setup to create rotate log files at 10 megabytes and only keep 5
    handler = logging.handlers.RotatingFileHandler(core.LOG_DIR+'/Smuggler.log', maxBytes=10*1024*1024, backupCount=5)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    #set up the logging to the console, use the same formatter as above
    #maybe we should use a different one, will see how it goes
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

   

def main():
    #load up configuration file
    try:
        configFile = open(core.CONFIG_FILE)
        configFile.close()
    except IOError:
        pictureRoot = raw_input("Please enter the path to the folder with your pictures: ")
        core.PICTURE_ROOT = pictureRoot
        core.saveConfig()
    core.loadConfig()
    #initialize logging
    logSetup()
    myLogger.info("Welcome to Smuggler!!!")
    myLogger.debug("Configuration File Processed and Logging Initialized.")
    
    dbSchema.upgradeSchema()
    myLogger.info("Database started.")
    """
    core.checkOAuthConnection()
    
    myLogger.info("Starting to scan directories to locate any new pictures")
    fileScan.findPictures()
    myLogger.debug("Finished scanning all files in the directory")
    
    myLogger.info("Starting to get all the picture info from SmugMug")
    smugScan.getAllPictureInfo()
    myLogger.debug("Finished getting all the picture info from SmugMug")
    """
    #Check for files that are the some local and on smugmug with different names
    
    report = [pictureReport.findMismatchedCategories(), "\n\n", 
              pictureReport.findMisatchedFilenames(), "\n\n", 
              pictureReport.findMissingLocalAlbums(), "\n\n", 
              pictureReport.findMissingSmugMugAlbums(), "\n\n",
              pictureReport.findMissingPictures()]
    print ''.join(report)
   
#    fileUtil.fileRenamer()

    #last thing to do before closing up shop is save configuration information
    myLogger.debug("Saving configuration file.")
    core.saveConfig()
    

    
if __name__ == '__main__':
    main()
    