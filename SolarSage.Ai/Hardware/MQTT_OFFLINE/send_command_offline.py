import paho.mqtt.client as mqtt
import json
import time

#MQTT Configuration
broker = "192.168.4.2"
port = 1884
topic = "spray/control"

#Creating MQTT Client
client = mqtt.Client(client_id="laptop_command", protocol=mqtt.MQTTv311, transport="tcp")

client.connect(broker,port,60)  #60 = keep alive time ==> if 1.5 x 60 = 90 sec => Dropout connection


#Spray_command
# Spray_command = {
#     "nozzle_id" : "nozzle_1",
#     "amount_ml" : 20,
#     "spray_timeout" : 10   
# }

def send_command(Spray_cmd , topic):
    payload = json.dumps(Spray_cmd)
    result = client.publish(topic,payload)
    status = result[0]
    if status == 0 :
        print(f"✅ Command sent to Topic {topic} : {payload}")
    else:
        print(f"❌ Failed to send command !")
    time.sleep(2)
    
for i in range(1,6):
    Spray_command = {
    "nozzle_id" : f"NOZZLE_{i}",
    "amount_ml" : 20*i,
    "spray_timeout" : 10*i   
    }
    send_command(Spray_command , topic)
    
    
client.disconnect()