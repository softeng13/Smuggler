import os
import errno
import logging.handlers
import sys

import core
from core import db
from core import smugglerWeb

myLogger = logging.getLogger('Smuggler')

def logSetup(debug, console, configobj):
    """
    Setting up the logging the way we want it. Basically we will log to both
    the console and to a log file. The log files will max out at 10 megabytes
    and be rotated out. Keeping 5 at a time. This should be reasonable in the
    case we need to do debugging in the future.
    """
    
    #make sure there is a log directory to write to
    try:
        os.makedirs(configobj.log_dir)
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
    
    formatter = logging.Formatter('%(processName)s %(threadName)s %(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    
    #File Handler Setup to create rotate log files at 10 megabytes and only keep 5
    handler = logging.handlers.RotatingFileHandler(configobj.log_dir+'/Smuggler.log', maxBytes=10*1024*1024, backupCount=5)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    if console:
        #set up the logging to the console, use the same formatter as above
        #maybe we should use a different one, will see how it goes
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)

def main():
    #load the config file if it is there
    print sys.version
    
    try:
        configFile = open("config.ini")
        configFile.close()
        #initialize db, only want to do this if the config is there already
        myLogger.info("Starting Smuggler, watch your back.")
        myLogger.debug("Configuration File Processed and Logging Initialized.")
        myLogger.info("Picture Root => "+core.configobj.picture_root)
        myLogger.info("Log Dir => "+core.configobj.log_dir)
        myLogger.info("Data Dir => "+core.configobj.data_dir)
        
        db.initDb(core.configobj)
        myLogger.info("Database started.")
    except IOError:
        pass #this just means a config file was not found, will happen on first run.
   
    #initialize logging for the application
    logSetup(True, True, core.configobj)
    #initialize logging for the application
    myLogger.info("Starting Smuggler, watch your back.")
    #start web server
    smugglerWeb.run()


if __name__ == '__main__':
    main()
