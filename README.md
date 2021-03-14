# WebSite monitoring exemple

Mise en place d'un monitoring de site web à l'aide d'[Elastic Heartbeat](https://www.elastic.co/fr/beats/heartbeat). Les données des sites web sont remontés dans une base [Elastic Search](https://www.elastic.co/fr/elasticsearch/) et un dashboard {Grafana}(https://grafana.com/) permet de visualiser les données et de générer des alertes.
Cette stack est lancée et préconfigurée dans un ensemble de container docker lancés via docker compose.

## Prérequis

Docker et docker compose doivent être présent.

## Lancement

Se positionner dans le répertoire *Docker*
Exécuter la commande *docker-compose up*

On peut se connecter à Grafana sur http://localhost:80 avec admin/admin

Dans la démo, nous effectuons le monitoring sur deux sites :
- inwebo.com
- famira.fr/test.php : Ce site contient un petit script php qui va de manière aléatoire prendre du temps pour répoudre un 200 ou un 500

Dans Grafana nous retrouvons deux graphique sur chaque site :
- Un graphique permettant de visualiser le temps de réponse du site. Une alerte est levée si le site met trop de temps à répondre. Cette alerte est volontairement basse pour la démo.
- Un graphique permettant de voir quand le site est UP (Réponse 200) ou DOWN (Réponse 500 ou timeout). Une alerte est levée si le site est trop souvent DOWN. Cette alerte est volontairement basse pour la démo.

Les alertes envoie une notificatin du type webhook consultables vers : https://webhook.site/#!/693630a3-7a32-4986-a7d2-5fb272d8b7c0

## Configuration

### Configuration des sites à monitorer

La configuration des sites à monitorer se situe dans le fichier *docker/heartbeat.docker.yml*. Se référer à la documentation de Heartbeat : https://www.elastic.co/guide/en/beats/heartbeat/current/configuring-howto-heartbeat.html

Après modification de la configuration de heartbeat il est nécessaire de rebuilder l'image en lançant un *docker-compose build* avant de relancer les container via *docker-compose up*

L'ajout d'un nouveau site à monitorer demande également l'ajout des différents graphiques et alertes dans Grafana.

### Configuration des alertes

Les alertes sont configurées directement dans Grafana.

L'ajout d'alertes de type mail nécessite de configurer un serveur smpt dans le fichier */grafana/grafana.ini*.

## Limitations et amélioration

Ce projet n'est absolument pas utilisable tel quel en production. Il manque notamment toute la gestion de la sécurité (Mot de passe par défaut ...).

Les seuils d'alerte sont définis pour lever des alertes plus fréquement que l'on voudrait dans un vrais projet. Ceci à des fins de tests.

Les dashboard Grafana nécessiteraient des améliorations, notamment l'utilisation de template.

On pourrait améliorer la gestion de la configuration de heartbeat pour ne pas avoir à rebuilder l'image en créant un volume qui fait pointer le fichier de configuration du docker vers le fichier de configuration local mais j'ai été confronté à un problème de droits.

