#! /usr/bin/env python3
# coding: utf-8
# vim:set ts=4 sw=4 et:

# René 2016/11/07

from __future__ import print_function
import sys
import socket
import select
import xml.sax
import requests

if sys.version_info[0] == 2:
    reload(sys)
    sys.setdefaultencoding('utf-8')

# cf. la documentation de GCE Electronics et celle d'ERDF
TELEINFO_ERDF = {
    'ADCO' : 'Adresse du compteur',
    'OPTARIF' : 'Option tarifaire choisie',
    'ISOUSC'  : 'Intensité souscrite',
    # Index option Base
    'BASE' : 'Index option Base',
    # Index option Heures Creuses
    'HCHC' : 'Heures Creuses',
    'HCHP' : 'Heures Pleines',
    # Index option EJP
    'EJPHN' : 'Heures Normales',
    'EJPHPM' : 'Heures de Pointe Mobile',
    # Index option Tempo
    'BBRHCJB' :   'Heures Creuses Jours Bleus',
    'BBRHPJB' :   'Heures Pleines Jours Bleus',
    'BBRHCJW' :   'Heures Creuses Jours Blancs',
    'BBRHPJW' :   'Heures Pleines Jours Blancs',
    'BBRHCJR' :   'Heures Creuses Jours Rouges',
    'BBRHPJR' :   'Heures Pleines Jours Rouges',
    # autres champs
    'PEJP' : 'Préavis Début EJP (30 min)',
    'PTEC' : 'Période Tarifaire en cours',
    'DEMAIN' : 'Couleur du lendemain',
    'IINST' : 'Intensité Instantanée',
    'IINST1' : 'Intensité Instantanée phase 1',
    'IINST2' : 'Intensité Instantanée phase 2',
    'IINST3' : 'Intensité Instantanée phase 3',
    'ADPS' : 'Avertissement de Dépassement De Puissance Souscrite',
    'IMAX' : 'Intensité maximale appelée',
    'IMAX1' : 'Intensité maximale appelée phase 1',
    'IMAX2' : 'Intensité maximale appelée phase 2',
    'IMAX3' : 'Intensité maximale appelée phase 3',
    'PAPP' : 'Puissance apparente',
    'PPAP' : 'Puissance apparente (mal orthographiée)',
    'HHPHC' : 'Horaire Heures Pleines Heures Creuses',
    'MOTDETAT' : "Mot d'état du compteur",
    'PPOT' : 'Présence des potentiels',
}


##
# @brief cherche les équipements GCE sur le réseau local
#
# @param duration       durée de recherche (1 seconde par défaut)
# @param name           nom du device à chercher ou * pour tous ou None pour le premier trouvé
#
# @return un tableau de [ IP, NOM, MAC, PORT ]
def find_gce(duration=1, name=None):

    gce = []

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.setblocking(0)

    data = b'Discover GCE Devices'
    s.sendto(data, ('<broadcast>', 30303))

    timeout = 0.1
    n = 0
    while n < duration / timeout:
        r = select.select([s],[],[], timeout)
        if len(r[0]) == 1:
            data, addr = s.recvfrom(256)
            if not isinstance(data, str):
                data = data.decode('ascii')
            data = data.split('\r\n')[0:-1]
            data = [ addr[0] ] + [ str.strip(i) for i in data ]

            if name is None or data[1].lower() == name.lower():
                gce.append(data)
                break
            elif name == '*':
                gce.append(data)

        n += 1

    s.close()

    return gce


##
# @brief cherche un module GCE
#
# @param duration durée de recherche
#
# @return None si aucun module n'est trouvé ou un tableau [ IP, NOM, MAC, PORT ]
def find_first_gce(duration=1):
    gce = find_gce(duration)
    return None if len(gce) == 0 else gce[0]


##
# @brief classe callback pour l'analyse de teleinfoX.xml
class T1_parser(xml.sax.handler.ContentHandler):
    def __init__(self, prefixe="T1_"):
        self.prefixe = prefixe
        self.values = dict()
        self.data = None

    def startElement(self, name, attrs):
        if name.startswith(self.prefixe):
            self.data = ""

    def characters(self, content):
        if not self.data is None:
            self.data += content

    def endElement(self, name):
        if not self.data is None:
            self.values[name] = self.data
            self.data = None

##
# @brief retourne un dict contenant la téléinfo du premier module détecté
#
# @param numero numéro de téléinfo (1 ou 2)
#
# @return 
def teleinfo(numero=1):
    assert(numero == 1 or numero == 2)

    gce = find_first_gce()
    if gce is None: return

    url = "http://{}:{}/protect/settings/teleinfo{}.xml".format(gce[0], gce[3], numero)
    data = requests.get(url)
 
    handler = T1_parser("T{}_".format(numero))
    xml.sax.parseString(data.text, handler)
    return handler.values


if __name__ == '__main__':
    if len(sys.argv) >= 2 and sys.argv[1] == 'find':
        name = None
        if len(sys.argv) > 2: name = sys.argv[2]
        t = find_gce(name=name)
        if len(t) > 0:
            t = t[0]
            print("{}:{}".format(t[0], t[3]))
    else:
        print("Test GCE")
        print(find_first_gce())
        for k, v in sorted(teleinfo().items()):
            t = '?'
            for i, j in TELEINFO_ERDF.items():
                if k.endswith(i):
                    t = j
            print("%20s : %-14s %s" % (k, v, t))

