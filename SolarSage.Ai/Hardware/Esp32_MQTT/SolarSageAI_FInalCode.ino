#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <Adafruit_NeoPixel.h>

const char* ssid = "ESP32_MQTT"; // creating a soft AP
const char* password = "12345678";
const String WifiName = "ESP32_MQTT";

WiFiServer server(80);
WiFiClient espClient;
PubSubClient client(espClient);


const char* mqtt_server = "192.168.4.2";  // laptop IP on ESP32 AP
const int mqtt_port = 1884; //duplicated_config file
const char* mqtt_topic_sub = "spray/control";
const char* mqtt_topic_data_heatmap = "spray/heatmap_data";

// Enum for nozzles
enum NOZZLES {
  NOZZLE_1,
  NOZZLE_2,
  NOZZLE_3,
  NOZZLE_4,
  NOZZLE_5,
  NOZZLE_COUNT
};

// GPIO Pins
const int nozzlePins[NOZZLE_COUNT] = {12, 13, 14, 15, 18};  // Nozzle GPIOs
#define LED_WIFI 19     // WiFi status
#define LED_MSG  21     // Message arrival

// NeoPixel setup
#define NOZZLE_NEOPIXEL_PIN 5
#define NOZZLE_NUMPIXELS 5
Adafruit_NeoPixel pixel_nozzle(NOZZLE_NUMPIXELS, NOZZLE_NEOPIXEL_PIN, NEO_GRB + NEO_KHZ800);

#define HEATMAP_PIN 4
#define HEATMAP_NUMPIXELS 25
Adafruit_NeoPixel heatMap(HEATMAP_NUMPIXELS,HEATMAP_PIN, NEO_GRB + NEO_KHZ800);

//pannel data matrix for storage of data
float panelData[5][5] = {
  {0.0, 0.0, 0.0, 0.0, 0.0},
  {0.0, 0.0, 0.0, 0.0, 0.0},
  {0.0, 0.0, 0.0, 0.0, 0.0},
  {0.0, 0.0, 0.0, 0.0, 0.0},
  {0.0, 0.0, 0.0, 0.0, 0.0}
};




//conntrolling spraying states via structure
struct SprayState {
  bool active = false;
  unsigned long startTime = 0;
  unsigned long duration = 0;
  int nozzleIndex = -1;
};

SprayState spray[NOZZLE_COUNT];

//function to get nozzle id / inedex
NOZZLES getNozzleIndex(String nozzle_id) {
  if (nozzle_id == "NOZZLE_1") return NOZZLE_1;
  if (nozzle_id == "NOZZLE_2") return NOZZLE_2;
  if (nozzle_id == "NOZZLE_3") return NOZZLE_3;
  if (nozzle_id == "NOZZLE_4") return NOZZLE_4;
  if (nozzle_id == "NOZZLE_5") return NOZZLE_5;
  return (NOZZLES)(-1);
}


// Message LED flash tracking
bool msgLedFlash = false;
unsigned long msgFlashStart = 0;
const unsigned long MSG_FLASH_DURATION = 150;  // ms


void setup() {
  Serial.begin(115200);
  // Initialize LED pins
  pinMode(LED_WIFI, OUTPUT);
  pinMode(LED_MSG, OUTPUT);
  heatMap.begin();
  heatMap.show(); // Turn off initially
  pixel_nozzle.begin();
  pixel_nozzle.show();  // Turn off initially



  // Turn off initially
  digitalWrite(LED_WIFI, LOW);
  digitalWrite(LED_MSG, LOW);

  WiFi.softAP(ssid, password);  // ESP32 as AP
  digitalWrite(LED_WIFI,HIGH);
  delay(500);
  digitalWrite(LED_WIFI,LOW);
  delay(500);
  digitalWrite(LED_WIFI,HIGH);

  Serial.println("ESP32 started AP mode");
  Serial.print("IP Address: ");
  Serial.println(WiFi.softAPIP());  // Should be 192.168.4.1

  Serial.print("Acces Point name : ");
  Serial.println(WifiName);

  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(mqttCallback);
}


//a callback function to get messages
void mqttCallback(char* topic, byte* payload, unsigned int length) {
  // Flash Message LED non-blocking
  msgLedFlash = true;
  msgFlashStart = millis();
  digitalWrite(LED_MSG, HIGH);

  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.println("]");

  String message;
  for (unsigned int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.println("Payload: " + message);

  // Parse JSON
  StaticJsonDocument<200> doc;
  DeserializationError error = deserializeJson(doc, message);
  if (error) {
    Serial.print("JSON parse error: ");
    Serial.println(error.c_str());
    return;
  }

  if (strcmp(topic, mqtt_topic_sub) == 0){
    String nozzle_id = doc["nozzle_id"];
    int amount_ml = doc["amount_ml"];  // Not used yet
    int spray_timeout = doc["spray_timeout"];
    nozzleController(nozzle_id, spray_timeout);

  }

  if (strcmp(topic, mqtt_topic_data_heatmap) == 0) {
  const char* panel_id_str = doc["panel_id"];
  String panelId = String(panel_id_str);
  float sprayInterval = doc["spray_interval"];
  int hard_reset = doc["hard_reset"];
  if (panelId == "ALL_PANNELS"){
      for(int row = 0 ; row < 5 ; row++){
        for(int col = 0 ; col < 5 ; col ++){
          hard_reset == 0 ? panelData[row][col] = sprayInterval: panelData[row][col] = 150;
        }
      }
      Serial.println("Hard Reset Occurred ..... Mannual Override !");
  }
  else{
    if (panelId.startsWith("PANNEL_")) {
    int index = panelId.substring(7).toInt();  // Get number after 'PANNEL_'

    if (index >= 0 && index < 25) {
      int row = index / 5;
      int col = index % 5;
      hard_reset == 0 ? panelData[row][col] = sprayInterval: panelData[row][col] = 150;
      Serial.printf("Updated [%d][%d] with spray_interval %.2f\n", row, col, sprayInterval);
    } else {
      Serial.println("Invalid panel index: " + String(index));
    }
    
  }

    }
  // Parse panel_id like "PANNEL_0" to get the number
  heatMap_pixelController();  // Show updated pattern
}


}

void nozzleController(String nozzle_id, int spray_timeout) {
  NOZZLES nozzle = getNozzleIndex(nozzle_id);
  if (nozzle == -1) {
    Serial.println("Invalid nozzle_id: " + nozzle_id);
    return;
  }

  if (!spray[nozzle].active) {
    spray[nozzle].nozzleIndex = nozzle;
    spray[nozzle].duration = spray_timeout * 1000UL;
    spray[nozzle].startTime = millis();
    spray[nozzle].active = true;

    digitalWrite(nozzlePins[nozzle], HIGH);
    pixel_nozzle.setPixelColor(nozzle, pixel_nozzle.Color(128, 0, 128));  // Purple
    pixel_nozzle.show();

    Serial.print(nozzle_id);
    Serial.println(" : ACTIVE");
  } else {
    Serial.println("Nozzle already active. Ignored.");
  }
}


void handleSprayTimeout() {
  unsigned long currentMillis = millis();
  for (int i = 0; i < NOZZLE_COUNT; i++) {
    if (spray[i].active && (currentMillis - spray[i].startTime >= spray[i].duration)) {
      digitalWrite(nozzlePins[i], LOW);
      pixel_nozzle.setPixelColor(i, 0);  // Turn off NeoPixel
      pixel_nozzle.show();

      spray[i].active = false;
      spray[i].nozzleIndex = -1;

      Serial.print("NOZZLE_");
      Serial.print(i + 1);
      Serial.println(" : OFF");
    }
  }
}

void handleMsgLedFlash() {
  if (msgLedFlash && (millis() - msgFlashStart >= MSG_FLASH_DURATION)) {
    digitalWrite(LED_MSG, LOW);
    msgLedFlash = false;
  }
}

uint32_t getHeatColor(float interval) {
  float norm = constrain(interval / 150.0, 0.0, 1.0);
  byte r, g, b;

  if (norm < 0.25) {        // Blue → Cyan
    r = 0;
    g = norm * 4 * 255;
    b = 255;
  } else if (norm < 0.5) {  // Cyan → Green
    r = 0;
    g = 255;
    b = (1 - (norm - 0.25) * 4) * 255;
  } else if (norm < 0.75) { // Green → Yellow
    r = (norm - 0.5) * 4 * 255;
    g = 255;
    b = 0;
  } else {                  // Yellow → Red
    r = 255;
    g = (1 - (norm - 0.75) * 4) * 255;
    b = 0;
  }

  return heatMap.Color((int)r, (int)g, (int)b);
}




void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("ESP32_Nozzle_Controller")) {
      Serial.println("connected");
      client.subscribe(mqtt_topic_sub);
      client.subscribe(mqtt_topic_data_heatmap);
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" retrying in 5 seconds...");
      delay(5000);
    }
  }
}


void heatMap_pixelController(){
  
  for (int i = 0; i < 25; i++) {
    int row = i / 5;
    int col = i % 5;
    float value = panelData[row][col];
    heatMap.setPixelColor(i, getHeatColor(value));
  }

  heatMap.show();
}

void loop() {
  
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  handleSprayTimeout();
  handleMsgLedFlash();
}
