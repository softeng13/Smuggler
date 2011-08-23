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
import webUtil

def missingSmugMugCategoriesHTML(conn):
    rows = db.missingSmugMugCategories(conn)
    columns = ["Category"]
    return webUtil.getTable(columns, rows)

def missingSmugMugSubCategoriesHTML(conn):
    rows = db.missingSmugMugSubCategories(conn)
    columns = ["SubCategory", "Category", "Category Id", "New Category Id"]
    columnsclass = [None, None, "hidden", "hidden"]
    return webUtil.getTable(columns, rows, columnsclass)

def missingSmugMugAlbumsHTML(conn):
    rows = db.missingSmugMugAlbums(conn)
    columns = ["Album", "Category", "Category Id", "New Category Id","SubCategory", "SubCategory Id", "New SubCategory Id"]
    columnsclass = [None, None, "hidden", "hidden",None, "hidden", "hidden"]
    return webUtil.getTable(columns, rows, columnsclass)