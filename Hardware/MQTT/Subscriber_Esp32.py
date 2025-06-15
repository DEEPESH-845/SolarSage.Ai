import paho.mqtt.client as mqtt
import json
import time

#MQTT INFO
broker = "broker.hivemq.com"
port = 1883
topic = "spray/data"

#Creating MQTT Client
client = mqtt.Client(client_id="laptop_receiver_for_ESP32", protocol=mqtt.MQTTv311, transport="tcp")


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"✅ Connected to Broker !")
        client.subscribe(topic)
        print(f"Subscribed to topic : {topic}")
    else:
        print("❌ NOT CONNECTED TPO BROKER !")

def on_message(client, userdata, msg):
    print(f"\n📥 Message received!")
    print(f"🧵 Topic: {msg.topic}")
    print(f"📦 Payload: {msg.payload.decode()}")
    
    
client.on_connect = on_connect
client.on_message = on_message

client.connect(broker,port,60)  #60 = keep alive time ==> if 1.5 x 60 = 90 sec => Dropout connection

print("📡 Waiting for messages... Press Ctrl+C to stop.\n")
client.loop_forever()