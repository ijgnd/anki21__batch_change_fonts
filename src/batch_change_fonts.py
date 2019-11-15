"""
Add-on for Anki 2.1
Copyright: Ankitects Pty Ltd and contributors
           ijgnd

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import aqt
from anki.lang import _
from aqt.qt import *
from aqt.fields import FieldDialog
from aqt.utils import (
    askUser,
    tooltip,
)

from .forms import dialog


class Batch_Fonts_Dialog(QDialog):
    def __init__(self):
        parent = aqt.mw.app.activeWindow()
        QDialog.__init__(self, parent=parent)
        self.setWindowModality(Qt.WindowModal)
        self.bfonts = dialog.Ui_Dialog()
        self.bfonts.setupUi(self)


# change all fonts of current note type from editor window
def onAllFonts(self):
    m = Batch_Fonts_Dialog()
    m.setWindowTitle("Anki Set Fonts For All Fields Of This Note")
    # load current values into window
    fld = self.model['flds'][self.currentIdx]
    m.bfonts.fontComboBox.setCurrentFont(QFont(fld['font']))
    m.bfonts.spinBox.setValue(fld['size'])
    if m.exec():
        font = m.bfonts.fontComboBox.currentFont().family()
        size = m.bfonts.spinBox.value()
        for i in range(len(self.model['flds'])):
            fld = self.model['flds'][i]
            fld['font'] = font
            fld['size'] = size
        # reload for current value, adjusted from loadField
        fld = self.model['flds'][self.currentIdx]
        f = self.form
        f.fontFamily.setCurrentFont(QFont(fld['font']))
        f.fontSize.setValue(fld['size'])
    else:
        tooltip('declined')
FieldDialog.onAllFonts = onAllFonts


# overwrite/monkey patch function from aqt/fields.py
# wrapping doesn't make sense: __init__ends with exec which
# wait until window is closed. So I can't wrap my function
# so that it is run after __init__. Wrapping so that it runs
# before doesn't help much either.
def __init__(self, mw, note, ord=0, parent=None):
    QDialog.__init__(self, parent or mw) #, Qt.Window)
    self.mw = mw
    self.parent = parent or mw
    self.note = note
    self.col = self.mw.col
    self.mm = self.mw.col.models
    self.model = note.model()
    self.mw.checkpoint(_("Fields"))
    self.form = aqt.forms.fields.Ui_Dialog()
    self.form.setupUi(self)

    # # # # start of my mod
    # up/down
    self.form.udbox = QHBoxLayout()
    layout = self.form.udbox

    bu = QToolButton()
    bu.setArrowType(Qt.UpArrow)
    bu.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    bu.clicked.connect(lambda _: self.onMove(-1))
    layout.addWidget(bu)

    bd = QToolButton()
    bd.setArrowType(Qt.DownArrow)
    bd.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    bd.clicked.connect(lambda _: self.onMove(1))
    layout.addWidget(bd)

    self.form.verticalLayout_3.addLayout(self.form.udbox)
    self.form.allfonts = QPushButton(self)
    self.form.allfonts.setText("AllFonts")
    self.form.allfonts.clicked.connect(self.onAllFonts)
    self.form.verticalLayout_3.addWidget(self.form.allfonts)

    # # # # end of my mod

    self.setWindowTitle(_("Fields for %s") % self.model['name'])
    self.form.buttonBox.button(QDialogButtonBox.Help).setAutoDefault(False)
    self.form.buttonBox.button(QDialogButtonBox.Close).setAutoDefault(False)
    self.currentIdx = None
    self.oldSortField = self.model['sortf']
    self.fillFields()
    self.setupSignals()
    self.form.fieldList.setCurrentRow(0)
    self.exec_()
FieldDialog.__init__ = __init__


# minimal modification of onPosition(self, delta=-1):
def onMove(self, direction):
    idx = self.currentIdx
    try:
        pos = idx + direction   # check if idx is None
    except:
        return
    else:
        l = len(self.model['flds'])
        if not 0 <= pos <= l-1:
            return
        self.saveField()
        f = self.model['flds'][self.currentIdx]
        self.mw.progress.start()
        self.mm.moveField(self.model, f, pos)
        self.mw.progress.finish()
        self.fillFields()
        self.form.fieldList.setCurrentRow(pos)
FieldDialog.onMove = onMove


question = ("Do you really want to set the fonts \n"
            "%s to the font: \n"
            "     %s   \n"
            "and this size: \n"
            "     %s")


# change all fields for all note types
def batch_change_fonts_all_fields_all_notes():
    m = Batch_Fonts_Dialog()
    m.setWindowTitle("Anki Set Fonts For All Fields Of ALL Notes (in the editor)")
    # load current values into window
    try:
        m.bfonts.fontComboBox.setCurrentFont("Arial")
        m.bfonts.spinBox.setValue(fld['size'])
    except:
        pass
    if m.exec():
        f = m.bfonts.fontComboBox.currentFont().family()
        s = m.bfonts.spinBox.value()
        if askUser(question % ("for all fields of all notes (in the editor)", str(f), str(s))):
            for m in aqt.mw.col.models.all():
                for c in m['flds']:
                    c['font'] = str(f)
                    c['size'] = int(s)
                aqt.mw.col.models.save(m)
            aqt.mw.col.models.flush()
            tooltip('Done')


# change Browser Appearance for all note types
def batch_browser_change_display_fonts():
    m = Batch_Fonts_Dialog()
    m.setWindowTitle("Anki Set Fonts used in BROWSER table (Browser Appearance)")
    # load current values into window
    try:
        m.bfonts.fontComboBox.setCurrentFont("Arial")
        m.bfonts.spinBox.setValue(fld['size'])
    except:
        pass
    if m.exec():
        f = m.bfonts.fontComboBox.currentFont().family()
        s = m.bfonts.spinBox.value()
        if askUser(question % ("that is used in Browser table for all cards", str(f), str(s))):
            for m in aqt.mw.col.models.all():
                for c in m['tmpls']:
                    c['bfont'] = str(f)
                    c['bsize'] = int(s)
                aqt.mw.col.models.save(m)
            tooltip('Done')


bfm = QMenu("Batch change fonts", aqt.mw)
aqt.mw.form.menuTools.addMenu(bfm)

abf = QAction("... for all fields of all notes (in the editor)", aqt.mw)
abf.triggered.connect(batch_change_fonts_all_fields_all_notes)
bfm.addAction(abf)

abf_browser = QAction("... for Browser Appearance", aqt.mw)
abf_browser.triggered.connect(batch_browser_change_display_fonts)
bfm.addAction(abf_browser)
