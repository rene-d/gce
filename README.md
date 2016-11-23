# gce.py
Script Python pour interroger un module [Teleinfo de GCE Electronics](http://gce-electronics.com/fr/carte-et-module-relais-serveur-ethernet/409-teleinformation-ethernet-ecodevices.html).

Documentation ERDF sur la [téléinformation client](http://www.enedis.fr/sites/default/files/ERDF-NOI-CPT_02E.pdf).

Nécessite le module [Requests](http://python-requests.org/) (voir [ici](https://github.com/rene-d/netatmo#installation-on-a-synology-nas) pour installer facilement sur un Synology).

## Détection
Les modules Teleinfo écoutent sur le port UDP 30303. Lorsqu'ils reçoivent une trame en broadcast contenant le texte 'Discover GCE Devices', ils envoient une réponse. C'est peut-être la même chose pour un IPX800 mais je ne peux pas tester.

La réponse est composée de trois lignes faciles à analyser:

    NOM<CR><LF>
    ADRESSE MAC<CR><LF>
    PORT<CR><LF>
    
## Valeurs
Les valeurs de téléinformation client sont extraites de http://ECO-DEVICES/protect/settings/teleinfo1.xml

## Usage en ligne de commande

### Retrouver l'adresse IP du module teleinfo:

    ./gce.py find [nom du device]

Exemple d'utilisation:

    curl "http://$(./gce.py find)/api/xdevices.json?cmd=10"

### Afficher tous les champs

    ./gce.py

## Usage dans un autre script Python

    #! /usr/bin/env python3
    import gce
    print(gce.teleinfo())

## Licence et garantie

Aucune. Vous pouvez réutiliser le script sans restriction. Il est fourni "tel quel", sans aucune garantie.
