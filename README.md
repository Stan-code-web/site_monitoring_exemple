# WebSite monitoring exemple

Mise en place d'un monitoring de site avec enregistrement dans une base de données {Elasticseach}(https://www.elastic.co/fr/elasticsearch/), visualisation dans un dashboard  {Grafana}(https://grafana.com/) et remontée des alertes via WebHook. 

Cette stack est lancée et préconfigurée dans un ensemble de container docker lancés via docker compose.

## Prérequis

Docker et docker compose doivent être présent.

## Lancement

Se positionner dans le répertoire *Docker*
Exécuter la commande ```docker-compose up```

On peut se connecter à Grafana sur http://localhost:80 avec admin/admin

Dans la démo, nous effectuons le monitoring sur deux sites :
- inwebo.com
- famira.fr/test.php : Ce site contient un petit script php qui va de manière aléatoire prendre du temps pour répoudre un 200 ou un 500

Dans Grafana nous retrouvons deux graphique sur chaque site :
- Un graphique permettant de visualiser le temps de réponse du site. 
- Un graphique permettant de voir quand le site est UP (Réponse 200) ou DOWN (Réponse 500 ou timeout).

En cas de non réponse d'un site ou de réponse autre que success, une alerte de type webhook consultables vers : https://webhook.site/#!/693630a3-7a32-4986-a7d2-5fb272d8b7c0

## Configuration

### Configuration des sites à monitorer

La configuration des sites à monitorer se situe dans le fichier *app/site_monitoring.yml*.

Configuration globale à tous les sites à surveiller :

```
conf:
  #Interval between each check in second
  check_interval: 15
  #Host of the Elasticseach instance to save data
  elasticsearch_host: 'elasticsearch:9200'
  #url of the WebHook to raise the alert
  alert_webhook_url: https://webhook.site/693630a3-7a32-4986-a7d2-5fb272d8b7c0
```

Configuration des sites :

```
sites:
  - famira_status:
      #Timeout of the request in second
      timeout: 2
      #Url of the site to monitor
      url: https://famira.fr/test.php
      #Description of the site to monitor
      description: "Famira Status"
      alert:
        #If we want to raise an alert if site response is not success or timeout
        raise_alert: true
        #Text to send with the alert
        alert_text: 'Famira website is slow or down'
```

L'ajout d'un nouveau site à monitorer demande également l'ajout des différents graphiques et alertes dans Grafana.

## Limitations et amélioration

Ce projet n'est absolument pas utilisable tel quel en production. Il manque notamment toute la gestion de la sécurité (Mot de passe par défaut ...).

Le script de monitoring manque de gestion d'erreur et les logs sont à émaliorer (Niveau de log).

La configuration du site de monitoring n'est pas rechargée automatiquement

Les dashboard Grafana nécessiteraient des améliorations, notamment l'utilisation de template.

De nombreuses amélioration à apporter sur la gestion des alertes : Envoyer les alertes seulement si le site est en erreur pendant un certain temps, permettre l'envoi vers d'autre format (mail, slack ...)

