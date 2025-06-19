import random
import math
import time
from datetime import datetime
import json

# ========== SIMULATION FUNCTIONS ==========

def sunlight_factor(hour):
    return max(0, math.sin((hour - 6) / 12 * math.pi))

def generate_panel_data(hour, row, col):
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
        "light": light
    }

def generate_all_panel_data():
    current_hour = datetime.now().hour
    all_data = []

    for row in range(5):
        for col in range(5):
            panel_data = generate_panel_data(current_hour, row, col)
            all_data.append(panel_data)

    return all_data

# ========== MAIN FUNCTION ==========

def save_data_to_json():
    data = generate_all_panel_data()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"panel_data_{timestamp}.json"

    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

    print(f"✅ Saved simulated panel data to '{filename}'")

# ========== RUN ==========

if __name__ == "__main__":
    save_data_to_json()
