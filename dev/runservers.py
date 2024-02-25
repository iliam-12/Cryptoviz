import subprocess, time, sys

class KafkaServer():
    def __init__(self):
        self.running = False

    def start(self):
        try:
            # Démarrer ZooKeeper
            zookeeper_process = subprocess.Popen(["kafka_setup/bin/zookeeper-server-start.sh", "kafka_setup/config/zookeeper.properties"])

            # Ajoutez un délai de 15 secondes ici
            time.sleep(15)

            # Démarrer Kafka
            kafka_process = subprocess.Popen(["kafka_setup/bin/kafka-server-start.sh", "kafka_setup/config/server.properties"])

            # Marquer le serveur comme en cours d'exécution
            self.running = True
        except Exception as e:
            print(e)
            self.stop()
            exit()

    def stop(self):
        # Terminer ZooKeeper et Kafka une fois le script terminé
        subprocess.run(["kafka_setup/bin/zookeeper-server-stop.sh"])
        subprocess.run(["kafka_setup/bin/kafka-server-stop.sh"])

if __name__ == "__main__":
    server = KafkaServer() 
    if "stop" in sys.argv:
        server.stop()
        sys.exit(0)
    server.start()
