#!/usr/bin/python3

"""news_scroll.py: Skrolujuci text s novinkami z predefinovanych webov."""
__author__ = "Miroslav Melicherčík"
__email__ = "miroslav.melichercik@umb.sk"

# PYTHONPATH musi odkazovat na absolutnu cestu k .../chodba-framework/base

# pip3 install googletrans
# apt-get install python3-pyqt5 python3-bs4 python3-html2text python3-feedparser

import sys
import os
import paho.mqtt.client as mqtt
import json
import random
import time
import logging
import feedparser
import html2text
from bs4 import BeautifulSoup
from googletrans import Translator
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QSizeGrip, QLabel, QDesktopWidget
from PyQt5.QtCore import QEvent, QTimer, pyqtSlot, Qt
from PyQt5.QtGui import QTextDocument, QPainter, QFontMetrics, QFontDatabase, QFont

import base_app

SCROLL_HEIGHT = 110

class Marquee(QLabel):

    x = 0

    paused = False
    document = None
    speed = 80
    timer = None

    def __init__(self, parent=None):
        super().__init__(parent,Qt.WindowStaysOnTopHint)
        #self.fm = QFontMetrics(self.font())
        sg = QDesktopWidget().screenGeometry()
        self.setFixedSize(sg.width(), SCROLL_HEIGHT)
        flags = Qt.WindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setWindowFlags(flags)
        vboxlayout = QVBoxLayout()
        sizegrip = QSizeGrip(self)
        #sizegrip.setVisible(True)
        vboxlayout.addWidget(sizegrip)
        self.setLayout(vboxlayout)

        sg = QDesktopWidget().screenGeometry()
        widget = self.geometry()
        x = 0
        y = sg.height() - widget.height()
        self.move(x, y)

        self.remaining_screen_width = sg.width()
        self.remaining_screen_height = sg.height() - widget.height()

    def setText(self, value):
        #self.x = 0

        self.document = QTextDocument(self)
        self.document.setPlainText(value)
        font = QFont()
        font.setPixelSize(90)
        font.setWeight(QFont.Bold)
        self.document.setDefaultFont(font)
        fm = QFontMetrics(font)
        # I multiplied by 1.06 because otherwise the text goes on 2 lines
        #self.document.setTextWidth(fm.width(value) * 1.06)
        self.document.setTextWidth(fm.width(value))
        self.document.setUseDesignMetrics(True)
        self.x = int(self.width() * 0.9)

        if self.document.textWidth() > self.width():
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.translate)
            self.timer.start((1 / self.speed) * 1000)

    @pyqtSlot()
    def translate(self):
        if not self.paused:
            #if self.width() - self.x < self.document.textWidth():
            if self.document.textWidth() + self.x > 0:
                self.x -= 4
            else:
                self.x = int(self.width() * 0.9)
                #self.timer.stop()
        self.repaint()

    def event(self, event):
        if event.type() == QEvent.Enter:
            self.paused = True
        elif event.type() == QEvent.Leave:
            self.paused = False
        return super().event(event)

    def paintEvent(self, event):
        if self.document:
            p = QPainter(self)
            p.translate(self.x, 0)
            self.document.drawContents(p)
        return super().paintEvent(event)



class NewsScroll(base_app.BaseApp):

    def run(self):
        # spracovavaj mqtt spravy
        self.client.loop_start()

        # vytvor Qt aplikaciu
        app = QApplication(sys.argv)
        w = Marquee()

        # oznam node manageru, ako ma obmedzit obrazovku
        msg = { "width": w.remaining_screen_width, "height": w.remaining_screen_height }
        self.pub_msg("screen_size", msg, "node/" + self.node)

        # napln rss feedy
        #TODO z konfiguracie
        text  = self.read_RSS("https://www.root.cz/rss/zpravicky/", "root.cz", ["školeni"], True)
        text += self.read_RSS("https://www.quark.sk/feed", "Quark", None)
        #TODO nastavit text by sa malo dako pravidelne; napr. kazdu hodinu
        w.setText(text)

        # spusti
        w.show()
        app.exec_()

    def read_RSS(self, link, title, filt, translate=False):
        if translate:
            translator = Translator()
        NewsFeed = feedparser.parse(link)
        ret = ("Zdroj: " + title).center(30)
        for i in range(0, len(NewsFeed.entries)):
            entry = NewsFeed.entries[i]
            if translate:
                text = translator.translate(entry.title, src='cs', dest='sk').text
            else:
                text = entry.title
                # osetri specialne pripady
                if title == "Quark":
                    text += ' --- '
                    sentences = str(BeautifulSoup(entry.description, "lxml").get_text().replace('\n','')).split('…')[0].split('.')
                    for j in range(0,len(sentences)-1):
                        text += sentences[j] + '.'

            je_tam = False
            for f in filt:
                if text.find(f) >= 0:
                    je_tam = True
            if not je_tam:
                ret += text + '   ***   '

        return ret


if __name__ == '__main__':
    app = NewsScroll()
    app.process_args(sys.argv)
    app.start()

