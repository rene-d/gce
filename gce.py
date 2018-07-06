#! /usr/bin/env python3
# coding: utf-8
# vim:set ts=4 sw=4 et:

# René 2016/11/07

"""
    Module d'interrogation d'Eco-Devices GCE Electronics
"""

from __future__ import print_function
import sys
import socket
import select
import xml.sax
import requests


# compatibilité Python 2.7
if sys.version_info[0] == 2:
    reload(sys)
    sys.setdefaultencoding('utf-8')


# cf. la documentation de GCE Electronics et celle d'ERDF
TELEINFO_ERDF = {
    'ADCO':     'Adresse du compteur',
    'OPTARIF':  'Option tarifaire choisie',
    'ISOUSC':   'Intensité souscrite',
    # Index option Base
    'BASE':     'Index option Base',
    # Index option Heures Creuses
    'HCHC':     'Heures Creuses',
    'HCHP':     'Heures Pleines',
    # Index option EJP
    'EJPHN':    'Heures Normales',
    'EJPHPM':   'Heures de Pointe Mobile',
    # Index option Tempo
    'BBRHCJB':  'Heures Creuses Jours Bleus',
    'BBRHPJB':  'Heures Pleines Jours Bleus',
    'BBRHCJW':  'Heures Creuses Jours Blancs',
    'BBRHPJW':  'Heures Pleines Jours Blancs',
    'BBRHCJR':  'Heures Creuses Jours Rouges',
    'BBRHPJR':  'Heures Pleines Jours Rouges',
    # autres champs
    'PEJP':     'Préavis Début EJP (30 min)',
    'PTEC':     'Période Tarifaire en cours',
    'DEMAIN':   'Couleur du lendemain',
    'IINST':    'Intensité Instantanée',
    'IINST1':   'Intensité Instantanée phase 1',
    'IINST2':   'Intensité Instantanée phase 2',
    'IINST3':   'Intensité Instantanée phase 3',
    'ADPS':     'Avertissement de Dépassement De Puissance Souscrite',
    'IMAX':     'Intensité maximale appelée',
    'IMAX1':    'Intensité maximale appelée phase 1',
    'IMAX2':    'Intensité maximale appelée phase 2',
    'IMAX3':    'Intensité maximale appelée phase 3',
    'PAPP':     'Puissance apparente',
    'PPAP':     'Puissance apparente (mal orthographiée)',
    'HHPHC':    'Horaire Heures Pleines Heures Creuses',
    'MOTDETAT': 'Mot d\'état du compteur',
    'PPOT':     'Présence des potentiels',
}


def find_gce(duration=1, name=None):
    """
        cherche les équipements GCE sur le réseau local

        duration   durée de recherche (1 seconde par défaut)
        name       nom du device à chercher ou * pour tous ou None pour le premier trouvé
        return     un tableau de [ IP, NOM, MAC, PORT ]
    """

    gce = []

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.setblocking(0)

    data = b'Discover GCE Devices'
    sock.sendto(data, ('<broadcast>', 30303))

    timeout = 0.1
    iteration = 0
    while iteration < duration / timeout:
        wait = select.select([sock], [], [], timeout)
        if len(wait[0]) == 1:
            data, addr = sock.recvfrom(256)
            if not isinstance(data, str):
                data = data.decode('ascii')
            data = data.split('\r\n')[0:-1]
            data = [addr[0]] + [str.strip(i) for i in data]

            if name is None or data[1].lower() == name.lower():
                gce.append(data)
                break
            elif name == '*':
                gce.append(data)

        iteration += 1

    sock.close()

    return gce


def find_first_gce(duration=1):
    """
        cherche un module GCE

        duration    durée de recherche
        return      None si aucun module n'est trouvé ou un tableau [ IP, NOM, MAC, PORT ]
    """
    gce = find_gce(duration)
    return None if len(gce) == 0 else gce[0]


class _TeleinfoParser(xml.sax.handler.ContentHandler):
    """
        classe callback pour l'analyse de teleinfoX.xml
    """

    def __init__(self, prefixe="T1_"):
        xml.sax.handler.ContentHandler.__init__(self)
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


def teleinfo(numero=1, gce=None):
    """
        retourne un dict contenant la téléinfo du premier module détecté

        numero  numéro de téléinfo (1 ou 2)
        return  un dict avec les valeurs ou None
    """
    assert numero == 1 or numero == 2

    if gce is None:
        gce = find_first_gce()
    if gce is None:
        return

    url = "http://{}:{}/protect/settings/teleinfo{}.xml".format(gce[0], gce[3], numero)
    data = requests.get(url)

    handler = _TeleinfoParser("T{}_".format(numero))
    xml.sax.parseString(data.text, handler)
    return handler.values


def status(gce=None):
    """
        retourne un dict contenant le status.xml du premier module détecté
        c'est la requête qui est effectuée en permanence par la page web du module

        return  un dict avec les valeurs ou None
    """

    if gce is None:
        gce = find_first_gce()
    if gce is None:
        return

    url = "http://{}:{}/status.xml".format(gce[0], gce[3])
    data = requests.get(url)

    handler = _TeleinfoParser("")
    xml.sax.parseString(data.text, handler)
    return handler.values


def donnees(gce=None):
    """
        retourne le résumé des données de l'Eco-Devices
    """
    if gce is None:
        gce = find_first_gce()
    if gce is None:
        return

    url = "http://{}:{}/api/xdevices.json?cmd=10".format(gce[0], gce[3])
    data = requests.get(url)
    if data.status_code == 200:
        return data.json()


def compteurs(gce=None):
    """
        retourne les valeurs des compteurs C1 et C2 du premier module détecté
    """
    if gce is None:
        gce = find_first_gce()
    if gce is None:
        return

    url = "http://{}:{}/api/xdevices.json?cmd=20".format(gce[0], gce[3])
    data = requests.get(url)
    if data.status_code == 200:
        return data.json()


def main():
    """
        fonction principale
    """
    if len(sys.argv) >= 2 and sys.argv[1] == 'find':
        if len(sys.argv) > 2:
            name = sys.argv[2]
        else:
            name = None
        data = find_gce(name=name)
        if len(data) > 0:
            data = data[0]
            print("{}:{}".format(data[0], data[3]))
    else:
        print("Test GCE")
        gce = find_first_gce()
        print("Device:", gce)

        # teleinfo
        print("Teleinfo:")
        for key, value in sorted(teleinfo(gce=gce).items()):
            text = '?'
            for i, j in TELEINFO_ERDF.items():
                if key.endswith(i):
                    text = j
            print("%20s : %-14s %s" % (key, value, text))
        
        # compteurs
        cpt = compteurs(gce=gce)
        print("Compteurs:")
        print("%20s : %-14s %s" % ("C1", cpt['Day_C1'], 'Compteur 1'))
        print("%20s : %-14s %s" % ("C2", cpt['Day_C2'], 'Compteur 2'))

        # # résumé des données
        # data = donnees(gce=gce)
        # for key, value in sorted(data.items()):
        #     print("%20s : %-14s" % (key, value))

        # # status
        # data = status(gce=gce)
        # for key, value in sorted(data.items()):
        #     print("%20s : %-14s" % (key, value))


if __name__ == '__main__':
    main()
