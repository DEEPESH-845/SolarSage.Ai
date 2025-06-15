import random
import math
import time
from datetime import datetime
import json
import paho.mqtt.client as mqtt

# ========== MQTT SETUP ==========
BROKER_IP = "192.168.4.2"   # laptop as a offline server on soft api
PORT = 1884
TOPIC = "spray/heatmap_data"

client = mqtt.Client()


def connect_mqtt():
    while True:
        try:
            client.connect(BROKER_IP, PORT, 60)
            client.loop_start()
            print("✅ Connected to MQTT broker!")
            time.sleep(2)
            return
        except Exception as e:
            print(f"❌ MQTT connection failed: {e}")
            print("🔁 Retrying in 3 seconds...")
            time.sleep(3)
            
connect_mqtt()
# ========== SIMULATION FUNCTIONS ==========

def sunlight_factor(hour):
    return max(0, math.sin((hour - 6) / 12 * math.pi))

def generate_panel_data(hour, row, col ,reset):
    sun_factor = sunlight_factor(hour)

    base_temp = 22 + 15 * sun_factor
    base_humidity = 80 - 35 * sun_factor
    base_power = 250 * sun_factor
    base_light = 100000 * sun_factor

    temp = round(base_temp + random.uniform(-2, 2), 2)
    humidity = round(base_humidity + random.uniform(-3, 3), 2)
    light = int(base_light + random.uniform(-5000, 5000))
    power = int(base_power + random.uniform(-15, 15))
    efficiency = round(random.uniform(70, 95), 2)
    spray_interval = random.choice([60, 90, 120, 150])
    spray_duration = random.choice([5, 10, 15, 20])

    return {
        "timestamp": datetime.now().isoformat(),
        "panel_id": f"PANNEL_{5*row + col}",
        "power": power,
        "efficiency": efficiency,
        "spray_interval": spray_interval,
        "spray_duration": spray_duration,
        "temperature": temp,
        "humidity": humidity,
        "light": light,
        "hard_reset" : reset,
    }

# ========== PUBLISH FUNCTION ==========

def publish_all_panel_data():
    current_hour = datetime.now().hour

    for row in range(5):
        for col in range(5):
            data = generate_panel_data(current_hour, row, col,0)

            # Only send panel_id and spray_interval for ESP32
            payload = {
                "panel_id": data["panel_id"],
                "spray_interval": data["spray_interval"],
                "hard_reset": data["hard_reset"]
            }
            
            try:
                if not client.is_connected():
                    raise Exception("MQTT Disconnected")
                client.publish(TOPIC, json.dumps(payload))
                print(f"📤 Sent data to {TOPIC}: {payload}")
            except Exception as e:
                print(f"⚠️ Failed to publish: {e}")
                print("🔁 Attempting reconnect...")
                connect_mqtt()
            time.sleep(0.2)  # Small delay to avoid flooding ESP32

    print("✅ All panel data sent!")

# ========== RUN LOOP ==========

if __name__ == "__main__":
    while True:
        publish_all_panel_data()
        time.sleep(10)  # Repeats every 10 seconds (adjust as needed)
