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
import web
import logging
import os
import json

from web import form
from lib import smugpy

import core
import db
import dbSchema
import fileScan
import messaging
import smugScan


myLogger = logging.getLogger('smugglerWeb')

working_dir = os.getcwd()
default_log = ''.join([working_dir, '/log']) 
default_data = ''.join([working_dir, '/data']) 


def make_text(string):
    return string

urls = (
        '/notify','notify',
        '/fullscan', 'fullscan',
        '/localscan', 'localscan',
        '/smugmugscan', 'smugmugscan',
        '/home', 'home',
        '/examples', 'examples',
        '/setup', 'setup',
        '/(.*)', 'index'
        )
render = web.template.render('template/')

app = web.application(urls, globals())

setup_form = form.Form(
                web.form.Textbox('root_dir', form.notnull, form.Validator('The root image directory must already exist.', lambda path: os.path.isdir(path)), id='root_dir'),
                web.form.Textbox('log_dir', form.notnull, form.Validator('The log directory must already exist.', lambda path: os.path.isdir(path)), id='log_dir', value = default_log),
                web.form.Textbox('data_dir', form.notnull, form.Validator('The data directory must already exist.', lambda path: os.path.isdir(path)), id='data_dir', value = default_data),
                web.form.Button('Save', id='save', class_="formbutton")
                )

def run():
    #web.httpserver.runsimple(app.wsgifunc(), ("0.0.0.0",8080))
    app.run()


class notify:
    def GET(self):
        send = []
        
        for message in messaging.messages.getMessages():
            send.append({'type':message.type, 'message':message.message})
        web.header('Content-Type', 'application/json')
        
        return json.dumps(send)
    
class fullscan:
    def GET(self):
        fileScan.localScan.start()
        smugScan.smugScan.start()
        web.header('Content-Type', 'application/json')
        messages =["Passed along request to Scan everything."]
        return json.dumps(messages)

class localscan:
    def GET(self):
        fileScan.localScan.start()
        web.header('Content-Type', 'application/json')
        messages =["Passed along request to Scan Locally."]
        return json.dumps(messages)
    
class smugmugscan:
    def GET(self):
        smugScan.smugScan.start()
        web.header('Content-Type', 'application/json')
        messages =["Passed along request to Scan SmugMug."]
        return json.dumps(messages)

class index:
    def GET(self, scan):
        print scan
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
                core.smugmug.auth_getAccessToken()
            except smugpy.SmugMugException:
                return self._GET(form, True)
            else:
                #self.first = False
                core.PICTURE_ROOT  = form.value['root_dir']
                core.LOG_DIR = form.value['log_dir']
                core.DATA_DIR = form.value['data_dir']
                core.saveConfig()
                myLogger.info("Config file Created.")
                dbSchema.upgradeSchema()
                myLogger.info("Database started.")
                db.setOAuthConnectionDetails(core.smugmug.oauth_token, core.smugmug.oauth_token_secret)
                return web.seeother('/')
    
    def _GET(self, form, authBad):
        if core.smugmug.oauth_token == None:
            core.smugmug.auth_getRequestToken()
        url = core.smugmug.authorize("Full", "Modify")
        return render.setup(form, url, authBad)

class examples:
    def GET(self):
        return render.examples()        

class home:
    def GET(self):
        return render.home()
    

    
