#!/usr/bin/env python
# -*- coding: utf-8 -*-
# filename: t2s.py
import os
from pathlib import Path

class tsTool:

    def __init__(self):
        base_dir = Path(os.path.dirname(os.path.abspath(__file__))).as_posix()
        # print(base_dir)
        trad = Path(base_dir) / "dict/traditional"
        simp = Path(base_dir) / "dict/simplified"
        
        with open(Path(trad).as_posix(), 'r', encoding="utf-8") as f:
            self.tdict = f.read()
        with open(Path(simp).as_posix(), 'r', encoding="utf-8") as f:
            self.sdict = f.read()

    def transfer(self, originalText, symbol = True):  # set True if t2s, else set False
        text = ""
        if symbol:
            for i in originalText:
                if i in self.tdict:
                    ind = self.tdict.find(i)
                    t = self.sdict[ind]
                    text += t
                else:
                    text += i
        else:
            for i in originalText:
                if i in self.sdict:
                    ind = self.sdict.find(i)
                    t = self.tdict[ind]
                    text += t
                else:
                    text += i
        return text
