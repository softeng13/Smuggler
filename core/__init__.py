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

import db
import dbSchema
import fileScan
import smugScan
import fileUtil
import pictureReport
import webbrowser

from db import *
from dbSchema import *
from lib.configobj import ConfigObj
from lib.smugpy import SmugMug


myLogger = logging.getLogger('core')

FIRST_RUN = False

CONFIG_FILE = "config.ini"
#the file extensions of pictures we can upload
EXTENSIONS = [".jpg", ".jpeg", ".jpe",".jfif",".jif", ".png", ".gif"]
#GENERAL
LOG_DIR = "log"
DATA_DIR = "data"
#USER
PICTURE_ROOT = ""

API_KEY = "RXgvpRaLqaQdEgoKQhaQZZiqiItVByuS"
OAUTH_SECRET = "b308a33ffc2f417b4b1ba50e3933e0fa"

smugmug = SmugMug(api_key=API_KEY, oauth_secret=OAUTH_SECRET, app_name="Smuggler")
#the instance of the DBConnection class
conn = DBConnection()

def loadConfig():
    """
    This will read in the configuration file and set the values to the 
    appropriate variables in the application for later use.
    """
    configFile = ConfigObj(core.CONFIG_FILE)
    #load general settings
    general = configFile['GENERAL']
    global LOG_DIR
    LOG_DIR = general['log_dir']
    global DATA_DIR
    DATA_DIR = general['data_dir']
    #load user settings
    user_settings = configFile['USER_SETTINGS']
    global PICTURE_ROOT
    PICTURE_ROOT = user_settings['picture_root']

def saveConfig():
    """
    This will write out the configuration file to the system. It will be called
    when the application is done with everything else to ensure any settings
    that are updated while running are preserved for the next run. Also the
    user could go and modify this file between runs if they so desired.
    """
    configFile = ConfigObj()
    configFile.filename = CONFIG_FILE
    #General stuff
    configFile['GENERAL'] = {}
    configFile['GENERAL']['log_dir'] = LOG_DIR
    configFile['GENERAL']['data_dir'] = DATA_DIR
    #User Specific
    configFile['USER_SETTINGS'] = {}
    configFile['USER_SETTINGS']['picture_root'] = PICTURE_ROOT
    configFile.write()

def checkOAuthConnection():
    oauthDetails = db.getOAuthConnectionDetails()
    if (oauthDetails is None):
        myLogger.info("OAuth details where not found. Prompting user")
        smugmug.auth_getRequestToken()
        url = smugmug.authorize("Full", "Modify")
        webbrowser.open(url)
        raw_input("Your default web browser should have opened to authorize Smuggler with SmugMug.\nYou should only need to do this once, and then the needed information will be\nstored for future use. If your browser did not open you can manually\nauthorize Smuggler by going to:\n %s\n\nPlease Press Enter when complete.\n" % (url))   
        smugmug.auth_getAccessToken()
        myLogger.debug("OAUTH_TOKEN : "+smugmug.oauth_token)
        myLogger.debug("OAUTH_TOKEN_SECRET : "+smugmug.oauth_token_secret)
        db.setOAuthConnectionDetails(smugmug.oauth_token, smugmug.oauth_token_secret)
        print "Smuggler has been authorized.\n"
    else:
        myLogger.info("Setting found OAuth Details")
        myLogger.debug("OAUTH_TOKEN from db : "+oauthDetails[0])
        myLogger.debug("OAUTH_TOKEN_SECRET from db: "+oauthDetails[1])
        smugmug.set_oauth_token(oauthDetails[0], oauthDetails[1])
        
