#!/usr/bin/env python
# -*- coding: utf-8 -*-
# filename: dockWidgets.py


import os, sys, re
from track import track

from PyQt6.QtCore import (
    QUrl,
    Qt,
    QVariant,
    QDir
)
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QMessageBox,
    QMenuBar,
    QFileDialog,
    QWidget,
    QVBoxLayout,
    QPlainTextEdit,
    QDockWidget,
    QToolBar,
    QLabel,
    QHBoxLayout,
    QLineEdit,
    QAbstractItemView,
    QTableView,
    QListView,
    QMenu,
    QInputDialog
)


from PyQt6.QtGui import (
    QIcon,
    QKeySequence,
    QPixmap,
    QAction,
    QTextCursor,
    QStandardItemModel,
    QStandardItem,
    QFileSystemModel
)
# from PyQt6.QtWidgets import *
# from PyQt6.QtCore import *
# from PyQt6.QtGui import *
from lrcShowX.lrcShowX import lrcShowX
from mutagen.flac import FLAC, Picture
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error
from pathlib import Path

basedir = Path(__file__).resolve().parent.as_posix()

class lrcShowxDock(QDockWidget):

    def __init__(self, title, parent = None):
        super().__init__(title)
        self.parent = parent
        self.lrcShowxWidget = lrcShowX(self)
        self.setWidget(self.lrcShowxWidget)
        self.setFloating(False)


class lrcEditorDock(QDockWidget):

    def __init__(self, title, parent = None):
        super().__init__(title)
        self.parent = parent
        self.setWindowTitle = title
        self.lrcEditorWidget = lrcEditorWidget(self)
        self.setWidget(self.lrcEditorWidget)
        self.setFloating(False)

class lrcEditorWidget(QWidget):

    def __init__(self, parent = None):
        super().__init__()
        self.parent = parent

        layout = QVBoxLayout(None)

        self.editLrc = QPlainTextEdit(self)
        self.editLrc.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)

        self.lrcFile = None

        self.initMenu()
        self.initToolBar()

        layout.addWidget(self.lrcEditMenu)
        layout.addWidget(self.toolBar)
        layout.addWidget(self.editLrc)

        self.setLayout(layout)

        self.newAction.triggered.connect(self.newAction_)
        self.openAction.triggered.connect(self.openAction_)
        self.saveAction.triggered.connect(self.saveAction_)
        self.saveAsAction.triggered.connect(self.saveAsAction_)

        self.editLrc.undoAvailable.connect(self.undoAction.setEnabled)
        self.editLrc.redoAvailable.connect(self.redoAction.setEnabled)
        self.editLrc.copyAvailable.connect(self.cutAction.setEnabled)
        self.editLrc.copyAvailable.connect(self.copyAction.setEnabled)

        self.undoAction.triggered.connect(self.editLrc.undo)
        self.redoAction.triggered.connect(self.editLrc.redo)
        self.cutAction.triggered.connect(self.editLrc.cut)
        self.copyAction.triggered.connect(self.editLrc.copy)
        self.pasteAction.triggered.connect(self.editLrc.paste)
        self.clearAction.triggered.connect(self.editLrc.clear)

        self.insertAction.triggered.connect(self.insertAction_)
        self.removeTagsAction.triggered.connect(self.removeTagsAction_)
        self.removeAllTagsAction.triggered.connect(self.removeAllTagsAction_)
        self.removeAllBlankLinesAction.triggered.connect(self.removeAllBlankLinesAction_)
        self.removeWhiteSpaceAction.triggered.connect(self.removeWhiteSpaceAction_)

    def initMenu(self):
        self.lrcEditMenu = QMenuBar(self)
        fileMenu = self.lrcEditMenu.addMenu(self.tr("File"))
        self.newAction = QAction(QIcon.fromTheme(QIcon.ThemeIcon.DocumentNew), self.tr("New"), self)
        self.openAction = QAction(QIcon.fromTheme(QIcon.ThemeIcon.DocumentOpen), self.tr("Open..."), self)
        self.saveAction = QAction(QIcon.fromTheme(QIcon.ThemeIcon.DocumentSave), self.tr("Save"), self)
        self.saveAsAction = QAction(QIcon.fromTheme(QIcon.ThemeIcon.DocumentSaveAs), self.tr('Save as...'), self)
        fileMenu.addAction(self.newAction)
        fileMenu.addAction(self.openAction)
        fileMenu.addAction(self.saveAction)
        fileMenu.addAction(self.saveAsAction)
        editMenu = self.lrcEditMenu.addMenu(self.tr("Edit"))
        self.undoAction = QAction(QIcon.fromTheme(QIcon.ThemeIcon.EditUndo), self.tr("Undo"), self)
        self.undoAction.setShortcut(QKeySequence("Ctrl+Z"))
        self.undoAction.setEnabled(False)
        self.redoAction = QAction(QIcon.fromTheme(QIcon.ThemeIcon.EditRedo), self.tr("Redo"), self)
        self.redoAction.setShortcut(QKeySequence("Ctrl+Shift+Z"))
        self.redoAction.setEnabled(False)
        self.cutAction = QAction(QIcon.fromTheme(QIcon.ThemeIcon.EditCut), self.tr("Cut"), self)
        self.cutAction.setEnabled(False)
        self.copyAction = QAction(QIcon.fromTheme(QIcon.ThemeIcon.EditCopy), self.tr("Copy"), self)
        self.copyAction.setShortcut(QKeySequence("Ctrl+C"))
        self.copyAction.setEnabled(False)
        self.pasteAction = QAction(QIcon.fromTheme(QIcon.ThemeIcon.EditPaste), self.tr("Paste"), self)
        self.pasteAction.setShortcut(QKeySequence("Ctrl+V"))
        self.pasteAction.setEnabled(self.editLrc.canPaste())
        self.clearAction = QAction(QIcon.fromTheme(QIcon.ThemeIcon.EditClear), self.tr("Clear"), self)
        editMenu.addAction(self.undoAction)
        editMenu.addAction(self.redoAction)
        editMenu.addSeparator()
        editMenu.addAction(self.cutAction)
        editMenu.addAction(self.copyAction)
        editMenu.addAction(self.pasteAction)
        editMenu.addSeparator()
        editMenu.addAction(self.clearAction)

        toolMenu = self.lrcEditMenu.addMenu(self.tr("Tool"))
        self.insertAction = QAction(self.tr("Insert a tag"), self)
        self.removeTagsAction = QAction(self.tr("Remove all tags in current line"), self)
        self.removeAllTagsAction = QAction(self.tr("Remove all tags"), self)
        self.removeAllBlankLinesAction = QAction(self.tr("Remove blank lines"), self)
        self.removeWhiteSpaceAction = QAction(self.tr("Remove whitespace character at start/end of lines"), self)
        toolMenu.addAction(self.insertAction)
        toolMenu.addAction(self.removeTagsAction)
        toolMenu.addAction(self.removeAllTagsAction)
        toolMenu.addAction(self.removeAllBlankLinesAction)
        toolMenu.addAction(self.removeWhiteSpaceAction)

    def initToolBar(self):
        self.toolBar = QToolBar(self)
        self.toolBar.addAction(self.insertAction)
        self.toolBar.addAction(self.removeTagsAction)

    def newAction_(self):
        self.editLrc.clear()
        self.editLrc.setPlainText("[ti:]\n[ar:]\n[al:]\n[by:]\n[offset: 0]\n\n")

    def openAction_(self):
        url, fil = QFileDialog.getOpenFileUrl(None, self.tr("choose a music file"), QUrl.fromLocalFile(self.parent.parent.parameter.lrcLocalPath), "lrc files (*.lrc)")
        if not url.isEmpty():
            with open(url.toLocalFile(), "r") as f:
                text = f.read()
            self.editLrc.setPlainText(text)
            self.lrcFile = url.toLocalFile()

    def saveAction_(self):
        if self.lrcFile:
            with open(self.lrcFile, "w") as f:
                f.write(self.editLrc.toPlainText())
        else:
            self.saveAsAction_()

    def saveAsAction_(self):
        f, r = QFileDialog.getSaveFileName(self, self.tr("Save as"), self.parent.parent.parameter.lrcLocalPath, "lrc files (*.lrc)")
        if f:
            self.lrcFile = f
            self.saveAction_()

    def insertAction_(self):
        m, ts = divmod(self.parent.parent.musicEngine.getPosition(), 60000)
        m = str(m).zfill(2)
        s = str(ts).zfill(5)[:2]
        ms = str(ts).zfill(5)[-3:]
        tag = f"[{m}:{s}.{ms}]"
        self.editLrc.moveCursor(QTextCursor.MoveOperation.StartOfLine)
        self.editLrc.textCursor().insertText(tag)
        self.editLrc.moveCursor(QTextCursor.MoveOperation.StartOfLine)
        self.editLrc.moveCursor(QTextCursor.MoveOperation.Down)

    def removeTagsAction_(self):
        self.editLrc.moveCursor(QTextCursor.MoveOperation.StartOfLine)
        self.editLrc.moveCursor(QTextCursor.MoveOperation.EndOfLine, QTextCursor.MoveMode.KeepAnchor)
        cursor = self.editLrc.textCursor()
        text = cursor.selectedText()
        newText = re.sub(r'\[\d\d:\d\d.*?\]', "", text)
        self.editLrc.cut()
        self.editLrc.insertPlainText(newText)

    def removeAllTagsAction_(self):
        text = self.editLrc.toPlainText()
        self.editLrc.clear()
        newText = re.sub(r'\[\d\d:\d\d.*?\]', "", text)
        self.editLrc.setPlainText(newText)

    def removeAllBlankLinesAction_(self):
        lines = self.editLrc.toPlainText().split("\n")
        self.editLrc.clear()
        newLines = list(filter(lambda x: x != "", lines))
        text = "\n".join(newLines)
        self.editLrc.setPlainText(text)

    def removeWhiteSpaceAction_(self):
        lines = self.editLrc.toPlainText().split("\n")
        self.editLrc.clear()
        newLines = list(map(lambda x: x.strip(), lines))
        text = "\n".join(newLines)
        self.editLrc.setPlainText(text)




class albumCoverDock(QDockWidget):

    def __init__(self, title, parent = None):
        super().__init__()
        self.setWindowTitle(title)
        self.parent = parent
        self.albumCoverWidget = albumCoverWidget(self)
        self.setWidget(self.albumCoverWidget)
        self.setFloating(False)




class albumCoverWidget(QLabel):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.setBlankCover()

        self.parent.parent.musicEngine.musicEquipment.playbackStateChanged.connect(self.schedule)

    def schedule(self, state):
        if state.value == 0:
            self.setBlankCover()
        elif state.value == 1:
            if self.parent.parent.currentTrack.trackType == "flac":
                self.searchMedia()
            else:
                self.searchOnline()
        else:
            pass

    def setBlankCover(self):
        pix = QPixmap(os.path.join(basedir, "icon/blankAlbum.png")).scaled(270, 270)
        self.setPixmap(pix)

    def searchMedia(self):
        f = self.parent.parent.currentTrack.trackFile
        
        if Path(f).suffix.lower() == ".mp3":
            audio = MP3(f, ID3=ID3)
            for tag in audio.tags.values():
                if isinstance(tag, APIC) and tag.type == 3:
                    pix = QPixmap()
                    pix.loadFromData(tag.data)
                    pix = pix.scaled(270, 270)
                    self.setPixmap(pix)
                else:
                    self.searchOnline()
        elif Path(f).suffix.lower() == ".flac":  
            audio = FLAC(f)
            if audio.pictures:
                p = audio.pictures[0]
                pix = QPixmap()
                pix.loadFromData(p.data)
                pix = pix.scaled(270, 270)
                self.setPixmap(pix)
            else:
                self.searchOnline()

    def searchOnline(self):
        pass



class playlistDock(QDockWidget):

    def __init__(self, title, parent = None):
        super().__init__(title)
        self.parent = parent
        self.playlistWidget = playlistWidget(self)
        self.setWidget(self.playlistWidget)
        self.setFloating(False)


class playlistWidget(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        self.initToolBar()

        searchLayout = QHBoxLayout(None)
        self.searchLabel = QLabel(self.tr("Search:"))
        self.searchLine = QLineEdit(self)
        self.searchLine.setClearButtonEnabled(True)

        self.searchLine.textChanged.connect(self.filtItems)

        searchLayout.addWidget(self.searchLabel)
        searchLayout.addWidget(self.searchLine)

        self.playlistTable = QTableView(self)
        self.playlistTable.setEditTriggers(QAbstractItemView.EditTrigger.SelectedClicked)
        self.playlistTable.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        #self.playlistTable.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.headers = [self.tr("Title"), self.tr("Artist"), self.tr("Length"), self.tr("Album"), self.tr("Type"), self.tr("Date"), self.tr("Bit rate"), self.tr("Sample rate"), self.tr("File")]

        self.model = QStandardItemModel(0, 8)  # 0 rows, 1 column

        self.model.setHorizontalHeaderLabels(self.headers)
        self.playlistTable.setModel(self.model)

        self.nameLabel = QLabel(self)
        self.updateNameLabel()

        toolLayout = QHBoxLayout(None)
        toolLayout.addWidget(self.toolBar)
        toolLayout.addStretch(0)
        toolLayout.addWidget(self.nameLabel)

        mainLayout = QVBoxLayout(None)

        mainLayout.addLayout(searchLayout)
        mainLayout.addLayout(toolLayout)
        mainLayout.addWidget(self.playlistTable)

        self.setLayout(mainLayout)

        self.clearTrackAction.triggered.connect(self.clearTrackAction_)
        self.playlistTable.activated.connect(self.enableThePlayButton)
        self.removeTrackAction.triggered.connect(self.removeTrackAction_)
        self.addTrackAction.triggered.connect(self.addTrackAction_)
        self.savePlaylistAction.triggered.connect(self.savePlaylistAction_)
        self.saveasPlayListAction.triggered.connect(self.saveasPlayListAction_)
        self.loadPlaylistAction.triggered.connect(self.loadPlaylistAction_)

        self.model.itemChanged.connect(self.itemTagChange)

    def itemTagChange(self, m):
        col = m.column()
        v = m.text()
        f = self.model.item(m.row(), 8).text()
        au = track(f)
        if col == 0:
            au.setTitleTag(v)
        elif col == 1:
            au.setArtistTag(v)
        elif col == 3:
            au.setAlbumTag(v)
        elif col == 5:
            au.setDateTag(v)


    def filtItems(self, t):
        if t == "":
            self.loadItems(self.parent.parent.playlistTmp)
        else:
            l0 = self.model.match(self.model.index(0, 0), Qt.ItemDataRole.DisplayRole, QVariant(t), -1, Qt.MatchFlag.MatchContains)
            l1 = self.model.match(self.model.index(0, 1), Qt.ItemDataRole.DisplayRole, QVariant(t), -1, Qt.MatchFlag.MatchContains)
            l3 = self.model.match(self.model.index(0, 3), Qt.ItemDataRole.DisplayRole, QVariant(t), -1, Qt.MatchFlag.MatchContains)
            l = list(set(l0 + l1 + l3))
            # l = self.model.findItems(t, Qt.MatchFlag.MatchContains)
            rowList = list(set((map(lambda x: x.row(), l))))
            tl = []
            for i in rowList:
                tl.append(self.parent.parent.playlistTmp[i])
            self.loadItems(tl, False, False)

    def loadItems(self, trackList, append = False, updatePlaylistTmp = True):
        self.model.clear()
        self.model.setHorizontalHeaderLabels(self.headers)
        try:
            self.playlistTable.horizontalHeader().restoreState(self.parent.parent.parameter.playlistDockPlaylistTableState)
        except:
            pass
        self.operateModel(trackList, append, updatePlaylistTmp)

    def appendItems(self, newList):
        newItems = list(set(newList) - set(self.parent.parent.playlistTmp))
        self.operateModel(newItems, True)

    def operateModel(self, trackList, append = False, updatePlaylistTmp = True):
        self.model.itemChanged.disconnect(self.itemTagChange)
        if append:
            row = len(self.parent.parent.playlistTmp)
        else:
            row = 0
        for i in trackList:
            if not i.strip():
                continue
            try:
                au = track(i.strip())
            except:
                continue
            itemTitle = QStandardItem(au.trackTitle)
            itemTitle.setEditable(True)
            self.model.setItem(row, 0, itemTitle)
            itemArtist = QStandardItem(au.trackArtist)
            itemArtist.setEditable(True)
            self.model.setItem(row, 1, itemArtist)
            itemLength = QStandardItem(self.formatTrackLength(au.trackLength))
            itemLength.setEditable(False)
            self.model.setItem(row, 2, itemLength)
            itemAlbum = QStandardItem(au.trackAlbum)
            itemAlbum.setEditable(True)
            self.model.setItem(row, 3, itemAlbum)
            itemType = QStandardItem(au.trackType)
            itemType.setEditable(False)
            self.model.setItem(row, 4, itemType)
            itemDate = QStandardItem(au.trackDate)
            itemDate.setEditable(True)
            self.model.setItem(row, 5, itemDate)
            itemBitrate = QStandardItem(str(au.trackBitrate))
            itemBitrate.setEditable(False)
            self.model.setItem(row, 6, itemBitrate)
            itemSamplerage = QStandardItem(str(au.trackSamplerate))
            itemSamplerage.setEditable(False)
            self.model.setItem(row, 7, itemSamplerage)
            itemFile = QStandardItem(au.trackFile)
            itemFile.setEditable(False)
            self.model.setItem(row, 8, itemFile)
            row += 1
        self.playlistTable.setModel(self.model)
        if updatePlaylistTmp:
            if append:
                self.parent.parent.playlistTmp += trackList
            else:
                self.parent.parent.playlistTmp = trackList
        self.model.itemChanged.connect(self.itemTagChange)


    def initToolBar(self):
        self.toolBar = QToolBar(self)
        self.loadPlaylistAction = QAction(self.tr("Load playlist"), self)
        self.savePlaylistAction = QAction(self.tr("Save"))
        self.saveasPlayListAction = QAction(self.tr("Save as..."))
        self.addTrackAction = QAction(self.tr("Add..."), self)
        self.removeTrackAction = QAction(self.tr("Remove"))
        self.clearTrackAction = QAction(self.tr("Clear"))
        self.toolBar.addAction(self.loadPlaylistAction)
        self.toolBar.addAction(self.savePlaylistAction)
        self.toolBar.addAction(self.saveasPlayListAction)
        self.toolBar.addAction(self.addTrackAction)
        self.toolBar.addAction(self.removeTrackAction)
        self.toolBar.addAction(self.clearTrackAction)

    def clearTrackAction_(self):
        self.loadItems([])

    def removeTrackAction_(self):
        indexList = self.playlistTable.selectedIndexes()
        fileList = []
        for i in indexList:
            f = self.model.item(i.row(), 8).text()
            fileList.append(f)
        l = list(set(self.parent.parent.playlistTmp) - set(fileList))
        self.loadItems(l)

    def addTrackAction_(self):
        urlList, fi = QFileDialog.getOpenFileNames(self, self.tr("Add tracks"), self.parent.parent.parameter.collectionPath, "Media files (*.mp3 *.flac *.ogg *.m4a)")
        self.appendItems(urlList)

    def savePlaylistAction_(self):
        if self.parent.parent.parameter.currentPlaylistName:
            t = "\n".join(self.parent.parent.playlistTmp) + "\n"
            with open(self.parent.parent.parameter.currentPlaylistName, "w", encoding="utf-8") as f:
                f.write(t)
        else:
            self.saveasPlayListAction_()

    def saveasPlayListAction_(self):
        f, r = QFileDialog.getSaveFileName(self, self.tr("Save as"), self.parent.parent.parameter.privatePath, "plain text files (*.txt)")
        if f:
            self.parent.parent.parameter.currentPlaylistName = f
            self.savePlaylistAction_()
            self.updateNameLabel()

    def loadPlaylistAction_(self):
        f, r = QFileDialog.getOpenFileName(self, self.tr("Select a playlist"), self.parent.parent.parameter.privatePath, "plain text files (*.txt)")
        if f:

            with open(f, "r") as ff:
                pl = ff.readlines()
            pl = list(map(lambda x: x.strip(), pl))
            pl = list(filter(lambda x: os.path.exists(x), pl))
            self.loadItems(pl, False, True)
            self.parent.parent.parameter.currentPlaylistName = f
            self.updateNameLabel()

    def updateNameLabel(self):
        if self.parent.parent.parameter.currentPlaylistName:
            self.nameLabel.setText(self.parent.parent.parameter.currentPlaylistName)
        else:
            self.nameLabel.setText(self.tr("Unamed playlist"))


    def enableThePlayButton(self, ind):
        if self.parent.parent.musicEngine.getPlaybackState().value == 0:
            self.parent.parent.playorpauseAction.setEnabled(True)
            self.parent.parent.centralWidget.playorpauseButton.setEnabled(True)
            self.parent.parent.currentIndex = ind.row()
            self.parent.parent.currentTrack = track(self.model.item(ind.row(), 8).text())


    def formatTrackLength(self, t):
        m, s = divmod(t, 60)
        if s < 10:
            return f"{m}:0{s}"
        else:
            return f"{m}:{s}"
#########################################################################################


class collectionDock(QDockWidget):

    def __init__(self, title, parent = None):
        super().__init__(title)
        self.parent = parent
        self.setWindowTitle = title
        self.collectionWidget = collectionWidget(self)
        self.setWidget(self.collectionWidget)
        self.setFloating(False)

class collectionWidget(QWidget):

    def __init__(self, parent = None):
        super().__init__()
        self.parent = parent

        self.collectionView = collectionView(self)

        di = QDir(self.parent.parent.parameter.collectionPath, "Media files (*.ogg *.mp3 *.flac *.m4a)")
        layout = QVBoxLayout(None)

        self.model = QFileSystemModel()
        self.model.setNameFilters(["*.ogg", "*.mp3", "*.flac", "*.m4a"])
        self.model.setNameFilterDisables(False)
        self.model.setRootPath(di.path())
        self.collectionView.setModel(self.model)
        self.collectionView.setRootIndex(self.model.index(di.path()))
        layout.addWidget(self.collectionView)
        self.setLayout(layout)

    def updateList(self):
        self.collectionView.reset()
        self.updateModel()

    def updateModel(self):
        di = QDir(self.parent.parent.parameter.collectionPath, "Media files (*.ogg)")
        self.model.setRootPath(di.path())

        self.collectionView.setModel(self.model)
        self.collectionView.setRootIndex(self.model.index(di.path()))



class collectionView(QListView):

    def __init__(self, parent = None):
        super().__init__()
        self.parent = parent
        #self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        self.initContextMenu()

        self.addToPlaylistAction.triggered.connect(self.addToPlaylistAction_)
        self.delFileAction.triggered.connect(self.delFileAction_)
        self.renameAction.triggered.connect(self.renameAction_)

    def initContextMenu(self):
        self.contextMenu = QMenu(self)
        self.addToPlaylistAction = QAction(self.tr("add to playlist"), self)
        self.addToPlaylistAction.setEnabled(False)
        self.contextMenu.addAction(self.addToPlaylistAction)
        self.contextMenu.addSeparator()
        self.delFileAction = QAction(self.tr("Del file..."), self)
        self.delFileAction.setEnabled(False)
        self.renameAction = QAction(self.tr("Rename..."), self)
        self.renameAction.setEnabled(False)
        self.contextMenu.addAction(self.delFileAction)
        self.contextMenu.addAction(self.renameAction)

    def renameAction_(self):
        oldName = self.selectedIndexes()[0].data()
        newName, ok = QInputDialog.getText(self, "Input new name", "New file name:", QLineEdit.EchoMode.Normal, oldName)
        if ok:
            root = self.model().rootPath()
            try:
                os.rename(os.path.join(root, oldName), os.path.join(root, newName))
            except:
                QMessageBox.information(self, self.tr("Information:"), self.tr("Rename failed, please check the input characters"))


    def delFileAction_(self):
        b = QMessageBox.warning(self, self.tr("Important:"), self.tr("You are deleting the selected tracks from disk\nAre you sure?"), QMessageBox.StandardButton.Yes, QMessageBox.StandardButton.No)
        if b.value == 16384:
            root = self.model().rootPath()
            for i in self.selectedIndexes():
                self.parent.model.remove(i)


    def contextMenuEvent(self, ev):
        n = len(self.selectedIndexes())
        if n != 0:
            self.addToPlaylistAction.setEnabled(True)
            self.delFileAction.setEnabled(True)
        else:
            self.addToPlaylistAction.setEnabled(False)
            self.delFileAction.setEnabled(False)
        if n == 1:
            self.renameAction.setEnabled(True)
        else:
            self.renameAction.setEnabled(False)
        self.contextMenu.popup(self.mapToGlobal(ev.pos()))

    def addToPlaylistAction_(self):
        root = self.model().rootPath()
        mediaList = []
        for i in self.selectedIndexes():
            mediaList.append(os.path.join(root, i.data()))
        self.parent.parent.parent.appendToPlaylist(mediaList)



if __name__ == "__main__":

    app = QApplication(sys.argv)
    w = albumCoverDock("Album cover")
    w.show()

    sys.exit(app.exec())



