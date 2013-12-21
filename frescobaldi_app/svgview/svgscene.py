# This file is part of the Frescobaldi project, http://www.frescobaldi.org/
#
# Copyright (c) 2008 - 2012 by Wilbert Berendsen
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# See http://www.gnu.org/licenses/ for more information.

"""
The GraphicsScene for the SVG view.
"""

import os
import sys

from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4.QtWebKit import QGraphicsWebView

import app
import textedit


from . import __path__


def getJsScript(filename):
    """fetch the js file"""
    directory = __path__[0]
    with open(os.path.join(directory, filename), 'r') as fileObject:
        jsValue = fileObject.read()
	return jsValue


class SvgScene(QtGui.QGraphicsScene):
    def __init__(self, parent):
        super(QtGui.QGraphicsScene, self).__init__(parent)
        self.view = QtGui.QGraphicsView(self)
        self.webview = QGraphicsWebView()
        self.webview.setFlags(QtGui.QGraphicsItem.ItemClipsToShape)
        self.webview.setCacheMode(QtGui.QGraphicsItem.NoCache)
        self.addItem(self.webview)

        self.webview.loadFinished.connect(self.svgLoaded)
        
    def svgLoaded(self):
        frame = self.webview.page().mainFrame()
        fsize = frame.contentsSize()
        self.webview.resize(QtCore.QSizeF(fsize))
        self.view.resize(fsize.width() + 10, fsize.height() + 10)

        self.links = JSLink(self.parent().mainwindow())
        frame.addToJavaScriptWindowObject("pyLinks", self.links)
        frame.evaluateJavaScript(getJsScript('pointandclick.js'))
        
    def toolTipText(self, txt):
		self.webview.setToolTip(txt)


class JSLink(QtCore.QObject):
    """functions to be called from JavaScript
    
    using addToJavaScriptWindowObject
    
    """
    def __init__(self, mainwindow):
        self.mainwindow = mainwindow
        super(JSLink, self).__init__()
        
    @QtCore.pyqtSlot(str)
    def setCursor(self, url):
        """set cursor in source by clicked textedit link""" 
        t = textedit.link(url)
        doc = app.openUrl(QtCore.QUrl.fromLocalFile(t.filename))
        cursor = QtGui.QTextCursor(doc)
        b = doc.findBlockByNumber(t.line - 1)
        p = b.position() + t.column
        cursor.setPosition(p)
        self.mainwindow.setTextCursor(cursor)
	
    @QtCore.pyqtSlot(str)	    
    def hover(self, url):
	    """actions when user set mouse over link"""
	    #TODO: implement highlighting in code when user hovers a link
	    pass
	    
    @QtCore.pyqtSlot(str)	    
    def pyLog(self, txt):
	    """Temporary function. Print to Python console."""
	    print txt
		
    
    
