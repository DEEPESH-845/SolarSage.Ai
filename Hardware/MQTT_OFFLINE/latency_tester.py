import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print("Connected with result code", rc)
    client.subscribe("latency/ping")

def on_message(client, userdata, msg):
    print("Ping received:", msg.payload.decode())
    client.publish("latency/pong", msg.payload)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("192.168.4.2", 1884, 60)  # Connect to ESP32 AP

client.loop_forever()
