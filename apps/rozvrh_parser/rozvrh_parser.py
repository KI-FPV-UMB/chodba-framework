#!/usr/bin/python3

#from html.parser import HTMLParser
from itertools import filterfalse
import libxml2
import urllib.request

def parsujStranku(url, aprob):
    def vynechaj(r):
        if '!DOCTYPE' in r or '<meta ' in r:
            return True;
        return False

    # nacitaj stranku
    stranka = urllib.request.urlopen(url).read().decode("utf-8")

    # vynechaj/oprav vadne riadky a elementy
    riadky = stranka.split('\n')
    riadky[:] = filterfalse(vynechaj, riadky)
    stranka = '\n'.join(riadky)

    stranka = stranka.replace('&nbsp;', ' ')
    stranka = stranka.replace('&nbsp', ' ')
    stranka = stranka.replace('<br>', '<br/>')

    # parsuj stranku
    doc = libxml2.parseDoc(stranka)
    ctxt = doc.xpathNewContext()

    # hodiny a ich casy
    hlavicka = ctxt.xpathEval('/html/body/table/tr[1]/td/div/text()')
    hodiny = hlavicka[1::2]
    casy = {}
    for i in range(0, len(hodiny)):
        oddo = str(hlavicka[0::2][1:][i]).split('-')
        casy[int(str(hodiny[i]))] = oddo

    dni = ctxt.xpathEval('/html/body/table/tr')
    hlavicka = True
    for den in dni:
        if hlavicka:
            hlavicka = False
            continue
        ctxt.setContextNode(den)
        hodiny = ctxt.xpathEval('td')
        #print(ctxt.xpathEval('td/div')[0].getContent())
        hod = 0
        for policko in hodiny:
            dlzka = 1
            if hod > 0:
                if policko.hasProp('colspan'):
                    dlzka = int(policko.prop('colspan'))
                ctxt.setContextNode(policko)
                obsahy = ctxt.xpathEval('div/table/tr')
                for obsah in obsahy:
                    ctxt.setContextNode(obsah)
                    cas_od = casy[hod][0].strip()
                    cas_do = casy[hod+dlzka-1][1].strip()
                    meno = ctxt.xpathEval('td/div/span')[0].getContent().strip()
                    predmet = ctxt.xpathEval('td/div/span')[1].getContent().strip()
                    ucebna = ctxt.xpathEval('td/div/span')[2].getContent().strip()
                    print(aprob, hod, cas_od, cas_do, meno, ucebna, predmet)
                    #TODO zapisat casy od, do, obsah (nazov, ucebnu, vyucujuceho), aprobaciu
            hod += dlzka

    doc.freeDoc()
    ctxt.xpathFreeContext()

rozvrhUrl = 'https://www.pdf.umb.sk/~rozvrh/Rozvrhy/2020-21%20ZS/'
parsujStranku(rozvrhUrl + 'rozvrh_Trieda_1nAIN.html', '1nAIN')
parsujStranku(rozvrhUrl + 'rozvrh_Trieda_2nAIN.html', '2nAIN')
parsujStranku(rozvrhUrl + 'rozvrh_Trieda_3nAIN.html', '3nAIN')

