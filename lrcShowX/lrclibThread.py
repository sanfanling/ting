#! /usr/bin/python

from PyQt6.QtCore import (
    pyqtSignal,
    QThread,
    QThreadPool
)



class lrclibSearchThread(QThread):
    
    lrcSearched = pyqtSignal(list)
    
    def __init__(self, api, title = None, artist = None):
        super().__init__()
        self.api = api
        self.title = title
        self.artist = artist
        self.threadpool = QThreadPool()
    

    def run(self):
        r = []
        results = self.api.search_lyrics(self.title, self.artist)
        if results is not None or len(results) == 0:
            for i in results:
                if i.instrumental:
                    continue
                else:
                    r.append(i)
            self.lrcSearched.emit(r)


class lrclibGetThread(QThread):

    lrcGot = pyqtSignal(str)

    def __init__(self, api, idd = None):
        super().__init__()
        self.api = api
        self.idd = idd


    def run(self):
        ob = self.api.get_lyrics_by_id(self.idd)
  

        lrc = ob.synced_lyrics
        
        self.lrcGot.emit(lrc)





    
