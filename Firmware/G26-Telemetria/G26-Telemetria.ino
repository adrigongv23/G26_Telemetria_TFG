#include "include/data_processor.hpp"
#include "include/can.hpp"
#include "include/common_libraries.hpp" //Librerias Wifi y credenciales

DataProcessor dataProcessor;
CAN canController;

// Cliente seguro para HTTPS
WiFiClientSecure wifiClient;

// --- ENVIO DE DATOS A TRAVÉS DE WIFI ---
// Esta función se ejecutará en paralelo sin bloquear el CAN
void TaskWifiSender(void *pvParameters) {
  
  Serial.println("[WIFI-TASK] Iniciando tarea de envío...");

  while (true) {
    // 1. Verificamos conexión WiFi
    if (WiFi.status() == WL_CONNECTED) {
      
      HTTPClient http;
      wifiClient.setInsecure(); // Importante para Firebase sin certificados complejos

      // 2. Preparamos el JSON
      // Leemos la variable 'volatile' del dataProcessor
      int tempActual = dataProcessor.current_ect_value; 

      // Creamos la URL completa
      String url = String(FIREBASE_HOST) + String(FIREBASE_PATH);
      
      // Creamos el payload JSON: {"valor": 95, "ts": 123456...}
      String jsonPayload = "{\"valor\":" + String(tempActual) + "}";

      // 3. Enviamos PUT o POST
      http.begin(wifiClient, url);
      int httpResponseCode = http.PUT(jsonPayload); // Usamos PUT para sobreescribir el valor actual

      if (httpResponseCode > 0) {
        Serial.printf("[WIFI] Enviado ECT: %d C° | Resp: %d\n", tempActual, httpResponseCode);
      } else {
        Serial.printf("[WIFI] Error envío: %s\n", http.errorToString(httpResponseCode).c_str());
      }
      http.end();

    } else {
      Serial.println("[WIFI] Desconectado. Reintentando...");
      // Si se desconecta, intentar reconectar (opcionalmente)
      WiFi.disconnect();
      WiFi.reconnect();
    }

    // 4. Esperar X tiempo antes del siguiente envío (ej. 1000ms = 1seg)
    // Usamos vTaskDelay en lugar de delay() para no bloquear
    vTaskDelay(1000 / portTICK_PERIOD_MS); 
  }
}

void setup() {
    Serial.begin(115200);
    
    // 1. INICIAR CAN Y PANTALLA
    // Pasamos el puntero de dataProcessor al controlador CAN
    canController.set_data_proccessor(&dataProcessor); 
    canController.start();
    canController.start_listening_task();
    
    // 2. INICIAR WIFI 
    Serial.println("--- CONECTANDO WIFI ---");
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    int intentos = 0;
    while (WiFi.status() != WL_CONNECTED && intentos < 20) {
        delay(500);
        Serial.print(".");
        intentos++;
    }
    if(WiFi.status() == WL_CONNECTED){
       Serial.println("\n[OK] WiFi Conectado.");
    } else {
       Serial.println("\n[ERR] No se pudo conectar WiFi (Continuando offline).");
    }

    // 3. CREAR TAREA WIFI (Multitasking)
    // Esto lanza la función TaskWifiSender en un núcleo aparte o hilo paralelo
    xTaskCreatePinnedToCore(
      TaskWifiSender,   // Función de la tarea
      "WifiSender",     // Nombre
      8192,             // Tamaño de pila (Stack size)
      NULL,             // Parámetros
      1,                // Prioridad (Baja, para que el CAN tenga prioridad)
      NULL,             // Handle
      0                 // Núcleo (0 o 1)
    );

    Serial.println("[OK] Sistema ONLINE (CAN + Pantalla + WiFi).");
}

void loop(){ 
    // El loop se queda SOLO para la interfaz gráfica (LVGL)
    vTaskDelay(5 / portTICK_PERIOD_MS);
}