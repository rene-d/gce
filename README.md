# gce
Script Python pour interroger un module Teleinfo de GCE Electronics

Nécessite le module (Requests)[http://docs.python-requests.org/]

## Détection
Les modules Teleinfo écoutent sur le port UDP 30303 
La réponse est composée de trois lignes
    NOM<CR><LF>
    ADRESSE MAC<CR><LF>
    PORT<CR><LF>
    
## Valeurs
Les valeurs de téléinformation client sont extraites de http://ECO-DEVICES/protect/settings/teleinfo1.xml
