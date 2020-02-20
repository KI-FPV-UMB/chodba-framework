#!/usr/bin/python3

# pip3 install googletrans feedparser html2text
# apt-get install python3-pyqt5 python3-bs4

import sys
import feedparser
import html2text

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QSizeGrip, QLabel, QDesktopWidget
from PyQt5.QtCore import QEvent, QTimer, pyqtSlot, Qt
from PyQt5.QtGui import QTextDocument, QPainter, QFontMetrics, QFontDatabase, QFont

from bs4 import BeautifulSoup

from googletrans import Translator

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
        #TODO oznamit svojmu node manageru, ze kolko miesta okupuje (resp. aky obdlznik na obrazovke je dostupny)
        self.setFixedSize(sg.width(), 110)
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
        self.document.setTextWidth(fm.width(value) * 1.06)
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

def ReadRSS_root(link):
    translator = Translator()
    NewsFeed = feedparser.parse(link)
    text='             root.cz            '
    for i in range(0,len(NewsFeed.entries)):
      entry = NewsFeed.entries[i]
      sentences = translator.translate(entry.title, src='cs', dest='sk').text
      if sentences.find("školeni") < 0 :
        text += sentences + '   ***   '
    return text

def ReadRSS_quark(link):
    NewsFeed = feedparser.parse(link)
    text='             Quark            '
    for i in range(0,len(NewsFeed.entries)):
      entry = NewsFeed.entries[i]
      text += entry.title + ' --- '
      sentences = str(BeautifulSoup(entry.description, "lxml").get_text().replace('\n','')).split('…')[0].split('.')
      for j in range(0,len(sentences)-1):
        text += sentences[j] + '.'
      text += '   ***   '
    return text




if __name__ == '__main__':

    app = QApplication(sys.argv)

    w = Marquee()

    text  = ReadRSS_root("https://www.root.cz/rss/zpravicky/")
    text += ReadRSS_quark("https://www.quark.sk/feed")

    w.setText(text)
    w.show()
    sys.exit(app.exec_())

