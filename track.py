#!/usr/bin/env python
# -*- coding: utf-8 -*-
# filename: track.py

import sys, os, mutagen

from mutagen.mp3 import MP3
from mutagen.mp4 import MP4

from mutagen.flac import FLAC

from mutagen.oggvorbis import OggVorbis

from mutagen.id3 import TIT2, TALB, TPE1, TDRC



class track:

    def __init__(self, f):

        self.trackFile = f

        if os.path.splitext(f)[1].lower() == ".mp3":
            self.loadMp3()
        elif os.path.splitext(f)[1].lower() == ".flac":
            self.loadFlac()
        elif os.path.splitext(f)[1].lower() == ".ogg":
            self.loadOgg()
        elif os.path.splitext(f)[1].lower() == ".m4a":
            self.loadM4a()
        else:
            self.loadUnkown()

    def loadM4a(self):
        self.trackType = "m4a"
        self.audio = mutagen.File(self.trackFile, easy = True)
        try:
            self.trackTitle = self.audio["title"][0]
        except:
            self.trackTitle = "unknow"
        try:
            self.trackAlbum = self.audio["album"][0]
        except:
            self.trackAlbum = "unknow"
        try:
            self.trackArtist = self.audio["artist"][0]
        except:
            self.trackArtist = "unknow"
        try:
            self.trackDate = self.audio["date"][0]
        except:
            self.trackDate = "unknow"
        try:
            self.trackBitrate = int(self.audio.info.bitrate)
        except:
            self.trackBitrate = 0
        try:
            self.trackSamplerate = int(self.audio.info.sample_rate)
        except:
            self.trackSamplerate = 0
        try:
            self.trackLength = int(self.audio.info.length)
        except:
            self.trackLength = 0
        try:
            self.trackBitrate = int(self.audio.info.bitrate)
        except:
            self.trackBitrate = 0
        try:
            self.trackSamplerate = int(self.audio.info.sample_rate)
        except:
            self.trackSamplerate = 0
        try:
            self.trackLength = int(self.audio.info.length)
        except:
            self.trackLength = 0

    def loadOgg(self):
        self.trackType = "ogg"
        self.audio = OggVorbis(self.trackFile)
        self.trackTitle = self.audio.tags.get(("TITLE"), ["unknow"])[0]
        self.trackAlbum = self.audio.tags.get(("ALBUM"), ["unknow"])[0]
        self.trackArtist = self.audio.tags.get(("ARTIST"), ["unknow"])[0]
        self.trackDate = self.audio.tags.get(("DATE"), ["unknow"])[0]
        try:
            self.trackBitrate = int(self.audio.info.bitrate)
        except:
            self.trackBitrate = 0
        try:
            self.trackSamplerate = int(self.audio.info.sample_rate)
        except:
            self.trackSamplerate = 0
        try:
            self.trackLength = int(self.audio.info.length)
        except:
            self.trackLength = 0

    def loadUnkown(self):
        self.trackType = "unknown"
        self.audio = None
        self.trackTitle = "unknown"
        self.trackAlbum = "unknown"
        self.trackArtist = "unknown"
        self.trackDate = "unknown"
        self.trackBitrate = 0
        self.trackSamplerate = 0
        self.trackLength = 0

    def loadFlac(self):
        self.trackType = "flac"
        self.audio = FLAC(self.trackFile)
        try:
            self.trackTitle = self.audio["title"][0]
        except:
            self.trackTitle = "unknown"
        try:
            self.trackAlbum = self.audio["album"][0]
        except:
            self.trackAlbum = "unknown"
        try:
            self.trackArtist = self.audio["artist"][0]
        except:
            self.trackArtist = "unknown"
        try:
            self.trackDate = self.audio["date"][0]
        except:
            self.trackDate = "unknown"
        try:
            self.trackBitrate = int(self.audio.info.bitrate)
        except:
            self.trackBitrate = 0
        try:
            self.trackSamplerate = int(self.audio.info.sample_rate)
        except:
            self.trackSamplerate = 0
        try:
            self.trackLength = int(self.audio.info.length)
        except:
            self.trackLength = 0

    def loadMp3(self):
        self.trackType = "mp3"
        self.audio = MP3(self.trackFile)
        try:
            self.trackTitle = str(self.audio["TIT2"].text[0])        
        except:
            self.trackTitle = "unknown"
        try:
            self.trackAlbum = str(self.audio["TALB"].text[0])
        except:
            self.trackAlbum = "unknown"
        try:
            self.trackArtist = str(self.audio["TPE1"].text[0])
        except:
            self.trackArtist = "unknown"
        try:
            self.trackDate = str(self.audio["TDRC"].text[0])
        except:
            self.trackDate = "unknown"
        try:
            self.trackBitrate = int(self.audio.info.bitrate)
        except:
            self.trackBitrate = 0
        try:
            self.trackSamplerate = int(self.audio.info.sample_rate)
        except:
            self.trackSamplerate = 0
        try:
            self.trackLength = int(self.audio.info.length)
        except:
            self.trackLength = 0

    def setTitleTag(self, v):
        if self.trackType == "mp3":
            self.audio['TIT2'] = TIT2(encoding = 3, text = v)
            self.audio.save()
        elif self.trackType == "flac" or self.trackType == "m4a":
            self.audio["title"] = v
            self.audio.save()
        elif  self.trackType == "ogg":
            self.audio["TITLE"] = v
            self.audio.save()
        else:
            print("Unsupported file type")

    def setAlbumTag(self, v):
        if self.trackType == "mp3":
            self.audio['TALB'] = TIT2(encoding = 3, text = v)
            self.audio.save()
        elif self.trackType == "flac" or self.trackType == "m4a":
            self.audio["album"] = v
            self.audio.save()
        elif  self.trackType == "ogg":
            self.audio["ALBUM"] = v
            self.audio.save()
        else:
            print("Unsupported file type")

    def setArtistTag(self, v):
        if self.trackType == "mp3":
            self.audio['TPE1'] = TIT2(encoding = 3, text = v)
            self.audio.save()
        elif self.trackType == "flac" or self.trackType == "m4a":
            self.audio["artist"] = v
            self.audio.save()
        elif  self.trackType == "ogg":
            self.audio["ARTIST"] = v
            self.audio.save()
        else:
            print("Unsupported file type")

    def setDateTag(self, v):
        if self.trackType == "mp3":
            self.audio['TDRC'] = TIT2(encoding = 3, text = v)
            self.audio.save()
        elif self.trackType == "flac" or self.trackType == "m4a":
            self.audio["date"] = v
            self.audio.save()
        elif  self.trackType == "ogg":
            self.audio["DATE"] = v
            self.audio.save()
        else:
            print("Unsupported file type")

