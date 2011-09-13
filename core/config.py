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
from lib.configobj import ConfigObj


myLogger = logging.getLogger('config')

class Config():
    def __init__(self, config="config.ini"):
        self.update = False
        self.config = config
        self.log_dir = "log"
        self.data_dir = "data"
        self.picture_root = None
        self.start_time ="22:00"
        self.scan_interval = "24"
        self.loadConfig()
        if self.update:
            self.saveConfig()
        

    def loadConfig(self):
        """
        This will read in the configuration file and set the values to the 
        appropriate variables in the application for later use.
        """
        try:
            myLogger.debug("checking if config file exists")
            configFile = open(self.config)
            configFile.close()
            myLogger.debug("Apparently config file exists")
            configFile = ConfigObj(self.config)
            #load general settings
            general = configFile['GENERAL']
            self.log_dir = general['log_dir']
            self.data_dir = general['data_dir']
            #load user settings
            user_settings = configFile['USER_SETTINGS']
            self.picture_root = user_settings['picture_root']
            
            #first update to config file
            try:
            #load scheduling settings
                schedule = configFile['SCHEDULING']
                self.start_time = schedule['start_time']
                self.scan_interval = schedule['scan_interval']
            except KeyError:
                self.update = True
            myLogger.debug("finished loading config file")
        except IOError:
            myLogger.debug("Config file does not exist. Gonna role with defaults")
            self.update = True

    def saveConfig(self):
        """
        This will write out the configuration file to the system. It will be called
        when the application is done with everything else to ensure any settings
        that are updated while running are preserved for the next run. Also the
        user could go and modify this file between runs if they so desired.
        """
        configFile = ConfigObj()
        configFile.filename = self.config
        #General stuff
        configFile['GENERAL'] = {}
        configFile['GENERAL']['log_dir'] = self.log_dir
        configFile['GENERAL']['data_dir'] = self.data_dir
        #User Specific
        configFile['USER_SETTINGS'] = {}
        configFile['USER_SETTINGS']['picture_root'] = self.picture_root
        configFile['SCHEDULING'] = {}
        configFile['SCHEDULING']['start_time'] = self.start_time
        configFile['SCHEDULING']['scan_interval'] = self.scan_interval
        configFile.write()