import paho.mqtt.client as mqtt
import time
import threading

# Configuration MQTT
MQTT_BROKER = "192.168.101.39"  # Adresse IP du Raspberry Pi
MQTT_PORT = 8883  # Port par défaut de Mosquitto
MQTT_TOPIC_COMMANDE = "maison/commande"  # Topic pour recevoir les commandes
MQTT_TOPIC_REPONSE = "maison/reponse"  # Topic pour envoyer les réponses
MQTT_TOPIC_STATUT = "maison/statut"  # Topic pour envoyer des mises à jour de statut

# Callback lorsque la connexion au broker est établie
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("Connecté au broker MQTT")
        # S'abonner au topic des commandes
        client.subscribe(MQTT_TOPIC_COMMANDE)
        print(f"Abonné au topic {MQTT_TOPIC_COMMANDE}")
    else:
        print(f"Échec de la connexion, code d'erreur: {rc}")

# Callback en cas de déconnexion
def on_disconnect(client, userdata, rc, properties=None):
    print("Déconnecté du broker MQTT")
    # Tentative de reconnexion
    print("Tentative de reconnexion...")
    client.reconnect()

# Callback pour la réception de messages
def on_message(client, userdata, msg):
    message = msg.payload.decode()
    print(f"Message reçu sur le topic {msg.topic}: {message}")

    # Traiter le message reçu
    if message == "allumer_lampe":
        print("Commande reçue : allumer la lampe")
        reponse = "Lampe allumée"
    elif message == "eteindre_lampe":
        print("Commande reçue : éteindre la lampe")
        reponse = "Lampe éteinte"
    else:
        print("Commande non reconnue")
        reponse = "Commande non reconnue"

    # Renvoyer une réponse sur le topic des réponses
    client.publish(MQTT_TOPIC_REPONSE, reponse)
    print(f"Réponse envoyée sur le topic {MQTT_TOPIC_REPONSE}: {reponse}")

# Fonction pour envoyer des mises à jour de statut
def envoyer_statut(client):
    while True:
        # Simuler un statut (par exemple, température ou état d'un capteur)
        statut = "Température: 25°C"
        client.publish(MQTT_TOPIC_STATUT, statut)
        print(f"Statut envoyé sur le topic {MQTT_TOPIC_STATUT}: {statut}")
        time.sleep(10)  # Envoyer un statut toutes les 10 secondes

# Créer un client MQTT avec la dernière version de l'API de rappel
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

# Assigner les callbacks
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message

# Se connecter au broker MQTT
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Démarrer la boucle de communication
client.loop_start()

# Démarrer un thread pour envoyer des mises à jour de statut
thread_statut = threading.Thread(target=envoyer_statut, args=(client,))
thread_statut.daemon = True  # Le thread s'arrêtera lorsque le programme principal s'arrête
thread_statut.start()

# Maintenir le script en cours d'exécution
try:
    while True:
        time.sleep(1)  # Réduire l'utilisation du CPU
except KeyboardInterrupt:
    print("Arrêt du script...")
    # Arrêter la boucle et se déconnecter proprement
    client.loop_stop()
    client.disconnect()