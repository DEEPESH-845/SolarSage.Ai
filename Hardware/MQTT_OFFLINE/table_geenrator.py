import pandas as pd
import matplotlib.pyplot as plt

# Data
trials = list(range(1, 51))
mqtt_latency = [30,26,35,24,28,15,12,40,56,36,72,66,39,82,56,13,23,36,49,36,
                69,10,15,27,51,31,65,39,54,29,11,37,35,41,16,45,90,83,61,43,
                50,48,44,15,22,34,73,19,81,46]
http_get = [75,84,62,55,52,38,54,45,90,47,56,58,81,22,91,124,83,46,114,34,
            52,65,169,41,32,33,74,71,44,35,42,24,52,54,79,20,50,36,47,66,
            78,56,81,30,22,33,45,61,37,77]

# Create DataFrame
df = pd.DataFrame({
    'Trial': trials,
    'MQTT Latency (ms)': mqtt_latency,
    'HTTP GET Latency (ms)': http_get
})

# Plot table
fig, ax = plt.subplots(figsize=(10, 15))  # Adjust height for full visibility
ax.axis('off')  # Hide axes

# Create the table and add to plot
table = ax.table(cellText=df.values,
                 colLabels=df.columns,
                 cellLoc='center',
                 loc='center')

table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1.2, 1.2)  # Scale table size

plt.title("Latency Table: MQTT vs HTTP GET", fontsize=14, pad=20)
plt.tight_layout()
plt.show()
