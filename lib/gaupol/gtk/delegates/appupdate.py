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


"""Updating of application GUI."""


try:
    from psyco.classes import *
except ImportError:
    pass

import os

import gobject
import gtk

from gaupol.constants        import Framerate, Mode
from gaupol.gtk.colconstants import *
from gaupol.gtk.delegates    import Delegate, UIMAction, UIMActions
from gaupol.gtk.util         import config, gtklib


class ActivateNextProjectAction(UIMAction):

    """Activate the next page in the notebook."""

    uim_action_item = (
        'activate_next_project',
        None,
        _('_Next'),
        '<control>Page_Down',
        _('Activate the project in the next tab'),
        'on_activate_next_project_activated'
    )

    uim_paths = ['/ui/menubar/projects/next']

    @classmethod
    def is_doable(cls, application, page):
        """Return whether action can or cannot be done."""

        if page is None:
            return False

        index = application.pages.index(page)
        last_index = len(application.pages) - 1
        return bool(index < last_index)


class ActivatePreviousProjectAction(UIMAction):

    """Activate the previous page in the notebook."""

    uim_action_item = (
        'activate_previous_project',
        None,
        _('_Previous'),
        '<control>Page_Up',
        _('Activate the project in the previous tab'),
        'on_activate_previous_project_activated'
    )

    uim_paths = ['/ui/menubar/projects/previous']

    @classmethod
    def is_doable(cls, application, page):
        """Return whether action can or cannot be done."""

        if page is None:
            return False

        return bool(application.pages.index(page) > 0)


class ApplicationUpdateDelegate(Delegate):

    """Updating of application GUI."""

    def on_activate_next_project_activated(self, *args):
        """Switch to the next page in the notebook."""

        self.notebook.next_page()

    def on_activate_previous_project_activated(self, *args):
        """Switch to the previous page in the notebook."""

        self.notebook.prev_page()

    def on_notebook_page_switched(self, notebook, pointer, page_no):
        """Set GUI properties for page switched to."""

        if not self.pages:
            return

        page = self.pages[page_no]
        self.set_sensitivities(page)
        page.view.grab_focus()

    def on_project_toggled(self, unknown, action):
        """Switch page in the notebook."""

        index = int(action.get_name().split('_')[-1])
        self.notebook.set_current_page(index)

    def on_video_filechooser_response(self, filechooser, response):
        """Set video file path."""

        page = self.get_current_page()
        if response == gtk.RESPONSE_ACCEPT:
            page.project.video_path = filechooser.get_filename()
        self.set_sensitivities(page)

    def on_window_state_event(self, window, event):
        """Remember whether window is maximized or not."""

        state = event.new_window_state
        maximized = bool(state & gtk.gdk.WINDOW_STATE_MAXIMIZED)
        config.application_window.maximized = maximized

    def _set_action_sensitivities(self, page):
        """Set sensitivities of all actions for page."""

        for cls in UIMActions.classes:
            doable = cls.is_doable(self, page)
            for path in cls.uim_paths:
                self.uim.get_action(path).set_sensitive(doable)
            for widget in cls.widgets:
                getattr(self, widget).set_sensitive(doable)

    def set_sensitivities(self, page=None):
        """
        Set sensitivities and visibilities of action and widgets.

        page needs to be given when not setting the properties for the page
        currently active in the notebook.
        """
        # NOTE:
        # This method updates pretty much all sensitivities that can be
        # updated. If this proves to be too slow, it can be complicated so
        # that only what really needs to be updated is updated.

        page = page or self.get_current_page()

        self._set_widget_states(page)
        self._set_visibility_of_statusbars(page)
        self._set_action_sensitivities(page)
        self._set_undo_and_redo_tooltips(page)

    def set_status_message(self, message, clear=True):
        """
        Set a message to the message statusbar.

        If message is None, statusbar will be cleared.
        Return False (to avoid iteration with gobject.timeout_add).
        """
        self.message_statusbar.pop(0)

        # Stop previous timeout event from affecting this new entry.
        if self.message_tag is not None:
            gobject.source_remove(self.message_tag)

        # Set tooltip.
        event_box = gtklib.get_event_box(self.message_statusbar)
        self.tooltips.set_tip(event_box, message)

        if message is None:
            return False
        self.message_statusbar.push(0, message)

        # Clear message after 6 seconds.
        if clear:
            method = self.set_status_message
            self.message_tag = gobject.timeout_add(6000, method, None)

        return False

    def _set_undo_and_redo_tooltips(self, page):
        """Set tooltips for undo and redo."""

        if page is None:
            return

        if page.project.can_undo():
            description = page.project.undoables[0].description
            tip = _('Undo %s') % description[0].lower() + description[1:]
            self.undo_button.set_tooltip(self.tooltips, tip)
            self.uim.get_action('/ui/menubar/edit/undo').props.tooltip = tip

        if page.project.can_redo():
            description = page.project.redoables[0].description
            tip = _('Redo %s') % description[0].lower() + description[1:]
            self.redo_button.set_tooltip(self.tooltips, tip)
            self.uim.get_action('/ui/menubar/edit/redo').props.tooltip = tip

    def _set_visibility_of_statusbars(self, page):
        """Set the visibility of the statusbars based on visible columns."""

        # Show only the message statusbar if no projects are open.
        if page is None:
            self.main_text_statusbar.hide()
            self.tran_text_statusbar.hide()
            self.message_statusbar.set_has_resize_grip(True)
            return

        # Get column visibility.
        text_visible = page.view.get_column(MTXT).get_visible()
        tran_visible = page.view.get_column(TTXT).get_visible()

        # Assume everything is correct if visibilities match.
        if text_visible == self.main_text_statusbar.props.visible and \
           tran_visible == self.tran_text_statusbar.props.visible:
            return

        # Set statusbar visibilities.
        self.main_text_statusbar.props.visible = text_visible
        self.tran_text_statusbar.props.visible = tran_visible

        # Show the resize grip only in the right-most statusbar.
        if tran_visible:
            self.message_statusbar.set_has_resize_grip(False)
            self.main_text_statusbar.set_has_resize_grip(False)
            self.tran_text_statusbar.set_has_resize_grip(True)
        else:
            if text_visible:
                self.message_statusbar.set_has_resize_grip(False)
                self.main_text_statusbar.set_has_resize_grip(True)
                self.tran_text_statusbar.set_has_resize_grip(False)
            else:
                self.message_statusbar.set_has_resize_grip(True)
                self.main_text_statusbar.set_has_resize_grip(False)
                self.tran_text_statusbar.set_has_resize_grip(False)

    def _set_widget_states(self, page):
        """Set the states of widgets."""

        if page is None:
            self.tooltips.disable()
            self.set_status_message(None)
            self.window.set_title('Gaupol')
            self.video_file_button.unselect_all()
            return

        # Enable tooltips.
        self.tooltips.enable()

        # Set window title.
        title = page.update_tab_labels()
        self.window.set_title(title)

        # Set edit mode state.
        edit_mode_name = Mode.id_names[page.edit_mode]
        path = '/ui/menubar/view/%ss' % edit_mode_name
        self.uim.get_action(path).set_active(True)

        # Set video file path.
        if page.project.video_path is not None:
            self.video_file_button.set_filename(page.project.video_path)
        else:
            self.video_file_button.unselect_all()
            if page.project.main_file is not None:
                dirname = os.path.dirname(page.project.main_file.path)
                self.video_file_button.set_current_folder(dirname)
        event_box = gtklib.get_event_box(self.video_file_button)
        self.tooltips.set_tip(event_box, page.project.video_path)

        # Set framerate state.
        framerate_name = Framerate.id_names[page.project.framerate]
        path = '/ui/menubar/view/framerate/%s' % framerate_name
        self.uim.get_action(path).set_active(True)
        self.framerate_combo_box.set_active(page.project.framerate)

        # Set column visibility states.
        for i in range(len(Column.id_names)):
            tree_view_column = page.view.get_column(i)
            visible = tree_view_column.props.visible
            path = '/ui/menubar/view/columns/%s' % Column.id_names[i]
            self.uim.get_action(path).set_active(visible)
