#!/usr/bin/python3

#from html.parser import HTMLParser
from itertools import filterfalse
import libxml2
import urllib.request

def vynechaj(r):
    if '!DOCTYPE' in r or '<meta ' in r:
        return True;
    return False

# nacitaj stranku
#TODO toto pride ako parameter
stranka = urllib.request.urlopen('https://www.pdf.umb.sk/~rozvrh/Rozvrhy/2020-21%20ZS/rozvrh_Trieda_2nAIN.html').read().decode("utf-8")

# vynechaj/oprav vadne riadky a elementy
riadky = stranka.split('\n')
riadky[:] = filterfalse(vynechaj, riadky)
stranka = '\n'.join(riadky)

stranka = stranka.replace('&nbsp;', ' ')
stranka = stranka.replace('&nbsp', ' ')
stranka = stranka.replace('<br>', '<br/>')
#stranka = stranka.replace('&#x148;', 'ň')

# parsuj stranku
doc = libxml2.parseDoc(stranka)
ctxt = doc.xpathNewContext()

# hodiny a ich casy
hlavicka = ctxt.xpathEval('/html/body/table/tr[1]/td/div/text()')
hodiny = hlavicka[1::2]
casy = {}
for i in range(0, len(hodiny)):
    #print('aaa', hodiny[i])
    #print('bbb', hlavicka[0::2][1:][i])
    oddo = str(hlavicka[0::2][1:][i]).split('-')
    casy[int(str(hodiny[i]))] = oddo

"""
rozvrh = {}
for i in range(0, 5):
    print()
    for j in range(2, len(casy)):
        hod = ctxt.xpathEval('/html/body/table/tr[' + str(2+i) + ']/td[' + str(j) + ']')
        if len(hod) == 0:
            continue
        dlzka = 1
        if hod[0].hasProp('colspan'):
            dlzka = int(hod[0].prop('colspan'))
        obsah = hod[0].getContent()
        if obsah:
            print(casy[str(j)], obsah, dlzka)
"""

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
                meno = ctxt.xpathEval('td/div/span')[0].getContent()
                predmet = ctxt.xpathEval('td/div/span')[1].getContent()
                ucebna = ctxt.xpathEval('td/div/span')[2].getContent()
                print(hod, cas_od, cas_do, meno, ucebna, predmet)
                #TODO zapisat casy od, do, obsah (nazov, ucebnu, vyucujuceho), aprobaciu
        hod += dlzka


doc.freeDoc()
ctxt.xpathFreeContext()


