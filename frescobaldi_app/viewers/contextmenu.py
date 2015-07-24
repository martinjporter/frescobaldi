# This file is part of the Frescobaldi project, http://www.frescobaldi.org/
#
# Copyright (c) 2008 - 2014 by Wilbert Berendsen
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
Base class for viewers' context menus.
"""

from __future__ import unicode_literals

from PyQt4.QtCore import QObject, QUrl
from PyQt4.QtGui import QApplication, QMenu


import icons

class AbstractViewerContextMenu(QObject):
    """Base class for viewers' context menus.
    It provides the template method pattern to generate the menu.
    Subclasses can override individual parts of the menu this way."""

    def __init__(self, panel):
        self._panel = panel
        self._actionCollection = panel.actionCollection
        self._surface = None
        self._menu = QMenu(self._panel)

    def surface(self):
        """Return the (cached) surface"""
        result = self._surface or self._panel.widget().view.surface()
        return result

    def addSeparator(self):
        """Add a separator to the menu."""
        self._menu.addSeparator()
        
    def addCopyImageAction(self):
        """Add action to copy image if available"""
        if self.surface().hasSelection():
            self._menu.addAction(self._actionCollection.music_copy_image)

    def addEditInPlaceAction(self, cursor, position):
        """Add action to edit snippet if on a textedit link"""
        a = self._menu.addAction(icons.get("document-edit"), _("Edit in Place"))
        @a.triggered.connect
        def edit():
            from . import editinplace
            editinplace.edit(self._panel.widget(), cursor, position)

    def addLinkAction(self, link):
        """Add action if on an arbitrary link"""
        m = self._menu
        a = m.addAction(icons.get("window-new"), _("Open Link in &New Window"))
        @a.triggered.connect
        def open_in_browser():
            import helpers
            helpers.openUrl(QUrl(link.url()))

        a = m.addAction(icons.get("edit-copy"), _("Copy &Link"))
        @a.triggered.connect
        def copy_link():
            QApplication.clipboard().setText(link.url())

    def addCursorLinkActions(self):
        """Add actions if on a textedit or arbitrary link"""
        if self._cursor:
            self.addEditInPlaceAction(self._cursor, self._position)
        elif self._link:
            self.addLinkAction(self._link)

    def addZoomActions(self):
        """Add actions to zoom the viewer"""
        m = self._menu
        m.addSeparator()
        sm = QMenu(m)
        sm.setTitle(_("Zoom"))
        m.addMenu(sm)
        ac = self._actionCollection
        sm.addAction(ac.music_fit_width)
        sm.addAction(ac.music_fit_height)
        sm.addAction(ac.music_fit_both)
        sm.addSeparator()
        sm.addAction(ac.music_zoom_in)
        sm.addAction(ac.music_zoom_out)
        sm.addAction(ac.music_zoom_original)

    def addOpenCloseActions(self):
        """Add actions to close documents.
        This is not implemented in the base class"""
        pass
        # TODO: Should these also be available in other viewers
        # than the manusccript viewer?

    def addSynchronizeAction(self):
        """Add an action telling the viewer to
        always try syncing with the input editor."""
        m = self._menu
        ac = self._actionCollection
        m.addAction(ac.music_sync_cursor)

    def addShowToolbarAction(self):
        """Add action to toggle the visibility of
        the viewer's toolbar"""
        m = self._menu
        ac = self._actionCollection
        m.addAction(ac.viewer_show_toolbar)

    def addHelpAction(self):
        """Add help menu item"""
        m = self._menu
        m.addSeparator()
        a = m.addAction(icons.get("help-contents"), _("Help"))
        @a.triggered.connect
        def help():
            import userguide
            userguide.show(self._panel.viewerName())

    def show(self, position, link, cursor, methods = None):
        """Build the panel's context menu dynamically.
        Implements the template method pattern to allow
        subclasses to override each step.
        If methods passes a list of methods these will be
        called instead to construct the menu, making it
        possible to change order or add methods not
        available in the base class."""

        self._position = position
        self._link = link
        self._cursor = cursor

        self._menu.clear()

        if not methods:
            # Actions affecting the current link(selection)
            self.addCopyImageAction()
            self.addCursorLinkActions()
            # Actions affecting the currently opened documents
            self.addOpenCloseActions()
            # Actions affecting the viewer's state
            self.addZoomActions()
            self.addSynchronizeAction()
            self.addShowToolbarAction()
        else:
            for m in methods:
                m()
        # The help action is added always
        self.addHelpAction()

        # show it!
        if self._menu.actions():
            self._menu.exec_(position)
        # TODO: Can this really be removed?
        # it had to be commented out because in the documents submenu
        # there popped up issues with deleted objects (the menu was already
        # deleted when the signal was emitted)
#        self._menu.deleteLater()
