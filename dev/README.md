[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)

# CRYPTO VIZ - REAL-TIME CRYPTO CURRENCIES TOOL


- Scraping Web avec _**Selenium Web Driver**_ et **_Docker_**

- Système de queue avec _**Apache Kafka**_

- Stockage avec _**InfluxDB**_

- Visualisation avec _**Tableau**_

## Description des fichiers:

**config.ini**: fichier de config

**kafka_setup/**: dossier contenant tout le projet kafka (pour run le server, stocker la Queue, etc...).

**runservers.py**: lance les 2 services **_zookeeper_** et **_kafka_**.

**kafka_controller.py**: fichier qui contient toutes les méthodes nécessaires à la manipulation des données à travers les topics (comparable à un CRUD).

**requirements.txt**: fichier qui contient les dépendances python3 installable via pip.

**venv**: dossier d'environnement à activer pour profiter des dépendances installés dedans.

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

## Instructions pour lancer Elasticsearch:

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

## Instructions pour Kafka:

Pour que kafka puisse être utilisé, il faut lancer les 2 services "zookeeper" et "kafka"

Ouvrez 2 terminaux spécialement dédié pour les laisser tourner.

Avant cela, s'ils existent, supprimer :

<img width="679" alt="image" src="https://github.com/EpitechMscProPromo2024/T-DAT-901-MAR_11/assets/65111947/7a1abf30-4bd1-4672-ad9e-a912c0f25492">

```
ps -aux | grep zookeeper
ps -aux | grep kafka

sudo kill -9 {id}
et/ou
python3 runservers.py stop
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
> Attendez que les services ce soient bien lancés avant de lancer kafka_controller.py.

Lister les topics présents
```
python3 kafka_controller.py --list_topics
```

Créer un nouveau topic
```
python3 kafka_controller.py --create_topic <nom_du_topic>
```

Supprimer un topic
```
python3 kafka_controller.py --delete_topic <list_topic>
```

Lire le contenu d'un topic `[LOOP]`
```
python3 kafka_controller.py --read_messages <nom_du_topic>
```

Envoyer des données à InfluxDB depuis un topic Kafka `[LOOP]`
```
python3 kafka_controller.py --send_to_influxdb <list_topic>
```

#
> [!TIP]
> Lancer dans cet ordre :

> python3 runservers.py
> 
> python3 scraper.py
> 
> python3 kafka_controller.py --send_to_elastic {topic_1 topic_2 topic_3 ...}