#!/usr/bin/env python
# -*- coding: utf-8 -*-
# filename: xting.py

from PyQt6.QtWidgets import QApplication
from PyQt6.QtMultimedia import QMediaDevices
from PyQt6.QtCore import QLocale, QTranslator
from mainWindow import mainWindow
import sys, os
from pathlib import Path


if __name__ == "__main__":

    __application__ = "xting"
    __version__ = "1.0.1"
    __author__ = "sanfanling"
    __license__ = "GPLV-3.0"
    __website__ = "https://github.com/sanfanling/xting"
    __supportedAudioformat__ = ["mp3", "flac", "ogg"]

    base_dir = Path(__file__).resolve().parent.as_posix()

    appdir = Path(os.path.join(os.path.expanduser("~"), ".xting")).as_posix()
    if not os.path.isdir(appdir):
        os.mkdir(appdir)
    if not os.path.isdir(Path(os.path.join(appdir, "lrc")).as_posix()):
        os.mkdir(Path(os.path.join(appdir, "lrc")).as_posix())

    args = [__application__, __version__, __author__, __license__, __website__, __supportedAudioformat__]
    app = QApplication(args)

    locale = QLocale.system().name()
    translator = QTranslator()
    translator_Folder = Path(base_dir) / f'translations/{locale}/xting.qm'
    if translator.load(Path(translator_Folder).as_posix()):
        app.installTranslator(translator)
    # else:
    #     print(f'No translation file found for {locale}')

    devices = QMediaDevices.audioOutputs()

    w = mainWindow(devices)
    w.show()
    sys.exit(app.exec())
