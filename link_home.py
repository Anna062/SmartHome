import time
import threading
from pymodbus.client.serial import ModbusSerialClient
import paho.mqtt.client as mqtt

# Configuration Modbus RTU (liaison série entre RPi et ESP32)
modbus_client = ModbusSerialClient(
    port='/dev/serial0',  # GPIO14/15 sur RPi
    baudrate=9600,
    parity='N',
    stopbits=1,
    bytesize=8,
    timeout=3
)

# Configuration MQTT
MQTT_BROKER = "192.168.101.39"  # Adresse IP du Raspberry Pi
MQTT_PORT = 8883
MQTT_TOPIC_COMMANDE = "maison/commande"  # Pour recevoir les commandes
MQTT_TOPIC_REPONSE = "maison/reponse"  # Pour envoyer des réponses
MQTT_TOPIC_STATUT = "maison/statut"  # Pour envoyer des mises à jour

# Création du client MQTT
mqtt_client = mqtt.Client()

# Callback lors de la connexion au broker
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("✅ Connecté au broker MQTT")
        client.subscribe(MQTT_TOPIC_COMMANDE)
        print(f"📡 Abonné au topic {MQTT_TOPIC_COMMANDE}")
    else:
        print(f"⚠️ Échec de connexion MQTT, code: {rc}")

# Callback lors de la réception d'un message MQTT (commande)
def on_message(client, userdata, msg):
    commande = msg.payload.decode()
    print(f"📥 Commande reçue : {commande}")
    
    try:
        valeur_a_envoyer = int(commande)  # Convertir en entier
        result = modbus_client.write_register(0, valeur_a_envoyer, slave=1)  # Écrire dans le registre 0 de l'ESP32
        
        if not result.isError():
            print(f"✅ Commande envoyée à l'ESP32 via Modbus: {valeur_a_envoyer}")
            mqtt_client.publish(MQTT_TOPIC_REPONSE, f"Commande {valeur_a_envoyer} envoyée")
        else:
            print("❌ Erreur Modbus lors de l'envoi de la commande")
            mqtt_client.publish(MQTT_TOPIC_REPONSE, "Erreur lors de l'envoi")
    
    except ValueError:
        print("⚠️ Erreur : la commande MQTT reçue n'est pas un nombre valide")
        mqtt_client.publish(MQTT_TOPIC_REPONSE, "Commande invalide")

# Callback en cas de déconnexion MQTT
def on_disconnect(client, userdata, rc, properties=None):
    print("❌ Déconnecté du broker MQTT")
    print("🔄 Tentative de reconnexion...")
    client.reconnect()

# Lire la température de l'ESP32 et la publier sur MQTT
def read_and_publish():
    while True:
        result = modbus_client.read_holding_registers(0, 1, slave=1)
        if not result.isError():
            temperature = result.registers[0] / 10.0
            print(f"🌡️ Température reçue : {temperature:.1f} °C")
            mqtt_client.publish(MQTT_TOPIC_STATUT, f"Température: {temperature}°C")
        else:
            print("❌ Erreur Modbus lors de la lecture")
        time.sleep(5)  # Lecture toutes les 5 secondes

# Initialisation MQTT
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.on_disconnect = on_disconnect

mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.loop_start()

# Vérifier la connexion Modbus avant de démarrer la boucle de lecture
if modbus_client.connect():
    print("✅ Connecté à l'ESP32 via Modbus RTU")

    # Démarrer un thread pour la lecture périodique
    thread_modbus = threading.Thread(target=read_and_publish)
    thread_modbus.daemon = True
    thread_modbus.start()

    try:
        while True:
            time.sleep(1)  # Garde le script actif
    except KeyboardInterrupt:
        print("🛑 Arrêt du script...")
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        modbus_client.close()
else:
    print("❌ Impossible de se connecter à l'ESP32")
