#ifndef COMMON_LIBRARIES_HPP
#define COMMON_LIBRARIES_HPP

#include <Arduino.h>
#include "time.h"
#include <ArduinoJson.h>
#include <vector>

//Librerías WiFi y HTTP ---
#include <WiFi.h>
#include <HTTPClient.h>
#include <WiFiClientSecure.h>

// --- CONFIGURACIÓN WIFI Y FIREBASE ---
#define WIFI_SSID "test" 
#define WIFI_PASSWORD "12345678"

#define FIREBASE_HOST "https://iot-formula-gades-default-rtdb.europe-west1.firebasedatabase.app"
// La ruta dentro de la base de datos donde guardaremos la temperatura
#define FIREBASE_PATH "/telemetria/temperatura.json"

#endif