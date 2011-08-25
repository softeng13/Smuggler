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
#Given to me by SmugMug for this app. Should never ever change, so that 
#probably means it will
API_KEY = "RXgvpRaLqaQdEgoKQhaQZZiqiItVByuS"
OAUTH_SECRET = "b308a33ffc2f417b4b1ba50e3933e0fa"

import config
import db
import dbSchema
import fileScan
import fileUtil
import messaging
import pictureReport
import processRunner
import smugglerWeb
import smugScan
import syncUtil
import webUtil

#the file extensions of pictures we can upload
EXTENSIONS = [".jpg", ".jpeg", ".jpe",".jfif",".jif", ".png", ".gif"]

#default configuration object
configobj = config.Config()

smugmugscan = processRunner.Runner(smugScan.getAllPictureInfo, 'SmugMug Scan has been Started.', 'Finished scanning SmugMug', 'SmugMug Scan had already been Started.')
smugmuglocalscan = processRunner.Runner(fileScan.findPictures, 'Local File Scan has been Started.', 'Finished Scanning Local Files.', 'Local Scan had already been Started.')

smugmugsync = processRunner.Runner(syncUtil.sync, 'SmugMug Sync has been Started.', 'Finished Sync with SmugMug', 'SmugMug Sync had already been Started.')
smugmugcontainers = processRunner.Runner(syncUtil.createMissingContainers, 'Staring to create missing Categories, SubCategories, and Albums on SmugMug.', 'Finished Creating Categories, SubCategories, and Albums on SmugMug.', 'Process to create Containers was already running.')
smugmugcategories = processRunner.Runner(syncUtil.createMissingCategories, 'Staring to create missing Categories on SmugMug.', 'Finished Creating Categories on SmugMug.', 'Process to create Categories was already running.')
smugmugsubcategories = processRunner.Runner(syncUtil.createMissingSubCategories, 'Staring to create missing SubCategories on SmugMug.', 'Finished Creating SubCategories on SmugMug.', 'Process to create SubCategories was already running.')
smugmugalbums = processRunner.Runner(syncUtil.createMissingAlbums, 'Staring to create missing Albums on SmugMug.', 'Finished Creating Albums on SmugMug.', 'Process to create Albums was already running.')
smugmugdownload = processRunner.Runner(syncUtil.download, 'Staring to download missing images from SmugMug.', 'Finished downloading missing images from SmugMug.', 'Process to download images is already running.')
 
