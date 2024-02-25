[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)

# CRYPTO VIZ - REAL-TIME PRODUCER/CONSUMER DATA PIPELINE

- Container Application Development avec **_Docker_**

- Scraping Web avec _**Selenium Webdriver**_

- Système de queue avec _**Apache Kafka**_

- Stockage avec _**ElasticSearch**_

- Visualisation avec _**Kibana**_

<img width="500" alt="Capture d’écran 2024-02-25 à 21 41 23" src="https://github.com/iliam-12/Cryptoviz/assets/65111947/9cc7bbec-1d84-4a57-b066-94161034944f">
<img width="500" alt="Capture d’écran 2024-02-25 à 19 40 23" src="https://github.com/iliam-12/Cryptoviz/assets/65111947/d0cc2e74-1dff-4551-ab4c-0ea2b948aa58">
<img width="500" alt="Capture d’écran 2024-02-25 à 19 40 55" src="https://github.com/iliam-12/Cryptoviz/assets/65111947/c4ac2827-a9d1-46dd-bbe5-29dc1ffc4902">
<img width="500" alt="Capture d’écran 2024-02-25 à 19 41 45" src="https://github.com/iliam-12/Cryptoviz/assets/65111947/21420deb-8706-42c5-9aac-35572c6175bf">

## Description des fichiers:

- **consumer_app/**: module contenant la partie scraper / ajout des données dans les topics kafka

- **producer_app/**: module contenant la partie aspiration des données des topics kafka / envoie des données à la db elasticsearch

- **\*/config.ini**: fichier de config

- **docker-compose.yml**: fichier de configuration pour lancer plusieurs conteneurs docker (images ou Dockerfiles) selon un ordre et des spécifications définis.

- **Dockerfile_producer**: Dockerfile du producer_app

- **Dockerfile_consumer**: Dockerfile du consumer_app

- **requirements.txt**: fichier qui contient les dépendances python installable via pip.

- **kafka_controller.py**: [DEV] fichier qui contient toutes les méthodes nécessaires à la manipulation des données à travers les topics (comparable à un CRUD).

- **runservers.py**: [DEV] lance les 2 services **_zookeeper_** et **_kafka_**.

- **kafka_setup/**: [DEV] dossier contenant tout le projet kafka (pour run le server, stocker la Queue, etc...).

## Diagramme de flux :

<img width="1508" alt="image" src="https://github.com/iliam-12/Cryptoviz/assets/65111947/03c22f47-2253-4e56-b5d9-3a164b17a0d5">

## Instructions pour lancer Elasticsearch (obligatoire):

#### Elasticsearch :
```
sudo docker run -d --name elasticsearch -p 9200:9200 -p 9300:9300 \
-e "discovery.type=single-node" \
docker.elastic.co/elasticsearch/elasticsearch:8.12.0
```

#### Kibana :
```
sudo docker run -d --name kibana -p 5601:5601 \
--link elasticsearch:elasticsearch \
docker.elastic.co/kibana/kibana:8.12.0
```

Accéder à l'interface web Kibana :
```
http://91.121.191.19:5601/
```

Entrer dans les terminaux des containers si besoin :
```
docker exec -it <container_id> /bin/bash
```

# Pour une utilisation microservicisé via Docker

## Architecture :

<img width="900" alt="Capture d’écran 2024-02-25 à 22 15 47" src="https://github.com/iliam-12/Cryptoviz/assets/65111947/0fcb5184-b1e5-4d87-8730-0265368ff4f9">

## Installation

Se connecter tout d'abord à notre server Debian.

Installer [Docker](https://docs.docker.com/engine/install/) selon votre environnement.

Vous pouvez dès à présent mettre en route toute la pipeline à partir de la commande :
```
docker-compose up
```
L'exécution des conteneurs se fera alors dans cet ordre :
```
zookeeper1 et zookeeper2 > kafka > producer_app > consumer_app > ia_module_app
```
pour que les données soient récoltés sur [coinmarketcap.com ](https://coinmarketcap.com/coins/), transformés, envoyés à elasticsearch et enfin visualisés sur [Kibana](http://91.121.191.19:5601/).

## Well Architected Framework

Notre architecture englobe plusieurs piliers fondamentaux dans la conception, le déploiement et la gestion des microservices, assurant ainsi la sécurité, la fiabilité, la performance et l'efficacité opérationnelle de nos systèmes.

- #### Sécurité :
> Qui peut se connecter à notre serveur kafka pour ajouter de fausses données ou voir même tout détruire ? Uniquement les adresses IP définit dans la configuration du server. Kafka prend en charge SSL/TLS pour chiffrer les données communiquant entre le client Kafka et les brokers Kafka (app conteneurs).

- #### Fiabilité et Disponibilité :
> Nous avons pris en charge tous les scénarios d'erreurs potentiels, réduisant ainsi la probabilité de dysfonctionnement des scripts Python grâce à l'utilisation de blocs try/except pour des conditions protégées. De plus, dans le fichier docker-compose.yml, nous avons spécifié une option de spécialisation "restart: always" pour chacun des microservices, garantissant ainsi leur redémarrage automatique en cas de crash. De plus, nous avons déployé deux instances de Zookeeper, renforçant ainsi la robustesse de l'application en assurant une disponibilité continue.

- #### Performance :
> Nous avons opté pour le langage de programmation Python, réputé dans la Data Engineering, ainsi que ses bibliothèques, afin de réaliser le scrapping et le traitement des données de manière rapide et efficace.

- #### Scalabilité :
> Le projet a été conçu de manière microservicisé afin de permettre au client d'ajouter les fonctionnalités de son choix tout en préservant l'intégrité du noyau central.

- #### Coût :
> Nous hébergeons tous les services sur notre serveur Debian gratuitement.

# Pour une utilisation locale en mode DEV sans microservices (optionel)

## Installations

Installez le dossier [Kafka](https://www.apache.org/dyn/closer.cgi?path=/kafka/3.6.1/kafka_2.13-3.6.1.tgz)

Renommez-le en **kafka_setup** et placez-le à la racine du projet.

### pré-requis:

- python3 :snake:

- pip3

Si l'environnement virtuel (le dossier venv) n'est pas présent à la racine du projet, le générer avec la commande :
```
python3 -m venv venv
```

Activation de l'environnement virtuel avec la commande :

```
source venv/bin/activate
```

Pour sortir de l'environnement virtuel :
```
deactivate
```

Installation des dépendances avec la commande :

```
pip install -r requirements.txt
```

## Instructions pour Kafka (optionel):

Pour que kafka puisse être utilisé, il faut lancer les 2 services "zookeeper" et "kafka"

Ouvrez 2 terminaux spécialement dédié pour les laisser tourner.

Avant cela, s'ils existent, supprimer :

<img width="679" alt="image" src="https://github.com/EpitechMscProPromo2024/T-DAT-901-MAR_11/assets/65111947/7a1abf30-4bd1-4672-ad9e-a912c0f25492">

```
ps -aux | grep zookeeper
ps -aux | grep kafka

sudo kill -9 {id}
```

Suppression des topics
```
rm -rf /tmp/kafka-logs /tmp/zookeeper
```

Lancer le server **zookeeper** en premier en attendant qu'il soit complètement lancé :
```
kafka_setup/bin/zookeeper-server-start.sh kafka_setup/config/zookeeper.properties
```
Lancer le server **kafka** :
```
kafka_setup/bin/kafka-server-start.sh kafka_setup/config/server.properties
```


# 
> [!NOTE]
> [DEV] Attendez que les services ce soient bien lancés avant de lancer kafka_controller.py.

Lister les topics présents
```
python3 kafka_controller.py --list_topics
```

Créer un nouveau topic
```
python3 kafka_controller.py <nom_du_topic> --create_topic
```

Supprimer un topic
```
python3 kafka_controller.py <nom_du_topic> --delete_topic
```

Ajouter des messages à un topic
```
python3 kafka_controller.py <nom_du_topic> --add_messages
```

Lire le contenu d'un topic `[LOOP]`
```
python3 kafka_controller.py <nom_du_topic> --read_messages
```

Envoyer des données à InfluxDB depuis un topic Kafka `[LOOP]`
```
python3 kafka_controller.py <nom_du_topic> --send_to_influxdb
```

#
> [!TIP]
> [DEV] Les arguments peuvent être aggrégés entre eux:
```
python3 kafka_controller.py <nom_du_topic> --create_topic --add_messages --read_messages
```

> Une fois votre topic créé et votre script **--send_to_influxdb** en marche, il ne vous reste plus qu'à lancer votre script **--add_messages** avec votre data pour avoir la pipeline fonctionnelle.
