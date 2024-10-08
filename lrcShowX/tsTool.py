#!/usr/bin/env python
# -*- coding: utf-8 -*-
# filename: t2s.py

class tsTool:

    def __init__(self):
        with open("lrcShowX/dict/traditional", 'r') as f:
            self.tdict = f.read()
        with open("lrcShowX/dict/simplified", 'r') as f:
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
