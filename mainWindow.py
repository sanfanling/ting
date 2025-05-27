#!/usr/bin/env python
# -*- coding: utf-8 -*-
# filename: mainWindow.py


import os, sys, glob, mutagen, random
import traceback

from PyQt6.QtCore import (
    QTimer,
    QUrl,
    QObject,
    pyqtSignal,
    QRunnable,
    pyqtSlot,
    QThreadPool
    
)
from PyQt6.QtWidgets import (
    QApplication,
    QSystemTrayIcon,
    QFileDialog,
    QMessageBox
    
)
from PyQt6.QtGui import (
    QIcon,
    QKeySequence,
    QPixmap,
    QFont  
)

from dockWidgets import albumCoverWidget

# from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput, QMediaMetaData, QMediaDevices
from pathlib import Path
from configuration import configuration
from windowUI import windowUI
from engine import engine


from track import track

base_dir = Path(__file__).resolve().parent.as_posix()

class WorkerSignals(QObject):
    """Signals from a running worker thread.

    finished
        No data

    error
        tuple (exctype, value, traceback.format_exc())

    result
        object data returned from processing, anything

    progress
        float indicating % progress
    """

    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(float)

class Worker(QRunnable):
    """Worker thread.

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread.
                     Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function
    """

    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        # Add the callback to our kwargs
        # self.kwargs["progress_callback"] = self.signals.progress

    @pyqtSlot()
    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
        except Exception:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()

class mainWindow(windowUI):

    def __init__(self, devices):
        super().__init__(devices)

        self.threadpool = QThreadPool()
        self.setWindowTitle("xting")
        self.setWindowIcon(QIcon(Path(os.path.join(base_dir, "icon/logo.png")).as_posix()))
        self.timer = QTimer()

        self.musicEngine = engine()
        self.playHistory = []
        self.addToPlayHistory = True
        self.currentTrack = None
        self.virtualStop = True
        self.currentIndex = 0

        self.initCentralWidget()
        self.initDockwidget()
        self.initMenuBar()
        self.initStatusBar()

        self.setShortcuts()

        path = Path(os.path.join(self.parameter.privatePath, "current.txt")).as_posix()
        if not self.parameter.currentPlaylistName:
            path = Path(os.path.join(self.parameter.privatePath, "current.txt")).as_posix()
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                # self.threadpool.start(worker)
                    self.playlistTmp = list(map(lambda x: x.strip(), f.readlines()))
                    self.playlistTmp = list(filter(lambda x: os.path.exists(x), self.playlistTmp))
                self.addToPlaylist(self.playlistTmp)
            else:
                self.playlistTmp = []
        else:
            # self.threadpool.start(worker)
            try:
                with open(self.parameter.currentPlaylistName, "r", encoding="utf-8") as f:
                    self.playlistTmp = list(map(lambda x: x.strip(), f.readlines()))
                    self.playlistTmp = list(filter(lambda x: os.path.exists(x), self.playlistTmp))
                self.addToPlaylist(self.playlistTmp)
            except FileNotFoundError:
                open(self.parameter.currentPlaylistName, "x").close()
        self.systemTray = QSystemTrayIcon(QIcon(Path(os.path.join(base_dir, "icon/logo.png")).as_posix()), self)
        self.systemTray.setContextMenu(self.trayContextMenu)
        self.systemTray.setVisible(self.parameter.trayIcon)

        if self.parameter.loop == "playlist":
            self.loopPlaylistAction.setChecked(True)
        elif self.parameter.loop == "track":
            self.loopTrackAction.setChecked(True)
        else:
            self.noLoopAction.setChecked(True)

        if self.parameter.sequence == "order":
            self.sequenceOrderAction.setChecked(True)
        elif self.parameter.sequence == "random":
            self.sequenceRandomAction.setChecked(True)
        else:
            self.sequenceReverseOrderAction.setChecked(True)



        k = 0
        for de in self.devices:
            if de.description() == self.musicEngine.audioOutput.device().description():
                break
            else:
                k += 1
        try:
            exec(f"self.device{k}Action.setChecked(True)")
        except AttributeError:
            pass
        self.musicEngine.setVolume(0.8)
        self.centralWidget.volumeSlider.setValue(8)



        self.openFileAction.triggered.connect(self.openFileAction_)
        self.centralWidget.playorpauseButton.clicked.connect(self.playorpause_)
        self.playorpauseAction.triggered.connect(self.playorpause_)
        self.centralWidget.stopButton.clicked.connect(self.stop_)
        self.stopAction.triggered.connect(self.stop_)
        self.centralWidget.previousButton.clicked.connect(self.previous_)
        self.previousAction.triggered.connect(self.previous_)
        self.centralWidget.nextButton.clicked.connect(self.next_)
        self.nextAction.triggered.connect(self.next_)
        self.repeatAction.triggered.connect(self.repeat_)
        self.centralWidget.repeatButton.clicked.connect(self.repeat_)
        self.configurationAction.triggered.connect(self.configurationAction_)

        for q in self.deviceGroup.actions():
            exec(f"q.triggered.connect(self.changeDevice)")

        self.restoreWidgetState()


        self.timer.timeout.connect(self.progressForward)

        self.centralWidget.progressSlider.valueChanged.connect(self.adjustTrackPosition)

        self.centralWidget.volumeSlider.valueChanged.connect(self.volumeSlider_)

        self.systemTray.activated.connect(self.showorhideTray_)

        self.playlistDock.playlistWidget.playlistTable.doubleClicked.connect(self.playByDoubleClick)

        self.musicEngine.musicEquipment.playbackStateChanged.connect(self.playbackStateChanged_)

        self.loopTrackAction.toggled.connect(self.changeLoop)
        self.loopPlaylistAction.toggled.connect(self.changeLoop)
        self.noLoopAction.toggled.connect(self.changeLoop)
        self.sequenceOrderAction.toggled.connect(self.changeSequence)
        self.sequenceReverseOrderAction.toggled.connect(self.changeSequence)
        self.sequenceRandomAction.toggled.connect(self.changeSequence)

        self.aboutAppAction.triggered.connect(self.aboutAppAction_)
        self.aboutQtAction.triggered.connect(QApplication.aboutQt)
        self.quitAction.triggered.connect(self.quit_)

    def addFileAlbum(self, file: str):
        album = albumCoverWidget(self)
        
        


        

    def restoreWidgetState(self):
        try:
            self.lrcShowxDock.restoreGeometry(self.parameter.lrcShowxDockGeometry)
        except:
            pass
        try:
            self.playlistDock.restoreGeometry(self.parameter.lrcShowxDockGeometry)
        except:
            pass
        try:
            self.albumCoverDock.restoreGeometry(self.parameter.lrcShowxDockGeometry)
        except:
            pass
        try:
            self.lrcEditorDock.restoreGeometry(self.parameter.lrcEditorDockGeometry)
        except:
            pass
        try:
            self.restoreState(self.parameter.windowState)
        except:
            pass
        try:
            self.restoreGeometry(self.parameter.windowGeometry)
        except:
            pass
        try:
            self.playlistDock.playlistWidget.playlistTable.horizontalHeader().restoreState(self.parameter.playlistDockPlaylistTableState)
        except:
            pass


    def addToPlaylist(self, fileList):
        self.playlistDock.playlistWidget.loadItems(fileList)

    def appendToPlaylist(self, fileList):
        self.playlistDock.playlistWidget.appendItems(fileList)

    def setButtonStatus(self, status = None):
        if len(self.playHistory) !=  0:
            self.previousAction.setEnabled(True)
            self.centralWidget.previousButton.setEnabled(True)
        else:
            self.previousAction.setEnabled(False)
            self.centralWidget.previousButton.setEnabled(False)

        if status == 0:
            self.playorpauseAction.setEnabled(True)
            self.playorpauseAction.setText(self.tr("Play"))
            self.centralWidget.playorpauseButton.setEnabled(True)
            self.centralWidget.playorpauseButton.setIcon(QIcon(os.path.join(base_dir, "icon/play.png")))
            self.stopAction.setEnabled(False)
            self.centralWidget.stopButton.setEnabled(False)
            self.previousAction.setEnabled(False)
            self.centralWidget.previousButton.setEnabled(False)
            self.nextAction.setEnabled(False)
            self.centralWidget.nextButton.setEnabled(False)
            self.repeatAction.setEnabled(False)
            self.centralWidget.repeatButton.setEnabled(False)
            self.centralWidget.progressSlider.setValue(0)
            self.centralWidget.progressSlider.setEnabled(False)
            self.centralWidget.lengthLabel.setText("--:--")
            self.centralWidget.timeLabel.setText("--:--")

        elif status == 1:
            self.playorpauseAction.setText(self.tr("Pause"))
            self.centralWidget.playorpauseButton.setIcon(QIcon(os.path.join(base_dir, "icon/pause.png")))
            self.playorpauseAction.setEnabled(True)
            self.centralWidget.playorpauseButton.setEnabled(True)
            self.stopAction.setEnabled(True)
            self.centralWidget.stopButton.setEnabled(True)
            self.centralWidget.nextButton.setEnabled(True)
            self.nextAction.setEnabled(True)
            self.centralWidget.repeatButton.setEnabled(True)
            self.repeatAction.setEnabled(True)

        elif status == 2:
            self.playorpauseAction.setText(self.tr("Play"))
            self.centralWidget.playorpauseButton.setIcon(QIcon(os.path.join(base_dir, "icon/play.png")))

    def addHistoryAction(self):
        if self.addToPlayHistory:
            try:
                a = self.playHistory[-1]
            except:
                self.playHistory.append(self.currentTrack.trackFile)
            else:
                if a != self.currentTrack.trackFile:
                    self.playHistory.append(self.currentTrack.trackFile)


    def playbackStateChanged_(self, status):

        if status.value == 0: # stoped status
            self.addHistoryAction()

            self.timer.stop()
            if self.virtualStop:   # True: handle track to track automatically, feel like playing by playing without stop, it's default
                self.scheduleNextTrack()
            else:                  # False: handle real stop, happens end of playlist, user click stop button etc
                self.afterStop()
        elif status.value == 1: # playing status
            self.setButtonStatus(1)
            self.showTrayInformation(1)
        elif status.value == 2: # paused status
            self.setButtonStatus(2)
            self.showTrayInformation(2)

    def afterStop(self):
        self.virtualStop = True
        self.setButtonStatus(0)
        self.showTrayInformation(0)

    def scheduleNextTrack(self):
        if not self.addToPlayHistory:   # command comes from previous button
            pf = self.playHistory[-1]
            try:
                self.playHistory = self.playHistory[:-1]
            except:
                self.playHistory = []
            self.currentIndex = self.getNumberFromFile(pf)
            self.currentTrack = track(pf)
            self.playlistDock.playlistWidget.playlistTable.selectRow(self.currentIndex)
            self.actualPlayOrPause()
            return

        if self.loopTrackAction.isChecked():
            self.playlistDock.playlistWidget.playlistTable.selectRow(self.currentIndex)
            self.actualPlayOrPause(True)
            return

        if self.sequenceRandomAction.isChecked():
            tr = self.playlistDock.playlistWidget.model.rowCount()
            ind = random.randint(0, tr - 1)
            url = self.playlistDock.playlistWidget.model.item(ind, 8).text()
            self.currentIndex = ind
            self.currentTrack = track(url)
            self.playlistDock.playlistWidget.playlistTable.selectRow(ind)
            self.actualPlayOrPause(True)
            return

        if self.sequenceOrderAction.isChecked():
            if self.currentIndex + 1 >= self.playlistDock.playlistWidget.model.rowCount():
                if self.noLoopAction.isChecked():
                    self.afterStop()
                elif self.loopPlaylistAction.isChecked():
                    self.currentIndex = 0
                    self.currentTrack = track(self.playlistDock.playlistWidget.model.item(self.currentIndex, 8).text())
                    self.playlistDock.playlistWidget.playlistTable.selectRow(self.currentIndex)
                    self.actualPlayOrPause(True)
            else:
                self.currentIndex += 1
                self.currentTrack = track(self.playlistDock.playlistWidget.model.item(self.currentIndex, 8).text())
                self.playlistDock.playlistWidget.playlistTable.selectRow(self.currentIndex)
                self.actualPlayOrPause(True)
            return

        if self.sequenceReverseOrderAction.isChecked():

            if self.currentIndex - 1 < 0:
                if self.noLoopAction.isChecked():
                    self.afterStop()
                elif self.loopPlaylistAction.isChecked():
                    self.currentIndex = self.playlistDock.playlistWidget.model.rowCount() - 1
                    self.currentTrack = track(self.playlistDock.playlistWidget.model.item(self.currentIndex, 8).text())
                    self.playlistDock.playlistWidget.playlistTable.selectRow(self.currentIndex)
                    self.actualPlayOrPause(True)
            else:
                self.currentIndex -= 1
                self.currentTrack = track(self.playlistDock.playlistWidget.model.item(self.currentIndex, 8).text())
                self.playlistDock.playlistWidget.playlistTable.selectRow(self.currentIndex)
                self.actualPlayOrPause(True)
            return

    def showTrayInformation(self, v):
        if self.parameter.trayIcon and self.parameter.trayInfo:
            if v == 1:
                self.systemTray.showMessage(self.tr("Status changed"), f"Now playing: {self.currentTrack.trackTitle} by {self.currentTrack.trackArtist}", QIcon(Path(os.path.join(base_dir, "icon/logo.png")).as_posix()), 6000)
            elif v == 2:
                self.systemTray.showMessage(self.tr("Status changed"), f"Paused: {self.currentTrack.trackTitle} by {self.currentTrack.trackArtist}", QIcon(Path(os.path.join(base_dir, "icon/logo.png")).as_posix()), 6000)
            else:
                self.systemTray.showMessage(self.tr("Status changed"), "Stopped", QIcon(Path(os.path.join(base_dir, "icon/logo.png")).as_posix()), 6000)

    def openFileAction_(self):
        url, fil = QFileDialog.getOpenFileUrl(None, self.tr("choose a music file"), QUrl.fromLocalFile(self.parameter.collectionPath), "music files (*.mp3 *.flac *.ogg *.m4a)")
        if not url.isEmpty():
            self.currentTrack = track(url.toLocalFile())
            self.addToPlaylist([self.currentTrack.trackFile])
            self.currentIndex = 0
            self.playlistDock.playlistWidget.playlistTable.selectRow(0)
            self.actualPlayOrPause(True)

    def getNumberFromFile(self, f):
        for i in range(0, self.playlistDock.playlistWidget.model.rowCount()):
            if f == self.playlistDock.playlistWidget.model.item(i, 8).text():
                break
        return i

    def playByDoubleClick(self, ind):
        self.virtualStop = False
        url = self.playlistDock.playlistWidget.model.item(ind.row(), 8).text()
        self.currentIndex = ind.row()
        self.currentTrack = track(url)
        self.actualPlayOrPause()
        self.virtualStop = True

    def next_(self):
        self.virtualStop = True
        self.musicEngine.stop()

    def previous_(self):
        self.addToPlayHistory = False
        self.next_()
        self.addToPlayHistory = True

    def playorpause_(self):
        if self.musicEngine.getPlaybackState().value == 0:
            self.actualPlayOrPause(True)
        else:
            self.actualPlayOrPause(False)


    def actualPlayOrPause(self, newTrack = True):
        if self.musicEngine.isPlaying() and (not newTrack):
            self.timer.stop()
            self.musicEngine.pause()
        else:
            self.beforePlayorpause(newTrack)

    def beforePlayorpause(self, newTrack):
        if newTrack:
            self.musicEngine.add(self.currentTrack.trackFile)
        t = self.currentTrack.trackLength
        self.centralWidget.progressSlider.setEnabled(True)
        self.centralWidget.progressSlider.setRange(0, t * 1000)
        self.timer.start(1000)
        self.centralWidget.lengthLabel.setText(self.formatTrackLength(t))
        self.centralWidget.progressSlider.setValue(self.musicEngine.getPosition())
        self.centralWidget.timeLabel.setText(self.formatTrackLength(self.musicEngine.getPosition()))
        
        worker = Worker(
            self.albumCoverDock.albumCoverWidget.searchMedia
        )
        self.threadpool.start(worker)
        # self.albumCoverDock.albumCoverWidget.searchMedia()
        self.musicEngine.play()


    def stop_(self):
        self.virtualStop = False
        self.musicEngine.stop()

    def repeat_(self):
        self.stop_()
        self.actualPlayOrPause(True)
        self.virtualStop = True

    def volumeSlider_(self, v):
        self.musicEngine.setVolume(v / 10)

    def progressForward(self):
        v = self.centralWidget.progressSlider.value()
        self.centralWidget.progressSlider.setValue(v + 1000)
        self.centralWidget.timeLabel.setText(self.formatTrackLength(int(v / 1000)))

    def adjustTrackPosition(self, v):
        if abs(v - self.musicEngine.getPosition()) < 1000 or v == 0:
            pass
        else:
            self.timer.stop()
            v = self.centralWidget.progressSlider.value()
            self.musicEngine.setPosition(v)
            self.timer.start(1000)
            self.positionChanged.emit()

    def showorhideTray_(self, r):
        if r.value == 3:
            if self.isHidden():
                self.show()
            else:
                self.hide()

    def changeLoop(self, b):
        if b:
            self.parameter.loop = self.sender().iconText().lower()

    def changeSequence(self, b):
        if b:
            self.parameter.sequence = self.sender().iconText().lower()

    def changeDevice(self):
        deviceId = self.sender().objectName()
        self.musicEngine.setDevice(self.devices[int(deviceId)])


    def formatTrackLength(self, t):
        m, s = divmod(t, 60)
        if s < 10:
            return f"{m}:0{s}"
        else:
            return f"{m}:{s}"

    def aboutAppAction_(self):
        b = QMessageBox(self)
        b.setIconPixmap(QPixmap(Path(os.path.join(base_dir, "icon/logo.png")).as_posix()))
        b.setWindowTitle(self.tr(f'About {QApplication.arguments()[0]}'))
        b.setText(f'Application: {QApplication.arguments()[0]}\n\nVersion: {QApplication.arguments()[1]}\n\nShort description: xting is a personal local music application, not special. Synced lyrics display is interesting\n\nAuthors: {QApplication.arguments()[2]}\n\nLicense: {QApplication.arguments()[3]}\n\nWebsite: {QApplication.arguments()[4]}')
        b.exec()

    def configurationAction_(self):
        settingDialog = configuration(self)
        settingDialog.playerConfig.playerPathBox.cpLine.setText(self.parameter.collectionPath)
        settingDialog.playerConfig.playerTrayBox.trayIcon.setChecked(self.parameter.trayIcon)
        settingDialog.playerConfig.playerTrayBox.trayIcon_(self.parameter.trayIcon)
        settingDialog.playerConfig.playerTrayBox.closeNotQuit.setChecked(self.parameter.closeNotQuit)
        settingDialog.playerConfig.playerTrayBox.trayInfo.setChecked(self.parameter.trayInfo)

        settingDialog.lrcShowxConfig.appearenceBox.tlLine.setValue(self.parameter.topMarginLines)
        settingDialog.lrcShowxConfig.appearenceBox.lmLine.setValue(self.parameter.lineMargin)

        settingDialog.lrcShowxConfig.appearenceBox.bgEffectLabel.setStyleSheet("QLabel { background-color: " + self.parameter.backGroundColor + "; color: white; }")
        settingDialog.lrcShowxConfig.appearenceBox.fgEffectLabel.setStyleSheet("QLabel { background-color: " + self.parameter.foreGroundColor + "; color: white; }")
        settingDialog.lrcShowxConfig.appearenceBox.hlEffectLabel.setStyleSheet("QLabel { background-color: " + self.parameter.highLightColor + "; color: white; }")
        ff = QFont()
        ff.fromString(self.parameter.lrcFont)
        settingDialog.lrcShowxConfig.appearenceBox.fontEffectLabel.setFont(ff)

        settingDialog.lrcShowxConfig.lrcPathBox.llLine.setText(self.parameter.lrcLocalPath)
        settingDialog.lrcShowxConfig.lrcPathBox.auto.setChecked(self.parameter.autoSaveLrc)
        r = settingDialog.exec()
        if r == 1:  # accepted

            self.parameter.trayIcon = settingDialog.playerConfig.playerTrayBox.trayIcon.isChecked()
            self.systemTray.setVisible(self.parameter.trayIcon)
            self.parameter.closeNotQuit = settingDialog.playerConfig.playerTrayBox.closeNotQuit.isChecked()
            self.parameter.trayInfo = settingDialog.playerConfig.playerTrayBox.trayInfo.isChecked()

            self.parameter.lrcLocalPath = self.lrcShowxDock.lrcShowxWidget.lrcLocalPath = settingDialog.lrcShowxConfig.lrcPathBox.llLine.text()
            self.parameter.autoSaveLrc = self.lrcShowxDock.lrcShowxWidget.autoSaveLrc = settingDialog.lrcShowxConfig.lrcPathBox.auto.isChecked()

            self.parameter.playorpauseActionShortcut = settingDialog.shortcutsConfig.playerShortcutsBox.playorpauseActionShortcut.keySequence()
            self.parameter.stopActionShortcut = settingDialog.shortcutsConfig.playerShortcutsBox.stopActionShortcut.keySequence()
            self.parameter.nextActionShortcut = settingDialog.shortcutsConfig.playerShortcutsBox.nextActionShortcut.keySequence()
            self.parameter.previousActionShortcut = settingDialog.shortcutsConfig.playerShortcutsBox.previousActionShortcut.keySequence()
            self.parameter.repeatActionShortcut = settingDialog.shortcutsConfig.playerShortcutsBox.repeatActionShortcut.keySequence()
            self.parameter.closeLrcShortcut = settingDialog.shortcutsConfig.lrcShowxShortcutsBox.closeLrcShortcut.keySequence()
            self.parameter.offsetForwardShortcut = settingDialog.shortcutsConfig.lrcShowxShortcutsBox.offsetForwardShortcut.keySequence()
            self.parameter.offsetBackwardShortcut = settingDialog.shortcutsConfig.lrcShowxShortcutsBox.offsetBackwardShortcut.keySequence()
            self.parameter.reloadLrcShortcut = settingDialog.shortcutsConfig.lrcShowxShortcutsBox.reloadLrcShortcut.keySequence()
            self.parameter.insertTagShortcut =settingDialog.shortcutsConfig.lrcEditorShortcutsBox.insertTagShortcut.keySequence()
            self.setShortcuts()

            if self.parameter.collectionPath != settingDialog.playerConfig.playerPathBox.cpLine.text():
                self.parameter.collectionPath = settingDialog.playerConfig.playerPathBox.cpLine.text()
                self.collectionDock.collectionWidget.updateList()

            if self.parameter.topMarginLines != settingDialog.lrcShowxConfig.appearenceBox.tlLine.value() or self.parameter.lineMargin != settingDialog.lrcShowxConfig.appearenceBox.lmLine.value() or settingDialog.lrcShowxConfig.appearenceBox.fontEffectLabel.font().toString != self.parameter.lrcFont:
                self.parameter.topMarginLines = self.lrcShowxDock.lrcShowxWidget.topMarginLines = settingDialog.lrcShowxConfig.appearenceBox.tlLine.value()
                self.parameter.lineMargin = self.lrcShowxDock.lrcShowxWidget.lineMargin = settingDialog.lrcShowxConfig.appearenceBox.lmLine.value()
                self.parameter.lrcFont = self.lrcShowxDock.lrcShowxWidget.lrcFont = settingDialog.lrcShowxConfig.appearenceBox.fontEffectLabel.font().toString()
                self.lrcShowxDock.lrcShowxWidget.initFont()
                self.lrcShowxDock.lrcShowxWidget.playbackStateChanged_(self.musicEngine.getPlaybackState())

            if self.parameter.backGroundColor != settingDialog.lrcShowxConfig.appearenceBox.backGroundColor or self.parameter.foreGroundColor != settingDialog.lrcShowxConfig.appearenceBox.foreGroundColor or self.parameter.highLightColor != settingDialog.lrcShowxConfig.appearenceBox.highLightColor:
                self.parameter.backGroundColor = self.lrcShowxDock.lrcShowxWidget.backGroundColor = settingDialog.lrcShowxConfig.appearenceBox.backGroundColor
                self.parameter.foreGroundColor = self.lrcShowxDock.lrcShowxWidget.foreGroundColor = settingDialog.lrcShowxConfig.appearenceBox.foreGroundColor
                self.parameter.highLightColor = self.lrcShowxDock.lrcShowxWidget.highLightColor = settingDialog.lrcShowxConfig.appearenceBox.highLightColor

        self.parameter.configurationSplitterState = settingDialog.splitter.saveState()

    def beforeClose(self):
        self.systemTray.hide()

        self.parameter.windowState = self.saveState()
        self.parameter.windowGeometry = self.saveGeometry()
        self.parameter.lrcShowxDockGeometry = self.lrcShowxDock.saveGeometry()
        self.parameter.playlistDockGeometry = self.playlistDock.saveGeometry()
        self.parameter.albumCoverDockGeometry = self.albumCoverDock.saveGeometry()
        self.parameter.lrcEditorDockGeometry = self.lrcEditorDock.saveGeometry()
        self.parameter.playlistDockPlaylistTableState = self.playlistDock.playlistWidget.playlistTable.horizontalHeader().saveState()

        self.parameter.save()

        if not self.parameter.currentPlaylistName:
            self.saveCurrentPlaylist()

    def saveCurrentPlaylist(self):
        t = "\n".join(self.playlistTmp) + "\n"
        with open(os.path.join(self.parameter.privatePath, "current.txt"), "w") as f:
            f.write(t)

    def setShortcuts(self):
        self.playorpauseAction.setShortcut(QKeySequence(self.parameter.playorpauseActionShortcut))
        self.stopAction.setShortcut(QKeySequence(self.parameter.stopActionShortcut))
        self.nextAction.setShortcut(QKeySequence(self.parameter.nextActionShortcut))
        self.previousAction.setShortcut(QKeySequence(self.parameter.previousActionShortcut))
        self.repeatAction.setShortcut(QKeySequence(self.parameter.repeatActionShortcut))
        self.lrcShowxDock.lrcShowxWidget.closeLrcAction.setShortcut(QKeySequence(self.parameter.closeLrcShortcut))
        self.lrcShowxDock.lrcShowxWidget.forwardAction.setShortcut(QKeySequence(self.parameter.offsetForwardShortcut))
        self.lrcShowxDock.lrcShowxWidget.backwardAction.setShortcut(QKeySequence(self.parameter.offsetBackwardShortcut))
        self.lrcShowxDock.lrcShowxWidget.reloadAction.setShortcut(QKeySequence(self.parameter.reloadLrcShortcut))
        self.lrcEditorDock.lrcEditorWidget.insertAction.setShortcut(QKeySequence(self.parameter.insertTagShortcut))

    def quit_(self):
        self.parameter.doQuit = self.parameter.closeNotQuit
        self.close()

    def closeEvent(self, e):
        if self.parameter.doQuit:
            self.beforeClose()
            e.accept()
        else:
            if self.parameter.trayIcon and self.parameter.closeNotQuit:
                e.ignore()
                self.hide()
            else:
                self.beforeClose()
                e.accept()
