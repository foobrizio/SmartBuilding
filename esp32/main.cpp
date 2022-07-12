#include <Arduino.h>
#include <ArduinoJson.h>
#include <ArduinoJson.hpp>

#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <DHT.h>

#include <WiFi.h>
#include <PubSubClient.h>

#include <string.h>


//Questa libreria serve per salvare dei valori nella EEPROM
#include <EEPROM.h>
#define EEPROM_SIZE 20
#define STATUS_ADDRESS 10

// DHT11 Configuration (temperature / humitity)
#define DHTTYPE DHT11
#define DHTPIN 27
DHT dht(DHTPIN,DHTTYPE);


// LED configuration
#define HEAT 4
#define COOL 0

// -------------- DATI CONFIGURAZIONE -------------

//Piano dell'edificio
const int building_floor = 5;
//Appartamento del piano
const int floor_apartment = 1;
//ID della scheda
const int deviceID = 0;

//Dati per la connessione WiFi
const char* ssid = "Covid 5G Diffusion";
//const char* ssid = "";
const char* pass = "Redibanez1";

//const char* ssid= "dlink-8D53";
//const char* pass= "Nuvola&Penny_53";



//Dati per la configurazione MQTT
//const char* mqtt_server = "192.168.102.162";
const char* mqtt_server = "broker.hivemq.com";
const int mqtt_port = 1883;
const char* mqtt_user = "510";
const char* mqtt_pass = "spezzano";
//const char* brm_LWT_topic = "resp/brm/3/0/11";

byte willQoS = 0;
char willTopic[60];
char willMessage[60];
boolean willRetain = true;


WiFiClient espClient;
PubSubClient client(espClient);

//Questa coppia serve per il controllo della connessione
long lastConnectionCheck;
const long connectionInterval = 5000;

/* Questo è il documento JSON che creiamo con tutti i valori ricevuti dai sensori.
 * Man mano che riceviamo valori, il documento cresce. Alla fine viene serializzato
 * ed inviato tramite MQTT
 */
DynamicJsonDocument jdoc(3600);
JsonArray array;


void checkConnection();
void subscribe();
void sendBirthMessage();

/*
 * Questo metodo serve ad implementare la connessione I2C con il bme280 
 */
void setupWires(){
  
  dht.begin();

  pinMode(HEAT, OUTPUT);
  pinMode(COOL, OUTPUT);
  digitalWrite(HEAT, LOW);
  digitalWrite(COOL, LOW);
}


/*
 * Questo serve per connettersi alla rete WiFi
 */
void setup_wifi(){

  delay(10);
  // We start by connecting to a WiFi network
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid,pass);
  while (WiFi.status() != WL_CONNECTED) {
    delay(700);
    Serial.print(".");
  }
  randomSeed(micros());
  Serial.println("Connected to the WiFi network!!");
}





void createLWTData(){
  snprintf(willTopic, sizeof(willTopic), "resp/esp32/%d/%d/%d/3/0/4", building_floor, floor_apartment, deviceID);
  Serial.println("Stiampiamo il topic dell'LWT");
  Serial.println(willTopic);
  StaticJsonDocument<20> respDoc;
  respDoc["v"]="Offline";
  serializeJson(respDoc, willMessage);
}






/*
 * This method processes a Temperature request. It gets the value from the sensor and,
 * the, it sends it through the respective MQTT topic. The following 4 methods work
 * in the same way.
 */
void processTemperature(){
  Serial.println("Sending temperature..");
  float temperature= dht.readTemperature();
  char tempString[8];
  dtostrf(temperature, 1, 2, tempString);
  StaticJsonDocument<200> doc;
  //doc["time"]=getTime();
  doc["v"]=tempString;
  uint8_t buffer[128];
  size_t n = serializeJson(doc, buffer);
  checkConnection();
  char topicString[60];
  snprintf(topicString, sizeof(topicString), "data/esp32/%d/%d/%d/3303/0/5700", building_floor, floor_apartment, deviceID);
  Serial.println(temperature);
  client.publish(topicString, buffer, n, false);
}

void processHumidity(){
  Serial.println("Sending humidity");
  float humidity= dht.readHumidity();
  char humString[8];
  dtostrf(humidity, 1, 2, humString);
  StaticJsonDocument<200> doc;
  //doc["time"]=getTime();
  doc["v"]=humString;
  uint8_t buffer[128];
  size_t n = serializeJson(doc, buffer);
  checkConnection();
  char topicString[60];
  snprintf(topicString, sizeof(topicString), "data/esp32/%d/%d/%d/3304/0/5700", building_floor, floor_apartment, deviceID);
  Serial.println(humidity);
  client.publish(topicString, buffer, n, false);
}




void callback(char* topic, byte* message, unsigned int length) {
  Serial.println("Message arrived.");
  Serial.println(topic);
  String messageTemp;
  
  //Qui u il byte* message in una stringa
  for (int i = 0; i < length; i++) {
    messageTemp += (char)message[i];
  }
  Serial.println(messageTemp);
  if(messageTemp.length() == 0)
    return;
  //Qui convertiamo il char* topic in un char[]
  char myTopic[50];
  char anotherTopic[50];
  strcpy(myTopic, topic);
  strcpy(anotherTopic, topic);

  //Qui tokenizziamo il token per navigarlo attraverso i vari levels
  String levels[10]; //Qui dentro avremo i nostri livelli
  char *ptr = NULL;
  byte index = 0;
  ptr = strtok(myTopic, "/");  // takes a list of delimiters
  while(ptr != NULL){
    levels[index] = ptr;
    index++;
    ptr = strtok(NULL, "/");  // takes a list of delimiters
  }
  //String locationId=levels[1]; //esp32
  String objectId=levels[5]; //3303
  String objectInstance=levels[6]; //0
  String resId=levels[7]; //5700
  Serial.println("resId:"+resId);

  StaticJsonDocument<200> doc;
  StaticJsonDocument<200> resp;

  // if(locationId == "slave"+building_floor+floor_apartment){
  //   //we received a message from the Brewmaster
  //   //Since there's no deviceID, we rewrite the variables
  //   objectId = levels[2];
  //   resId = levels[4];
  // }
 if(objectId=="3303"){
    //Temperature
    if(objectInstance=="0"){
      if(resId=="5700"){
        //we want to take the value
        
        processTemperature();
      }
    }
  }

  else if(objectId=="3304"){
    //Humidity
    if(objectInstance=="0"){
      if(resId=="5700"){
        //we want to take the value
        Serial.println("temperature");
        processHumidity();
      }
    }
  }

  else if(objectId=="3306"){
    //LEDs
    Serial.println("Checking LEDS");
    // Deserialize the JSON document
    DeserializationError error = deserializeJson(doc, messageTemp);
    // Test if parsing succeeds.
      if (error) {
        Serial.print(F("deserializeJson() failed: "));
        Serial.println(error.c_str());
        return;
      }
    String value = doc["v"];
    if(objectInstance=="1"){
      //Conditioner HEAT
      Serial.print("Too cold");
      if(resId=="5850"){
        if(value=="on"){
          digitalWrite(HEAT, HIGH);
          digitalWrite(COOL, LOW);
        }
        else if(value=="off"){
          digitalWrite(HEAT, LOW);
        }
      }
    }
    else if(objectInstance=="0"){
      //Conditioner COOL
      Serial.print("Too hot");
      if(resId=="5850"){
        if(value=="on"){
          digitalWrite(COOL, HIGH);
          digitalWrite(HEAT, LOW);
        }
        else if(value=="off"){
          digitalWrite(COOL, LOW);
        }
      }
    }
    client.publish(anotherTopic, "", true);
  }
}






void subscribe(){
  //With the # wildcard we subscribe to all the subtopics of each sublevel. 
  char topicString[20];
  snprintf(topicString, sizeof(topicString), "cmd/esp32/%d/%d/%d/#", building_floor, floor_apartment, deviceID);
  boolean res = client.subscribe(topicString, 1);
  Serial.println(topicString);
  if(res)
    Serial.println("Subscribed!");
  else
    Serial.println("Unable to subscribe");
}



void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect
    char clientId[20];
    snprintf(clientId, sizeof(clientId), "esp32-%d_%d_%d", building_floor, floor_apartment, deviceID);
    if (client.connect(clientId, mqtt_user, mqtt_pass, willTopic, willQoS, willRetain, willMessage)) {
      Serial.println("connected");
      delay(1000);
      sendBirthMessage();
      subscribe();
    }
    else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  } 
}


void checkConnection(){
  if(!client.connected())
    reconnect();
}


void sendBirthMessage(){
  StaticJsonDocument<800> resp;
  resp["v"]="Online";
  uint8_t buffer[128];
  size_t n = serializeJson(resp, buffer);
  checkConnection();
  char topicString[60];
  snprintf(topicString, sizeof(topicString), "resp/esp32/%d/%d/%d/3/0/4", building_floor, floor_apartment, deviceID);
  client.publish(topicString, buffer, n, true);
}

/*
 * Configurazione del broker MQTT.
 */
void setup_mqtt(){

  //espClient.setCACert(CA_cert);
  client.setServer(mqtt_server,mqtt_port);
  client.setCallback(callback);
  createLWTData();
  reconnect();
  delay(2000);
}




void setup() {

  Serial.begin(115200);
  // initialize EEPROM with predefined size
  EEPROM.begin(EEPROM_SIZE);
  setup_wifi();
  setup_mqtt();
  setupWires();
}



void loop() {

  client.loop();
  long now = millis();
  if(now - lastConnectionCheck >= connectionInterval){
    checkConnection();
    now=millis();
    lastConnectionCheck= now;
  }
}
