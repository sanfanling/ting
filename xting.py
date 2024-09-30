#!/usr/bin/env python
# -*- coding: utf-8 -*-
# filename: xting.py

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtMultimedia import QMediaDevices
from PyQt6.QtCore import QLocale, QTranslator
from mainWindow import mainWindow
import sys, os



if __name__ == "__main__":

    __application__ = "xting"
    __version__ = "0.99"
    __author__ = "sanfanling"
    __license__ = "GPLV-3.0"
    __website__ = "https://github.com/sanfanling/xting"

    appdir = os.path.join(os.path.expanduser("~"), ".xting")
    if not os.path.isdir(appdir):
        os.mkdir(appdir)
    if not os.path.isdir(os.path.join(appdir, "lrc")):
        os.mkdir(os.path.join(appdir, "lrc"))

    args = [__application__, __version__, __author__, __license__, __website__]
    app = QApplication(args)

    devices = QMediaDevices.audioOutputs()

    locale = QLocale.system().name()
    translator = QTranslator()
    if translator.load(f'translations/{locale}/xting.qm'):
        app.installTranslator(translator)
    # else:
    #     print(f'No translation file found for {locale}')

    w = mainWindow(devices)
    w.show()
    sys.exit(app.exec())
