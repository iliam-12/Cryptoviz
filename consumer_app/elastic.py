from elasticsearch import Elasticsearch, helpers
import configparser, sys, json, argparse, time
from datetime import datetime
from loguru import logger
from tools import retry


def retry(max_attempts=5, delay=1, backoff=2):
    def decorator(func):
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    logger.error(f"Error: {str(e)}")
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                    delay *= backoff
                    attempts += 1
            logger.error(f"Function {func.__name__} failed after {max_attempts} attempts.")
            return None
        return wrapper
    return decorator

class ElasticController:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read("credentials/config.ini")
        self.es = None

    def conn(self):
        try:
            if not self.es:
                self.es = Elasticsearch(
                    hosts=self.config["ELASTIC"]["URL"],
                    basic_auth=(self.config["ELASTIC"]["USERNAME"],
                    self.config["ELASTIC"]["PASSWORD"]),
                    ca_certs=False,
                    verify_certs=False
                )
                if self.es:
                    logger.info("Connected to elasticsearch")
            return self.es
        except Exception as err:
            logger.error(f"Can't connect to elasticsearch: {err}")
            sys.exit(1)

    def create_index_not_exist(self, index):
        try:
            if not self.es.indices.exists(index=index):
                elastic_mapping = json.load(open("credentials/cryptocurrencies_mapping.json"))
                self.es.indices.create(index=index, body=elastic_mapping, ignore=400)
                logger.info(f"{index} created !")
        except Exception as err:
            logger.error(err)

    def delete_index(self, index):
        try:
            self.es = self.conn()  # safety measure, uncomment this if you are sure
            if self.es.indices.exists(index=index):
                if input(f"Are you sure you want to delete '{index}' index ? [O/N]") in [True, "O", "yes", "Y"]:
                    resp = self.es.indices.delete(index=index)
                    if resp["acknowledged"]:
                        logger.info(f"Delete index {index} OK")
                        return True
                    else:
                        logger.error(f"Delete index {index} FAILED with response {resp}")
                        return False
        except Exception as e:
            logger.error(f"Error during delete index {str(e)}")

    @retry(max_attempts=5, delay=1, backoff=2)
    def upload_data(self, data, index_name="cryptocurrency"):
        try:
            self.create_index_not_exist(index_name)
            helpers.bulk(client=self.es, actions=data, index=index_name)
            logger.info("bulk data successfully send")
        except Exception as err:
            logger.error(err)
            return False

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--delete_index", type=str, help="Nom de l'index à supprimer")
    parser.add_argument("--create_index", type=str, help="Nom de l'index à créer")
    parser.add_argument("--index", type=str, help="Index visé")
    parser.add_argument("--crypto_name", type=str, help="Crypto à ajouter")
    parser.add_argument("--price", type=str, help="Prix de la crypto à ajouter")
    parser.add_argument("--symbol", type=str, help="Symbol de la crypto à ajouter")

    return parser.parse_args()

if __name__ == "__main__":
    args = get_args()
    logger.info(args)

    es = ElasticController()
    es.conn()

    if args.create_index:
        es.create_index_not_exist(args.create_index)
    if args.delete_index:
        es.delete_index(args.delete_index)
