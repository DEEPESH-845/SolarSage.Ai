import matplotlib.pyplot as plt

trials =range(1,51);
mqtt_latency = [30,26,35,24,28,15,12,40,56,36,72,66,39,82,56,13,23,36,49,36,69,10,15,27,51,31,65,39,54,29,11,37,35,41,16,45,90,83,61,43,50,48,44,15,22,34,73,19,81,46,]
http_get = [75,84,62,55,52,38,54,45,90,47,56,58,81,22,91,124,83,46,114,34,52,65,169,41,32,33,74,71,44,35,42,24,52,54,79,20,50,36,47,66,78,56,81,30,22,33,45,61,37,77,]
http_post = [620, 600, 630, 610, 615]

plt.plot(trials, mqtt_latency, label='MQTT', marker='o')
plt.plot(trials, http_get, label='HTTP GET', marker='x')
#plt.plot(trials, http_post, label='HTTP POST', marker='^')

plt.xlabel("Trial")
plt.ylabel("Latency (ms)")
plt.title("ESP32 Latency: MQTT vs HTTP")
plt.legend()
plt.grid(True)
plt.show()
