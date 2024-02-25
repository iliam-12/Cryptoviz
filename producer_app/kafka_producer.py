from kafka import KafkaAdminClient, KafkaProducer
from kafka.admin import NewTopic
from kafka.errors import TopicAlreadyExistsError, NoBrokersAvailable, UnknownTopicOrPartitionError
import json, os, time
from loguru import logger


class KafkaHelper:
    def __init__(self, bootstrap_servers=None):
        self.topic_configs = {
            "cleanup.policy": "delete",        # Politique de nettoyage des logs
            "retention.ms": 10800000,        # Rétention de 3 heures (3 * 60 * 60 * 1000 ms)
            "retention.bytes": 1073741824,    # Taille maximale de 1 Go en octets (1024^3)
        }
        self.bootstrap_servers = bootstrap_servers
        if not bootstrap_servers:
            self.bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS') or "kafka:19092"
        logger.info(f"Kafka bootstrap servers: {self.bootstrap_servers}")
        while True:
            try:
                self.admin_client = KafkaAdminClient(bootstrap_servers=self.bootstrap_servers)
                logger.info("KafkaAdminClient created successfully")
                break
            except Exception as e:
                logger.error(e)
                time.sleep(5)
        self.es = None

    def topic_exists(self, topic):
        existing_topics = self.get_list_topics()
        return topic in existing_topics

    def create_topic(self, topic):
        try:
            self.admin_client.create_topics([NewTopic(topic=topic, num_partitions=1, replication_factor=2, config=self.topic_configs)])
            logger.info(f"Le topic '{topic}' a été créé avec succès.")
        except TopicAlreadyExistsError:
            logger.error(f"Le topic '{topic}' existe déjà.")
        except NoBrokersAvailable:
            logger.error("Aucun broker disponible. Assurez-vous que votre cluster Kafka est en cours d'exécution.")
        except Exception as e:
            logger.error(e)

    def delete_topic(self, topic):
        try:
            self.admin_client.delete_topics([topic])
            logger.info(f"Le topic '{topic}' a été supprimé avec succès.")
        except UnknownTopicOrPartitionError:
            logger.error(f"Le topic '{topic}' n'existe pas.")
        except Exception as e:
            logger.error(e)

    def add_message(self, topic, message):
        try:
            logger.info("adding message")
            if not self.topic_exists(topic):
                logger.info(f"Le topic '{topic}' n'existe pas.")
                logger.info("Création du topic...")
                time.sleep(5)
            producer = KafkaProducer(bootstrap_servers=self.bootstrap_servers,
                                     value_serializer=lambda v: json.dumps(v).encode('utf-8'))
            producer.send(topic, message)
            producer.flush()
            logger.info("data flushed")
            # logger.info(f"Message ajouté au topic '{topic}': {str(message)}")
        except NoBrokersAvailable:
            logger.error("Aucun broker disponible. Assurez-vous que votre cluster Kafka est en cours d'exécution.")
        except Exception as e:
            logger.error(e)

    def get_list_topics(self):
        try:
            topics = self.admin_client.list_topics()
            if not topics:
                logger.info("Aucun topic")
                return []
            return topics
        except NoBrokersAvailable:
            logger.error("Aucun broker disponible. Assurez-vous que votre cluster Kafka est en cours d'exécution.")
        except Exception as e:
            logger.error(e)