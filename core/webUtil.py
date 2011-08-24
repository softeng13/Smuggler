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
import itertools


myLogger = logging.getLogger('webUtil')

def getHeaderRow(columns, columnsclass=[]):
    result = "<thead><tr>"
    for column, columnclass in itertools.izip_longest(columns,columnsclass):
        if (columnclass == None):
            add = "<th>"+column+"</th>"
        else:
            add = "<th class=\""+columnclass+"\">"+str(column)+"</th>"
        result = result + add
    result = result + "</tr></thead>"
    return result

def getResultRow(columns, css, columnsclass=[]):
    result = "<tr  class=\""+css+"\">"
    for column, columnclass in itertools.izip_longest(columns,columnsclass):
        if column == None:
            column = ''
        if (columnclass == None):
            add = "<td>"+str(column)+"</td>"
        else:
            add = "<td class=\""+columnclass+"\">"+str(column)+"</td>"
        result = result + add
    result = result + "</tr>"
    return result

def getTable(columns, rows, columnsclass=[]):
    table = "<table>"
    table = table + getHeaderRow(columns, columnsclass) + "<tbody>"
    css = 'odd'
    for row in rows:
        table = table + getResultRow(row,css,columnsclass)
        if (css == 'odd'):
            css = 'even'
        else:
            css ='odd'
    
    table = table + "</tbody></table>"
    myLogger.debug(table)
    return table
