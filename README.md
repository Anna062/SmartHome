# 📘 Projet Smart Home - Keyestudio KS5009 avec ESP32 et Raspberry Pi

Ce projet vise à simuler une maison intelligente en utilisant le kit Keyestudio KS5009, une **ESP32** pour la gestion des capteurs/actionneurs, et une **Raspberry Pi 4B** comme passerelle et serveur central. La communication se fait en **Modbus RTU (UART)** entre l'ESP32 et le Raspberry Pi, et en **MQTT sécurisé (TLS, port 8883)** entre le Raspberry Pi et le PC.

---

## 📅 Historique complet du projet

---

## ⚙️ 1 - Installation de l’environnement

### 📍 Côté PC
- Installation de **l’IDE Arduino**.
- Installation de toutes les bibliothèques nécessaires :
    - `ESP32Servo`
    - `LiquidCrystal_I2C`
    - `MFRC522_I2C`
    - `ESP32_AnalogWrite`
    - `Adafruit NeoPixel`
    - `Wire`
    - `OneButton`
    - `DHT11`
    - `ESP32Tone`
    - `ESP32_Music_Lib_Home`
- Création d’une **librairie globale `GlobalLibrary`** contenant tous les wrappers pour simplifier les inclusions.

### 📍 Côté Raspberry Pi
- Installation de Raspberry Pi OS Lite.
- Connexion SSH via Visual Studio Code (Remote SSH).
- Activation du port série via `raspi-config`.
- Création d’un environnement virtuel Python (venv).
- Installation des dépendances :
    - `pymodbus`
    - `paho-mqtt`

---

## 🧩 2 - Tests initiaux des capteurs/actionneurs

### Composants testés individuellement :
- Boutons
- LED
- Servo-moteur
- Capteur de température DHT11
- Capteur RFID
- Buzzer
- Écran LCD I2C
- Ventilateur (PWM)

### Exemple de test :
- Faire clignoter une LED.
- Faire tourner le ventilateur à plusieurs vitesses.
- Afficher la température sur l’écran LCD.
- Ouvrir une porte avec le module RFID.
- Jouer une mélodie avec le buzzer.

---

## 🔌 3 - Mise en place de la communication ESP32 ↔ Raspberry Pi via Modbus RTU

### 📍 Côté ESP32 (esclave)
- Initialisation de l’UART1 sur :
    - RX = GPIO4
    - TX = GPIO5
- Mise en place d’un **esclave Modbus** avec 2 registres :
    - Registre 0 = Température (en dixièmes de °C)
    - Registre 1 = Vitesse du ventilateur
- Callback `cbWrite()` pour appliquer les commandes de vitesse reçues via Modbus.
- Simulation d’une température aléatoire entre 20°C et 30°C.

### 📍 Côté Raspberry Pi (maître)
- Configuration de la liaison série sur `/dev/serial0`.
- Lecture toutes les 5 secondes du registre 0 (température).
- En fonction de la température, écriture de la vitesse du ventilateur dans le registre 1.

### 📍 Tests et débogage
- Affichage des logs côté ESP32 (reçu une commande, valeur de la vitesse, etc.).
- Affichage des logs côté Raspberry (température lue, vitesse envoyée, erreurs Modbus).

---

## 🔐 4 - Mise en place de la communication MQTT sécurisée

### 📍 Objectif
- Remonter la température et la vitesse du ventilateur vers un **broker MQTT sécurisé (port 8883)**.
- Utilisation de certificats pour sécuriser la connexion.

### 📍 Outils utilisés
- MQTTX (abandonné pour passer à Mosquitto).
- Configuration complète du broker Mosquitto avec :
    - Certificat serveur
    - Certificat client
    - Connexion TLS

---

## 📡 5 - Workflow final du projet

### Schéma de la communication
[ESP32 - Maison] | | (UART / Modbus RTU) | [Raspberry Pi - Passerelle] | | (WiFi / MQTT sécurisé 8883) | [PC - Dashboard / Supervision]


### Cycle complet
1. Le Raspberry interroge l’ESP32 via Modbus RTU pour lire la température.
2. En fonction de la température, il ajuste la vitesse du ventilateur.
3. Il publie la température et la vitesse sur des **topics MQTT sécurisés**.
4. Le PC (ou un dashboard Node-RED) reçoit ces données et les affiche en temps réel.

---

## ⚠️ 6 - Problèmes rencontrés et solutions apportées

| Problème                                                                   | Solution |
|------------------------------------------------|-----------------------------------------------------------------|
| Bibliothèques Arduino incompatibles (ESP32Servo, Wire)         | Remplacement par des versions compatibles ESP32 |
| Conflits pymodbus 2.x / 3.x                    |               Migration vers pymodbus 3.x et adaptation du code |
| Permissions UART Raspberry                     |              Ajout de l’utilisateur `admin` au groupe `dialout` |
| Modbus RX bruité / illisible                   |                 Vérification des câbles et alimentation commune |
| Erreurs de lecture Modbus (Incomplete message) | Ajustement des configurations UART et stabilisation des timings |
| Abandon de MQTTX (trop limité)                 |                     Passage à Mosquitto pour le broker avec TLS |
| Confusion entre GPIO et UART sur Raspberry Pi  |      Vérification avec `pinout` officiel et ajustement des pins |

---

## 📝 7 - Commandes utiles

### 📍 Connexion SSH
 ssh admin@Starterkit.local

### 📍 Activation UART
sudo raspi-config

### 📍 Création de l’environnement virtuel```
python3 -m venv venv
source venv/bin/activate

### 📍 Installation des dépendances
```
pip install pymodbus paho-mqtt
```

### 📍 Lancer le script de monitoring
```
Copier
Modifier
python3 read_home.py
```

---

### 📂 8 - Structure du projet
```
Copier
Modifier
Projet-Home-StartKit/
│
├── codes/
│   ├── Test_LED.ino
│   ├── Test_Servo.ino
│   ├── esp32_modbus_slave.ino     # Code final ESP32
│   └── ...
│
├── raspberry-python/
│   ├── read_home.py                # Code final côté Raspberry Pi
│   ├── requirements.txt            # Liste des dépendances Python
│   └── ...
│
├── certificates/
│   ├── ca.crt                      # Certificat d’autorité
│   ├── client.crt                  # Certificat client
│   ├── client.key                  # Clé privée client
│
├── README.md                        # Ce fichier
│
└── logs/
    ├── esp32_logs.txt              # Logs côté ESP32
    ├── raspberry_logs.txt          # Logs côté Raspberry Pi
    └── mqtt_logs.txt                # Logs côté MQTT
```

---

### 🛠️  9 - Checklist de vérification
```
- ESP32 téléversement réussi
- Logs ESP32 lisibles (commande reçue, température simulée)
- Raspberry Pi reçoit bien les valeurs Modbus
- Vitesse ventilateur change bien selon la température
- MQTT publie correctement sur les topics
- Dashboard (en option) reçoit bien les données
```
---

### 🚀  10 - Évolutions possibles
```
- Intégration Node-RED pour visualisation temps réel.
- Ajout d’une base de données InfluxDB pour historique.
- Enrichissement avec capteurs supplémentaires (humidité, luminosité, etc.).
- Sécurisation supplémentaire avec authentification côté Modbus RTU.
- Notification e-mail en cas d’anomalie (température trop élevée, etc.).
```

---

### 👨‍💻 Auteurs
```
Samy Boudaoud - Développement UART/modBus + Dashboard(en cours) + configuration hardware (RaspBerri Serial port config)
Youssouf Abayazid - Assistance montage et tests + certificats/sécurité
Fatim Dicko - Câblage initial + Développement modBus
```
