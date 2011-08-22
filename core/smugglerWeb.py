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

import json
import logging
import multiprocessing
import os
import web
from web import form

import core
import db
import fileScan
from lib import smugpy
import messaging
import pictureReport
import smugScan


myLogger = logging.getLogger('smugglerWeb')

smugmug = smugpy.SmugMug(api_key=core.API_KEY, oauth_secret=core.OAUTH_SECRET, app_name="Smuggler")

working_dir = os.getcwd()
default_log = ''.join([working_dir, '/log']) 
default_data = ''.join([working_dir, '/data']) 


urls = (
        '/json/notify','notify',
        '/json/fullscan', 'fullscan',
        '/json/localscan', 'localscan',
        '/json/smugmugscan', 'smugmugscan',
        '/json/rootdir', 'rootdir',
        '/json/logdir', 'logdir',
        '/json/datadir', 'datadir',
        
        '/examples', 'examples',
        '/setup', 'setup',
        '/', 'index',
        '/config', 'config',
        
        '/reports', 'reports',
        '/reports/category', 'reports_category',
        '/reports/filename', 'reports_filename',
        '/reports/localAlbum', 'reports_localAlbum',
        '/reports/smugmugAlbum', 'reports_smugmugAlbum',
        '/reports/missingImage', 'reports_missingImage',
        '/reports/duplicateLocalImage', 'reports_duplicateLocalImage',
        '/reports/duplicateSmugmugImage', 'reports_duplicateSmugmugImage',
        
        '/table/categoryTable', 'categoryTable',
        '/table/filenameTable', 'filenameTable',
        '/table/localAlbumTable', 'localAlbumTable',
        '/table/smugmugAlbumTable', 'smugmugAlbumTable',
        '/table/missingImageTable', 'missingImageTable',
        '/table/duplicateLocalImageTable', 'duplicateLocalImageTable',
        '/table/duplicateSmugmugImageTable', 'duplicateSmugmugImageTable'
        )
render = web.template.render('template/', base='layout')
render_plain = web.template.render('template/')

app = web.application(urls, globals())

def run():
    #web.httpserver.runsimple(app.wsgifunc(), ("0.0.0.0",8080))
    app.run()

###############################################################################
#                                                                             #
#    Below are all the forms used by various screens                          #
#                                                                             #
###############################################################################

setup_form = form.Form(
                web.form.Textbox('root_dir', form.notnull, form.Validator('The root image directory must already exist.', lambda path: os.path.isdir(path)), id='root_dir'),
                web.form.Textbox('log_dir', form.notnull, form.Validator('The log directory must already exist.', lambda path: os.path.isdir(path)), id='log_dir', value = default_log),
                web.form.Textbox('data_dir', form.notnull, form.Validator('The data directory must already exist.', lambda path: os.path.isdir(path)), id='data_dir', value = default_data),
                web.form.Button('Save', id='save', class_="formbutton")
                )

    
config_form = form.Form(
                web.form.Textbox('root_dir', form.notnull, form.Validator('The root image directory must already exist.', lambda path: os.path.isdir(path)), id='root_dir'),
                web.form.Textbox('log_dir', form.notnull, form.Validator('The log directory must already exist.', lambda path: os.path.isdir(path)), id='log_dir'),
                web.form.Textbox('data_dir', form.notnull, form.Validator('The data directory must already exist.', lambda path: os.path.isdir(path)), id='data_dir'),
                web.form.Button('Save', id='save', class_="formbutton")
                )


###############################################################################
#                                                                             #
#    Below are all the classes to handle html requests                        #
#                                                                             #
###############################################################################

class examples:
    """
    Examples of how current css styles i am using effect different things.
    """
    def GET(self):
        return render_plain.examples()   
    
class index:
    """
    The default screen and starting point for users.
    """
    def GET(self):
        try:
            #Don't particularly like put this test in here to check for 
            #first run, but couldn't find a better way yet
            configFile = open("config.ini")
            configFile.close()
        except IOError:
            return web.seeother('/setup')
        else:
            return render.index()
            
class setup:
    """
    This should only be used once when the application is initially installed.
    The user will be redirected to here to setup everything how they  want.
    """
    def GET(self):
        #/Users/jacobschoen/Desktop/pictures/SmugMug
        form = setup_form()
        return self._GET(form, False)
    
    def POST(self): 
        form = setup_form()
        if not form.validates(): 
            return self._GET(form, False)
        else:
            try:
                smugmug.auth_getAccessToken()
            except smugpy.SmugMugException:
                return self._GET(form, True)
            else:
                #self.first = False
                core.configobj.picture_root  = form.value['root_dir']
                core.configobj.log_dir = form.value['log_dir']
                core.configobj.data_dir = form.value['data_dir']
                core.configobj.saveConfig()
                myLogger.info("Config file Created.")
                db.initDb(core.configobj)
                myLogger.info("Database started.")
                db.setOAuthConnectionDetails(db.getConn(core.configobj), smugmug.oauth_token, smugmug.oauth_token_secret)
                return web.seeother('/')
    
    def _GET(self, form, authBad):
        if smugmug.oauth_token == None:
            smugmug.auth_getRequestToken()
        url = smugmug.authorize("Full", "Modify")
        return render_plain.setup(form, url, authBad)

class config:    
    def GET(self):
        form = config_form()
        return self._GET(form, False, core.configobj.picture_root)
    
    def POST(self): 
        form = config_form()
        if not form.validates(): 
            return self._GET(form, False, '')
        else:
            try:
                smugmug.auth_getAccessToken()
            except smugpy.SmugMugException:
                return self._GET(form, True, '')
            else:
                #self.first = False
                core.configobj.picture_root  = form.value['root_dir']
                core.configobj.log_dir = form.value['log_dir']
                core.configobj.data_dir = form.value['data_dir']
                core.configobj.saveConfig()
                myLogger.info("Config file Created.")
                db.initDb(core.configobj)
                myLogger.info("Database started.")
                db.setOAuthConnectionDetails(db.getConn(core.configobj), smugmug.oauth_token, smugmug.oauth_token_secret)
                return self._GET(form, True, '')
    
    def _GET(self, form, authBad, picRoot):
        if smugmug.oauth_token == None:
            smugmug.auth_getRequestToken()
        url = smugmug.authorize("Full", "Modify")
        return render.config(form, url, authBad, picRoot)

class reports:
    def GET(self):
        return render.reports()
    
class reports_category:
    def GET(self):
        return render.reports_category() 
    
class reports_filename:
    def GET(self):
        return render.reports_filename() 
    
class reports_localAlbum:
    def GET(self):
        return render.reports_localAlbum() 
    
class reports_smugmugAlbum:
    def GET(self):
        return render.reports_smugmugAlbum() 
    
class reports_missingImage:
    def GET(self):
        return render.reports_missingImage() 
    
class reports_duplicateLocalImage:
    def GET(self):
        return render.reports_duplicateLocalImage() 
    
class reports_duplicateSmugmugImage:
    def GET(self):
        return render.reports_duplicateSmugmugImage() 

###############################################################################
#                                                                             #
#    Below are all the classes to handle requests for report tables           #
#                                                                             #
###############################################################################
    
class categoryTable:
    def GET(self):
        return pictureReport.findMismatchedCategoriesHtml(db.getConn(core.configobj))    

class filenameTable:
    def GET(self):
        return pictureReport.findMisatchedFilenamesHtml(db.getConn(core.configobj))     

class localAlbumTable:
    def GET(self):
        return pictureReport.findMissingLocalAlbumsHtml(db.getConn(core.configobj))     

class smugmugAlbumTable:
    def GET(self):
        return pictureReport.findMissingSmugMugAlbumsHtml(db.getConn(core.configobj))     

class missingImageTable:
    def GET(self):
        return pictureReport.findMissingPicturesHtml(db.getConn(core.configobj))     

class duplicateLocalImageTable:
    def GET(self):
        return pictureReport.findDuplicateLocalImageHtml(db.getConn(core.configobj))    

class duplicateSmugmugImageTable:
    def GET(self):
        return pictureReport.findDuplicateSmugMugImageHtml(db.getConn(core.configobj))  
    
###############################################################################
#                                                                             #
#    Below are all the classes to handle json requests                        #
#                                                                             #
###############################################################################


class notify:
    """
    Used to pass notifications to users of the application. Is returned as json.
    """
    def GET(self):
        send = []
        
        for message in messaging.messages.getMessages():
            send.append({'type':message.type, 'message':message.message})
        web.header('Content-Type', 'application/json')
        
        return json.dumps(send)
    
class fullscan:
    """
    Used to initiate a scan of local and smugmug images. It returns json 
    acknowledging the request.
    """
    def GET(self):
        lock = multiprocessing.Lock()
        result = db.getOAuthConnectionDetails(db.getConn(core.configobj))
        token = result[0]
        secret = result[1]
        smugmug.set_oauth_token(token, secret)
        fileScan.localScan.start(core.configobj, lock)
        smugScan.smugScan.start(smugmug, core.configobj, lock)
        web.header('Content-Type', 'application/json')
        messages =["Passed along request to Scan everything."]
        return json.dumps(messages)

class localscan:
    """
    Used to initiate a scan of local images. It returns json 
    acknowledging the request.
    """
    def GET(self):
        lock = multiprocessing.Lock()
        fileScan.localScan.start(core.configobj, lock)
        web.header('Content-Type', 'application/json')
        messages =["Passed along request to Scan Locally."]
        return json.dumps(messages)
    
class smugmugscan:
    """
    Used to initiate a scan of smugmug images. It returns json 
    acknowledging the request.
    """
    def GET(self):
        lock = multiprocessing.Lock()
        result = db.getOAuthConnectionDetails(db.getConn(core.configobj))
        token = result[0]
        secret = result[1]
        smugmug.set_oauth_token(token, secret)
        smugScan.smugScan.start(smugmug, core.configobj, lock)
        web.header('Content-Type', 'application/json')
        messages =["Passed along request to Scan SmugMug."]
        return json.dumps(messages)

class rootdir:
    def GET(self):
        web.header('Content-Type', 'application/json')
        messages =[core.configobj.picture_root]
        return json.dumps(messages)

class datadir:
    def GET(self):
        web.header('Content-Type', 'application/json')
        messages =[core.configobj.data_dir]
        return json.dumps(messages)
    
class logdir:
    def GET(self):
        web.header('Content-Type', 'application/json')
        messages =[core.configobj.log_dir]
        return json.dumps(messages)
