from elasticsearch import Elasticsearch, helpers
from datetime import datetime, timedelta
import configparser
import json, time
import pandas as pd
from prophet import Prophet
import concurrent.futures

config = configparser.ConfigParser()
config.read("credentials/config.ini")

# Créer le client Elasticsearch avec les paramètres de connexion
client = Elasticsearch(
    hosts=config["ELASTIC"]["URL"],
    http_auth=(config["ELASTIC"]["USERNAME"], config["ELASTIC"]["PASSWORD"]),
    verify_certs=False
)

# Définir la fenêtre de temps pour récupérer les données de la journée précédente
hier = datetime.now() - timedelta(days=1)
hier_str = hier.strftime('%Y-%m-%dT%H:%M:%S')

# Durée de validité du scroll (à ajuster si nécessaire)
scroll_time = '1s'

# Requête Elasticsearch pour récupérer les données de la journée précédente avec la fonction de scroll
query = {
    "query": {
        "range": {
            "@timestamp": {
                "gte": hier_str,
                "lt": "now"
            }
        }
    },
    "size": 10000  # Taille des résultats par itération
}

# Initialiser la recherche avec scroll
response = client.search(
    index="cryptocurrency",
    body=query,
    scroll=scroll_time  # Durée de validité du scroll
)

# Récupérer le scroll_id initial
scroll_id = response['_scroll_id']

formatted_data = {}

try:
    # Itérer jusqu'à ce qu'il n'y ait plus de résultats
    while response['hits']['hits']:
        # Parcourir les résultats actuels
        for item in response['hits']['hits']:
            cryptocurrency = item["_source"]["Cryptocurrency"]
            price = item["_source"]["Price"]
            timestamp = item["_source"]["@timestamp"]

            if cryptocurrency in formatted_data:
                formatted_data[cryptocurrency].append({"ds": timestamp, "y": price})
            else:
                formatted_data[cryptocurrency] = [{"ds": timestamp, "y": price}]

        # Effectuer une nouvelle requête de scroll
        response = client.scroll(scroll_id=scroll_id, scroll=scroll_time)
        scroll_id = response['_scroll_id']
        time.sleep(1)

except Exception as e:
    print(f"Une erreur s'est produite : {str(e)}")


predictions = []

def predict_crypto(crypto, data):
    df = pd.DataFrame(data)
    m = Prophet()
    m.fit(df)
    
    # Créez un DataFrame avec 24 timestamps, un pour chaque heure de la journée
    start_date = datetime.now()
    timestamps = [start_date + timedelta(hours=i) for i in range(24)]
    future = pd.DataFrame(timestamps, columns=['ds'])

    # Générez les prédictions avec Prophet
    forecast = m.predict(future)
    
    crypto_predictions = []
    for i in range(24):
        timestamp = forecast['ds'][i].strftime('%Y-%m-%dT%H:%M:%S.000Z')
        price = float(forecast['trend'][i])
        lower = float(forecast['yhat_lower'][i])
        upper = float(forecast['yhat_upper'][i])
        crypto_predictions.append({'_index': 'prediction', 'Cryptocurrency': crypto, '@timestamp': timestamp, 'Price': price, 'Lower': lower, 'Upper': upper})
    return crypto_predictions

with concurrent.futures.ThreadPoolExecutor() as executor:
    future_predictions = {executor.submit(predict_crypto, crypto, data): (crypto, data) for crypto, data in formatted_data.items()}
    for future in concurrent.futures.as_completed(future_predictions):
        crypto, crypto_data = future_predictions[future]
        try:
            crypto_predictions = future.result()
            predictions.extend(crypto_predictions)
            print(f"Prédiction pour {crypto} terminée.")
        except Exception as e:
            print(f"Une erreur s'est produite lors de la prédiction pour {crypto}: {e}")


if client.indices.exists(index='prediction'):
    client.indices.delete(index='prediction')
    print('Index deleting...')
    time.sleep(5)

helpers.bulk(client=client, actions=predictions)
