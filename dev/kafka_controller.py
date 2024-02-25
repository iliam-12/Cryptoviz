from kafka import KafkaAdminClient, KafkaConsumer, KafkaProducer
from kafka.admin import NewTopic
from kafka.errors import TopicAlreadyExistsError, NoBrokersAvailable, UnknownTopicOrPartitionError
import json, argparse, configparser, os, time
from elastic import ElasticHelper
from loguru import logger


class KafkaHelper:
    def __init__(self, bootstrap_servers=None):
        if not bootstrap_servers:
            bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS') or "host.docker.internal:29092"
        logger.info(f"Kafka bootstrap servers: {bootstrap_servers}")
        while True:
            try:
                self.admin_client = KafkaAdminClient(bootstrap_servers=bootstrap_servers)
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

    def delete_topic(self, topic):
        try:
            self.admin_client.delete_topics([topic])
            print(f"Le topic '{topic}' a été supprimé avec succès.")
        except UnknownTopicOrPartitionError:
            print(f"Le topic '{topic}' n'existe pas.")
        except Exception as e:
            print(e)

    def add_message(self, topic, message):
        try:
            if not kafka_helper.topic_exists(topic):
                print(f"Le topic '{topic}' n'existe pas.")
                print("Création du topic...")
            producer = KafkaProducer(bootstrap_servers=self.bootstrap_servers,
                                     value_serializer=lambda v: json.dumps(v).encode('utf-8'))
            producer.send(topic, message)
            print(f"Message ajouté au topic '{topic}': {message}")
            producer.flush()
        except NoBrokersAvailable:
            print("Aucun broker disponible. Assurez-vous que votre cluster Kafka est en cours d'exécution.")
        except Exception as e:
            print(e)

    def read_messages(self, topic):
        try:
            if not kafka_helper.topic_exists(topic):
                print(f"Le topic '{topic}' n'existe pas.")
                exit()

            consumer = KafkaConsumer(
                topic,
                group_id="cryptocurrencies",
                bootstrap_servers=self.bootstrap_servers,
                value_deserializer=lambda x: json.loads(x.decode('utf-8'))
            )
            print(f"Contenu du topic '{topic}':")
            for message in consumer:
                print(message.value)
        except NoBrokersAvailable:
            print("Aucun broker disponible. Assurez-vous que votre cluster Kafka est en cours d'exécution.")
        except Exception as e:
            print(e)

    def list_topics(self):
        try:
            topics = self.admin_client.list_topics()
            if not topics:
                logger.info("Aucun topic")
                return []
            print("Liste des topics:")
            for topic in topics:
                print("->", topic)
            return topics
        except NoBrokersAvailable:
            print("Aucun broker disponible. Assurez-vous que votre cluster Kafka est en cours d'exécution.")
        except Exception as e:
            print(e)

    def send_to_elastic(self, topic_list, index_name="cryptocurrencies"):
        from concurrent.futures import ThreadPoolExecutor

        if not self.es:
            self.es = ElasticHelper()
            self.es.conn()

        def process_topic(topic):
            consumer = KafkaConsumer(
                topic,
                group_id="cryptocurrencies",
                bootstrap_servers=self.bootstrap_servers,
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                auto_commit_interval_ms=1000,
                value_deserializer=lambda x: json.loads(x.decode('utf-8'))
            )
            for record in consumer:
                data = record.value
                self.es.upload_data(data, index_name)

        if "all" in topic_list:
            topic_list = self.list_topics()

        if not topic_list:
            logger.warning("Aucun topic à traiter pour l'envoi à Elasticsearch.")
            return "Aucun topic à traiter pour l'envoi à Elasticsearch."

        with ThreadPoolExecutor() as executor:
            executor.map(process_topic, topic_list)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--list_topics", help="Liste les topics", action="store_true")
    # parser.add_argument("--add_message", type=str, help="Messages à ajouter au topic")
    parser.add_argument("--create_topics", nargs="+", help="Créer de nouveaux topics")
    parser.add_argument("--delete_topics", nargs="+", help="Supprimer des topics")
    parser.add_argument("--read_messages", type=str, help="Lire le contenu du topic")
    parser.add_argument("--bootstrap_servers", type=str, help="Liste des brokers Kafka", default=None)
    parser.add_argument("--send_to_elastic", nargs="+", help="Envoi la donnée des topics à Elasticsearch")

    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()
    print("command:", args)

    kafka_helper = KafkaHelper(args.bootstrap_servers)

    if args.list_topics:
        kafka_helper.list_topics()
        exit()

    if args.delete_topics:
        for topic in args.delete_topics:
            kafka_helper.delete_topic(topic)

    if args.create_topics:
        for topic in args.create_topics:
            if kafka_helper.topic_exists(topic):
                print(f"Le topic '{topic}' existe déjà.")
            else:
                kafka_helper.create_topic(topic)

    """
    # Ajoutez des messages au topic
    if args.add_message:
        kafka_helper.add_message(args.add_message, data)
    """

    # Lisez le contenu du topic
    if args.read_messages:
        kafka_helper.read_messages(args.read_messages)

    if args.send_to_elastic:
        config = configparser.ConfigParser()
        config.read('credentials/config.ini')

        kafka_helper.send_to_elastic(
            topic_list=args.send_to_elastic,
            index_name=config["ELASTIC"]["INDEX_NAME"],
        )
