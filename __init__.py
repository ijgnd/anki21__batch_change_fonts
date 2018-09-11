# -*- coding: utf-8 -*-
# # - License: AGPLv3

import aqt
from aqt import mw
from aqt.qt import *
from aqt.fields import FieldDialog
from aqt.utils import tooltip, askUser

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QPushButton, QHBoxLayout, QToolButton

from . import dialog


class Batch_Fonts_Dialog(QDialog):
    def __init__(self):
        parent = aqt.mw.app.activeWindow()
        QDialog.__init__(self, parent=parent)
        self.setWindowModality(Qt.WindowModal)
        self.bfonts = dialog.Ui_Dialog()  
        self.bfonts.setupUi(self)


#change all fonts of current note type from editor window
def onAllFonts(self):
    m=Batch_Fonts_Dialog()
    m.setWindowTitle("Anki Set Fonts For All Fields Of This Note")
    #load current values into window
    fld = self.model['flds'][self.currentIdx]
    m.bfonts.fontComboBox.setCurrentFont(QFont(fld['font']))
    m.bfonts.spinBox.setValue(fld['size'])
    if m.exec_():  # this is True if dialog is 'accepted, False otherwise  https://stackoverflow.com/a/11553456
        font = m.bfonts.fontComboBox.currentFont().family()
        size = m.bfonts.spinBox.value()
        for i in range(len(self.model['flds'])):
            fld = self.model['flds'][i]
            fld['font'] = font
            fld['size'] = size
        #reload for current value, adjusted from loadField
        fld = self.model['flds'][self.currentIdx]
        f = self.form
        f.fontFamily.setCurrentFont(QFont(fld['font']))
        f.fontSize.setValue(fld['size'])
    else:
        tooltip('declined')
FieldDialog.onAllFonts = onAllFonts


#overwrite/monkey patch function from aqt/fields.py
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

    ####start of my mod
    #up/down
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


    #self.form.setupUi(self) muss davor sein, sonst sind ja attribute noch nicht vergeben
    self.form.allfonts = QPushButton(self)
    self.form.allfonts.setText("AllFonts")
    self.form.allfonts.clicked.connect(self.onAllFonts)
    self.form.verticalLayout_3.addWidget(self.form.allfonts)

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


#minimal modification of onPosition(self, delta=-1):
def onMove(self, direction):
    idx = self.currentIdx
    try: 
        pos = idx + direction    #check if idx is None
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



#change for all note types from menu
def batch_change_fonts_all_fields_all_notes():
    m=Batch_Fonts_Dialog()
    m.setWindowTitle("Anki Set Fonts For All Fields Of ALL Notes")
    #load current values into window
    try:
        m.bfonts.fontComboBox.setCurrentFont("Arial")
        m.bfonts.spinBox.setValue(fld['size'])
    except:
        pass
    if m.exec_():  # this is True if dialog is 'accepted, False otherwise  https://stackoverflow.com/a/11553456
        font = m.bfonts.fontComboBox.currentFont().family()
        size = m.bfonts.spinBox.value()
        if askUser("Do you really want to set the fonts for \n" \
                    "ALL fields of ALL notes to the font: \n" \
                    + '    ' + str(font) + '\n' \
                    + 'and this size: \n' \
                    + '    ' + str(size)):
            for m in mw.col.models.all():
                for f in m['flds']:
                    f['font'] = font
                for f in m['flds']:
                    f['size'] = size
            mw.col.models.save(m)
            tooltip('Done')


batch_font_action = QAction("Batch change fonts on all fields all notes", mw)
batch_font_action.triggered.connect(batch_change_fonts_all_fields_all_notes)
mw.form.menuTools.addAction(batch_font_action) 



#change for all note types from menu
def batch_browser_change_fonts_all_fields_all_notes():
    m=Batch_Fonts_Dialog()
    m.setWindowTitle("Anki Set Fonts for all cards in BROWSER")
    #load current values into window
    try:
        m.bfonts.fontComboBox.setCurrentFont("Arial")
        m.bfonts.spinBox.setValue(fld['size'])
    except:
        pass
    if m.exec_():  # this is True if dialog is 'accepted, False otherwise  https://stackoverflow.com/a/11553456
        font = m.bfonts.fontComboBox.currentFont().family()
        size = m.bfonts.spinBox.value()
        if askUser("Do you really want to set the fonts for \n" \
                    "for all cards in BROWSER to the font: \n" \
                    + '    ' + str(font) + '\n' \
                    + 'and this size: \n' \
                    + '    ' + str(size)):
            for m in mw.col.models.all():
                for c in m['tmpls']:
                    c['bfont'] = font
                    c['bsize'] = size
            mw.col.models.save(m)
            tooltip('Done')
batch_browser_font_action = QAction("Batch change fonts for all cards in BROWSER", mw)
batch_browser_font_action.triggered.connect(batch_browser_change_fonts_all_fields_all_notes)
mw.form.menuTools.addAction(batch_browser_font_action)
