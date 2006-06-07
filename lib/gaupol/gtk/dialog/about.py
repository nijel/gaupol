# Copyright (C) 2005-2006 Osmo Salomaa
#
# This file is part of Gaupol.
#
# Gaupol is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# Gaupol is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# Gaupol; if not, write to the Free Software Foundation, Inc., 51 Franklin
# Street, Fifth Floor, Boston, MA 02110-1301, USA.


"""Dialog to display information about Gaupol."""


from gettext import gettext as _

import gtk

from gaupol           import __version__
from gaupol.base.util import wwwlib


# Translators: This is a special message that shouldn't be translated
# literally. It is used in the about dialog to give credits to the translators.
# Thus, you should translate it to your name and email address.  You can also
# include other translators who have contributed to this translation; in that
# case, please write them on separate lines seperated by newlines (\n).
TRANSLATORS = _('translator-credits')

LICENSE = \
'Gaupol is free software; you can redistribute it and/or modify it under the' \
'terms of the GNU General Public License as published by the Free Software' \
'Foundation; either version 2 of the License, or (at your option) any later' \
'version.\n\n' \
'Gaupol is distributed in the hope that it will be useful, but WITHOUT ANY' \
'WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS ' \
'FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more ' \
'details.\n\n' \
'You should have received a copy of the GNU General Public License along ' \
'with Gaupol; if not, write to the Free Software Foundation, Inc., 51 ' \
'Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.'


class AboutDialog(gtk.AboutDialog):

    """Dialog to display application information."""

    def __init__(self, parent):

        gtk.AboutDialog.__init__(self)

        self.set_name('Gaupol')
        self.set_version(__version__)
        self.set_copyright(u'Copyright \xa9 2005-2006 Osmo Salomaa')
        self.set_comments(_('Subtitle editor'))
        self.set_website_label('http://home.gna.org/gaupol')
        self.set_authors(['Osmo Salomaa <otsaloma@cc.hut.fi>'])
        self.set_artists(['Osmo Salomaa <otsaloma@cc.hut.fi>'])
        self.set_translator_credits(TRANSLATORS)
        self.set_license(LICENSE)

        icon_theme = gtk.icon_theme_get_default()
        if icon_theme.has_icon('gaupol'):
            self.set_logo_icon_name('gaupol')

        gtk.about_dialog_set_url_hook(self._on_url_clicked)
        self.set_wrap_license(True)
        self.set_transient_for(parent)

    def _on_url_clicked(self, *args):
        """Open website in browser."""

        wwwlib.browse_url('http://home.gna.org/gaupol')
