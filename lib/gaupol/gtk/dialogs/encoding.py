# Copyright (C) 2005 Osmo Salomaa
#
# This file is part of Gaupol.
#
# Gaupol is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Gaupol is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Gaupol; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA


"""Dialogs for selecting character encodings."""


try:
    from psyco.classes import *
except ImportError:
    pass

import gobject
import gtk

from gaupol.base.util import encodinglib
from gaupol.gtk.util  import config, gtklib


DESC, NAME, SHOW = 0, 1, 2


class EncodingDialog(object):

    """Dialog for selecting a character encoding."""

    def __init__(self, parent):

        glade_xml = gtklib.get_glade_xml('encoding-dialog.glade')
        self._dialog = glade_xml.get_widget('dialog')
        self._view   = glade_xml.get_widget('tree_view')

        self._dialog.set_transient_for(parent)
        self._dialog.set_default_response(gtk.RESPONSE_OK)

        label = glade_xml.get_widget('label')
        label.set_mnemonic_widget(self._tree_view)

        self._init_view()

    def _init_view(self):
        """Initialize the list of encodings."""

        self._view.columns_autosize()

        store = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING)
        self._view.set_model(store)

        selection = self._view.get_selection()
        selection.set_mode(gtk.SELECTION_SINGLE)
        selection.unselect_all()

        cell_renderer_0 = gtk.CellRendererText()
        cell_renderer_1 = gtk.CellRendererText()

        TVC = gtk.TreeViewColumn
        tree_view_column_0 = TVC(_('Description'), cell_renderer_0, text=0)
        tree_view_column_1 = TVC(_('Encoding')   , cell_renderer_1, text=1)

        # Set column properties and append columns.
        for i in range(2):
            tree_view_column = eval('tree_view_column_%d' % i)
            self._view.append_column(tree_view_column)
            tree_view_column.set_resizable(True)
            tree_view_column.set_clickable(True)
            tree_view_column.set_sort_column_id(i)

        store.set_sort_column_id(DESC, gtk.SORT_ASCENDING)

        # Insert data.
        for entry in encodinglib.get_valid_encodings():
            store.append([entry[2], entry[1]])

        # Set view size.
        width, height = self._view.size_request()
        width  = min(500, width  + 24)
        height = min(400, height + 24)
        self._view.set_size_request(width, height)

    def destroy(self):
        """Destroy the dialog."""

        self._dialog.destroy()

    def get_encoding(self):
        """
        Get the selected encoding.

        Return encoding or None.
        """
        selection = self._view.get_selection()
        store, rows = selection.get_selected_rows()

        if not rows:
            return None
        else:
            row = rows[0]

        display_name = store[row][NAME]
        return encodinglib.get_python_name(display_name)

    def run(self):
        """Show and run the dialog."""

        self._dialog.show()
        self._view.grab_focus()
        return self._dialog.run()


class AdvancedEncodingDialog(EncodingDialog):

    """Dialog for selecting character encodings."""

    def __init__(self, parent):

        EncodingDialog.__init__(self, parent)

    def _init_view(self):
        """Initialize the list of encodings."""

        self._view.columns_autosize()

        store = gtk.ListStore(
            gobject.TYPE_STRING,
            gobject.TYPE_STRING,
            gobject.TYPE_BOOLEAN
        )
        self._view.set_model(store)

        selection = self._view.get_selection()
        selection.set_mode(gtk.SELECTION_SINGLE)
        selection.unselect_all()

        cell_renderer_0 = gtk.CellRendererText()
        cell_renderer_1 = gtk.CellRendererText()
        cell_renderer_2 = gtk.CellRendererToggle()

        cell_renderer_2.connect('toggled', self._on_view_cell_toggled)

        TVC = gtk.TreeViewColumn
        tree_view_column_0 = TVC(_('Description') , cell_renderer_0, text  =0)
        tree_view_column_1 = TVC(_('Encoding')    , cell_renderer_1, text  =1)
        tree_view_column_2 = TVC(_('Show In Menu'), cell_renderer_2, active=2)

        # Set column properties and append columns.
        for i in range(3):
            tree_view_column = eval('tree_view_column_%d' % i)
            self._view.append_column(tree_view_column)
            tree_view_column.set_resizable(True)
            tree_view_column.set_clickable(True)
            tree_view_column.set_sort_column_id(i)

        store.set_sort_column_id(DESC, gtk.SORT_ASCENDING)

        # Insert data.
        visible_encodings = config.file.visible_encodings
        for entry in encodinglib.get_valid_encodings():
            store.append([entry[2], entry[1], entry[0] in visible_encodings])

        # Set view size.
        width, height = self._view.size_request()
        width  = min(500, width  + 24)
        height = min(400, height + 24)
        self._view.set_size_request(width, height)

    def get_visible_encodings(self):
        """Get the encodings chosen to be visible."""

        store = self._view.get_model()
        visible_encodings = []

        for row in range(len(store)):
            if store[row][SHOW]:
                encoding = encodinglib.get_python_name(store[row][NAME])
                visible_encodings.append(encoding)

        return visible_encodings

    def _on_view_cell_toggled(self, cell_renderer, row):
        """Toggle a value in a cell in the "Show In Menu" column."""

        store = self._view.get_model()
        store[row][SHOW] = not store[row][SHOW]
