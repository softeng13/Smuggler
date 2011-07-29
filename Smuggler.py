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
import getopt
import logging.handlers
import sys

import core
from core import fileScan
from core import smugScan
from core import dbSchema
from core import fileUtil
from core import pictureReport

myLogger = logging.getLogger('Smuggler')


def logSetup(debug, console):
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
    if(debug):
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.WARNING) 
    
    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    
    #File Handler Setup to create rotate log files at 10 megabytes and only keep 5
    handler = logging.handlers.RotatingFileHandler(core.LOG_DIR+'/Smuggler.log', maxBytes=10*1024*1024, backupCount=5)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    if console:
        #set up the logging to the console, use the same formatter as above
        #maybe we should use a different one, will see how it goes
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)

def usage():
    help = (
            "usage: python Smuggler.py [--help] [--forcescan] [--upload] [--download]        \n"
            "       [--logdebug] [--consolelog] [--config=<file path>]                       \n\n"
            "If Smuggler is ran with out any options, all it will do is scan for changes of  \n"
            "local and SmugMug files and generate a report detailing what it found. The      \n"
            "report is helpful to determine any sync issues you may have if you perform the  \n"
            "upload and\or download functions. It is important to look over them to see if   \n"
            "there are any things you need to fix. If there is, after fixing them rerun this \n"
            "with the [--forcescan] option to rescan everything to double check it before you\n"
            "go any farther.                                                                 \n\n"
            "Options and arguments explained:                                                \n"
            "--help       : print this help message and exit                                 \n"
            "--forcescan  : delete existing database and start completly fresh. the old      \n"
            "               database will be renamed smuggler.db.old in the data dir. If     \n"
            "               there is already a file with that name, that file will be deleted\n"
            "--upload     : upload all images that are not currently on SmugMug              \n"
            "               NOTE: NOT IMPLEMENTED YET SO WILL JUST EXIT                      \n"
            "--download   : download all images that are on SmugMug but not found locally    \n"
            "               NOTE: NOT IMPLEMENTED YET SO WILL JUST EXIT                      \n"
            "--logdebug   : will set the logging level to debug. This will slow things down  \n"
            "               so it should not always be used, but is helpful if you are having\n"
            "               a problem                                                        \n"
            "--consolelog : will print logs to the console while running.                    \n"
            "--config     : passes in the file path the configuration file you want to use.  \n"
            "               Helpful if you want to run two instances of Smuggler, with       \n"
            "               different path roots for the images.                             \n\n"
            "If you run into a issue or bug or question check out the issues on github at    \n"
            "https://github.com/jkschoen/Smuggler/. One day maybe there will be something on \n"
            "the wiki for the project, but until then just look at open/closed issues and if \n"
            "you don't see your problem open up a new one.                                   \n"
           )
    print help   

def main():
    #Default values for parameters
    deleteDb = False
    upload = False
    download = False
    logdebug = False
    consolelog = False
    #process options
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hfudlc", ['help','forcescan', 'upload', 'download', 'logdebug', 'consolelog', 'config='])
    except getopt.GetoptError, err:
        out = [str(err), "\n\n"]
        print ''.join(out)
        usage()
        sys.exit(2)
        
    for option, value in opts:
        if option in ("-h", "--help"):
            usage()
            #sys.exit()
        elif option in ("-f", "--forceScan"):
            deleteDb = True
        elif option in ("-u", "--upload"):
            upload = True
            assert False, "Come on man, I just started writing this thing. Be patient."
        elif option in ("-d", "--download"):
            download = True
            assert False, "Come on man, I have not even implemented upload yet. Be patient."
        elif option in ("-l", "--logdebug"):
            logdebug = True
        elif option in ("-c", "--consolelog"):
            consolelog = True
        elif option == "--config":
            core.CONFIG_FILE = value   
        else:
            assert False, "Unhandled Opton. Go create an issue on github and tell me a joke while you are there."
    
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
    logSetup(logdebug, consolelog)
    """
    
    
    myLogger.info("Welcome to Smuggler!!!")
    myLogger.debug("Configuration File Processed and Logging Initialized.")
    
    dbSchema.upgradeSchema()
    myLogger.info("Database started.")
    
    core.checkOAuthConnection()
    
    myLogger.info("Starting to scan directories to locate any new pictures")
    fileScan.findPictures()
    myLogger.debug("Finished scanning all files in the directory")
    
    myLogger.info("Starting to get all the picture info from SmugMug")
    smugScan.getAllPictureInfo()
    myLogger.debug("Finished getting all the picture info from SmugMug")
    
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
    
    """
    
if __name__ == '__main__':
    main()
    