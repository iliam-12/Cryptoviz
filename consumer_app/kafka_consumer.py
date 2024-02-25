from kafka import KafkaAdminClient, KafkaConsumer
from kafka.admin import NewTopic
from kafka.errors import TopicAlreadyExistsError, NoBrokersAvailable, UnknownTopicOrPartitionError
import json, argparse, configparser, os, time
from elastic import ElasticController
from loguru import logger


class KafkaHelper:
    def __init__(self, bootstrap_servers=None):
        self.bootstrap_servers = bootstrap_servers
        if not bootstrap_servers:
            self.bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS') or "host.docker.internal:29092"
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
        existing_topics = self.admin_client.list_topics()
        return topic in existing_topics

    def create_topic(self, topic):
        try:
            self.admin_client.create_topics([NewTopic(topic, 1, 1)])
            print(f"Le topic '{topic}' a été créé avec succès.")
        except TopicAlreadyExistsError:
            print(f"Le topic '{topic}' existe déjà.")
        except NoBrokersAvailable:
            print("Aucun broker disponible. Assurez-vous que votre cluster Kafka est en cours d'exécution.")
        except Exception as e:
            print(e)

    def get_list_topics(self):
        try:
            topics = self.admin_client.list_topics()
            if not topics:
                logger.info("Aucun topic")
                return []
            return topics
        except NoBrokersAvailable:
            print("Aucun broker disponible. Assurez-vous que votre cluster Kafka est en cours d'exécution.")
        except Exception as e:
            print(e)

    def send_to_elastic(self, topic_list, index_name="cryptocurrency"):
        from concurrent.futures import ThreadPoolExecutor
        logger.info("in send_to_elastic")
        self.topic_list = topic_list

        if not self.es:
            self.es = ElasticController()
            self.es.conn()

        def process_topic(topic):
            try:
                self.topic_list = self.get_list_topics()
                consumer = KafkaConsumer(
                    topic,
                    group_id="cryptocurrency",
                    bootstrap_servers=self.bootstrap_servers,
                    auto_offset_reset='earliest',
                    enable_auto_commit=True,
                    auto_commit_interval_ms=5000,
                    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
                )
                for record in consumer:
                    datas = record.value
                    actions = [
                        {
                            "_index": index_name,
                            "_source": data,
                        } for data in json.loads(record.value)
                    ]
                    self.es.upload_data(actions, topic.replace("_topic", ""))
            except Exception as e:
                logger.error(e)

        if "all" in self.topic_list:
            self.topic_list = self.get_list_topics()
            if not self.topic_list:
                time.sleep(5)
                self.send_to_elastic(["all"])

        if not self.topic_list:
            logger.warning("Aucun topic à traiter pour l'envoi à Elasticsearch.")
            return "Aucun topic à traiter pour l'envoi à Elasticsearch."

        with ThreadPoolExecutor() as executor:
            executor.map(process_topic, self.topic_list)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bootstrap_servers", type=str, help="Liste des brokers Kafka", default=None)
    parser.add_argument("--topics", nargs="+", default=["all"], help="Liste des topics cible pour envoyer à Elasticsearch")

    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()
    print("command:", args)

    kafka_consumer = KafkaHelper(args.bootstrap_servers)

    config = configparser.ConfigParser()
    config.read('credentials/config.ini')

    kafka_consumer.send_to_elastic(
        topic_list=args.topics,
        index_name=config["ELASTIC"]["INDEX_NAME"],
    )