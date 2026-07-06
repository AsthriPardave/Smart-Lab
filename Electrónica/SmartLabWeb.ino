#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <Adafruit_Fingerprint.h>
#include <WiFi.h>
#include <HTTPClient.h>

// WIFI 
const char* ssid = "Wingo";
const char* pass = "virtualmiau1604";
const String SERVER_URL = "http://192.168.137.3:8000/api/"; 
const String CODIGO_DISPOSITIVO = "DISP001";

LiquidCrystal_I2C lcd(0x27, 16, 2);
#define RX2_PIN 16
#define TX2_PIN 17
HardwareSerial mySerial(2);
Adafruit_Fingerprint finger = Adafruit_Fingerprint(&mySerial);
const int BOTON_REGISTRO_PIN = 12;
const int BOTON_BORRAR_PIN = 14;
const int RELE_PIN = 25;

// Variables de Control de Estado
int intentosFallidos = 0;
const int MAX_INTENTOS = 3;
bool estaBloqueado = false;
unsigned long tiempoBloqueoInicio = 0;
const unsigned long DURACION_BLOQUEO = 3 * 60 * 1000; // 3 minutos
const unsigned long TIEMPO_ESPERA_REGISTRO = 20000;   // 20 segundos
const unsigned long TIEMPO_ABIERTO = 4000;

void setup() {
  Serial.begin(115200);
  pinMode(RELE_PIN, OUTPUT);
  digitalWrite(RELE_PIN, LOW);
  pinMode(BOTON_REGISTRO_PIN, INPUT_PULLUP);
  pinMode(BOTON_BORRAR_PIN, INPUT_PULLUP);

  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("Iniciando...    ");
  delay(1000);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, pass);
  
  lcd.setCursor(0, 0);
  lcd.print("Conectando WiFi ");
  lcd.setCursor(0, 1);
  lcd.print("                ");
  lcd.setCursor(0, 1);
  
  Serial.print("Conectando a WIFI");
  
  int intentos_wifi = 0;
  while (WiFi.status() != WL_CONNECTED && intentos_wifi < 30) { 
    delay(500);
    Serial.print(".");
    lcd.print(".");
    intentos_wifi++;
    
    if(intentos_wifi == 16) {
       lcd.setCursor(0, 1);
       lcd.print("                ");
       lcd.setCursor(0, 1);
    }
  }
  Serial.println("");

  if (WiFi.status() == WL_CONNECTED) {
    lcd.setCursor(0, 0);
    lcd.print("WiFi Conectado! ");
    lcd.setCursor(0, 1);
    lcd.print("                ");
    Serial.print("Conectado. IP: "); 
    Serial.println(WiFi.localIP());
    delay(2000);
  } else {
    lcd.setCursor(0, 0);
    lcd.print("Error de WiFi   ");
    lcd.setCursor(0, 1);
    lcd.print("Modo Offline    ");
    Serial.println("Error: Tiempo de espera agotado. Iniciando sin red.");
    delay(3000);
  }

  // Lector de huella
  mySerial.begin(57600, SERIAL_8N1, RX2_PIN, TX2_PIN);
  finger.begin(57600);
  delay(50);

  if (finger.verifyPassword()) {
    Serial.println("Sensor detectado con éxito.");
    lcd.setCursor(0, 0);
    lcd.print("Sensor Listo    ");
    lcd.setCursor(0, 1);
    lcd.print("                ");
  } else {
    Serial.println("No se encontró el sensor de huellas.");
    lcd.setCursor(0, 0);
    lcd.print("Error Sensor    ");
    lcd.setCursor(0, 1);
    lcd.print("Revisa cables   ");
    while (1) { delay(1); } 
  }
  
  finger.getTemplateCount();
  delay(1500);
  mostrarPantallaStandby();
}

void loop() {
  if (estaBloqueado) {
    unsigned long tiempoTranscurrido = millis() - tiempoBloqueoInicio;
    if (tiempoTranscurrido >= DURACION_BLOQUEO) {
      estaBloqueado = false;
      intentosFallidos = 0;
      mostrarPantallaStandby();
    } else {
      unsigned long tiempoRestanteMs = DURACION_BLOQUEO - tiempoTranscurrido;
      int minutos = tiempoRestanteMs / 60000;
      int segundos = (tiempoRestanteMs % 60000) / 1000;
      
      lcd.setCursor(0, 0);
      lcd.print("ACCESO BLOQUEADO"); // Exactamente 16 caracteres
      lcd.setCursor(0, 1);
      // Rellenamos con espacios para asegurar que borre rastros anteriores
      lcd.print("Espere: " + String(minutos) + "m " + String(segundos) + "s     ");
      delay(500); 
      return; 
    }
  }

  // DETECCIÓN DEL BOTÓN FÍSICO
  if (digitalRead(BOTON_REGISTRO_PIN) == LOW) {
    delay(200); // Antirebote
    registrarNuevaHuella();
    mostrarPantallaStandby();
  }

  // DETECCIÓN DEL BOTÓN FÍSICO
  if (digitalRead(BOTON_BORRAR_PIN) == LOW) {
    delay(200); // Antirebote
    borrarTodosLosRegistros();
    mostrarPantallaStandby();
  }

  // Lector de huellas en ciclo continuo  
  verificarHuellaBucle();
  delay(50); 
}

// --- FUNCIONES DEL SISTEMA ---

void mostrarPantallaStandby() {
  lcd.setCursor(0, 0);
  lcd.print("COLOQUE SU DEDO ");
  lcd.setCursor(0, 1);
  lcd.print("Para ingresar...");
}

void mostrarTiempoAgotado() {
  lcd.setCursor(0, 0);
  lcd.print("Tiempo agotado  ");
  lcd.setCursor(0, 1);
  lcd.print("Cancelando...   ");
  delay(2000);
}

void verificarHuellaBucle() {
  int p = finger.getImage();
  if (p != FINGERPRINT_OK) return; 

  p = finger.image2Tz();
  if (p != FINGERPRINT_OK) {
    mostrarErrorLectura();
    return;
  }

  p = finger.fingerFastSearch();
  if (p == FINGERPRINT_OK) {
    intentosFallidos = 0;
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Validando en red");
    
    // --- PETICIÓN AL BACKEND ---
    if(WiFi.status() == WL_CONNECTED){
      HTTPClient http;
      http.begin(SERVER_URL + "validar-acceso/");
      http.addHeader("Content-Type", "application/json");

      // Crear el JSON a enviar
      String httpRequestData = "{\"fingerprint_id\":" + String(finger.fingerID) + ",\"dispositivo_codigo\":\"" + CODIGO_DISPOSITIVO + "\"}";
      
      int httpResponseCode = http.POST(httpRequestData);
      Serial.println(httpResponseCode);
      if (httpResponseCode == 200) {
        // Acceso permitido por el backend
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("ACCESO PERMITIDO");
        abrirCerradura();

      } else {
        // Acceso denegado (fuera de horario, inactivo, etc) o error
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("ACCESO DENEGADO ");
        lcd.setCursor(0, 1);
        lcd.print("Revise horario  ");
        delay(3000);
      }
      http.end();
    } else {
       // Opcional: ¿Qué hacer si no hay WiFi? ¿Abrir igual o bloquear?
       lcd.print("Sin conexion WiFi");
       delay(2000);
    }
    
    mostrarPantallaStandby();
  } else if (p == FINGERPRINT_NOTFOUND) {
    intentosFallidos++;
    lcd.setCursor(0, 0);
    lcd.print("NO AUTORIZADO   ");
    lcd.setCursor(0, 1);
    String msjInt = "Intentos: " + String(intentosFallidos) + "/" + String(MAX_INTENTOS);
    while(msjInt.length() < 16) msjInt += " ";
    lcd.print(msjInt);
    
    delay(2000);

    if (intentosFallidos >= MAX_INTENTOS) {
      estaBloqueado = true;
      tiempoBloqueoInicio = millis();
    } else {
      mostrarPantallaStandby();
    }
  } else {
    mostrarErrorLectura();
  }
}

void mostrarErrorLectura() {
  lcd.setCursor(0, 0);
  lcd.print("Error lectura   ");
  lcd.setCursor(0, 1);
  lcd.print("Intente de nuevo");
  delay(1500);
  mostrarPantallaStandby();
}

void registrarNuevaHuella() {
  finger.getTemplateCount();
  int id = finger.templateCount + 1;

  if (id > 127) {
    lcd.setCursor(0, 0);
    lcd.print("Memoria Llena   ");
    lcd.setCursor(0, 1);
    lcd.print("                ");
    delay(2000);
    return;
  }

  lcd.setCursor(0, 0);
  lcd.print("MODO REGISTRO   ");
  lcd.setCursor(0, 1);
  lcd.print("Ponga dedo (20s)");

  int p = -1;
  unsigned long tiempoInicio = millis();
  
  while (p != FINGERPRINT_OK) {
    p = finger.getImage();
    if (millis() - tiempoInicio > TIEMPO_ESPERA_REGISTRO) {
      mostrarTiempoAgotado();
      return;
    }
    delay(50); // PAUSA VITAL
  }
  
  // ¡AQUÍ ESTABA EL ERROR! Debe ser el slot 1
  p = finger.image2Tz(1); 
  
  if (p != FINGERPRINT_OK) {
    lcd.setCursor(0, 0);
    lcd.print("Error de imagen ");
    lcd.setCursor(0, 1);
    lcd.print("                ");
    delay(2000);
    return;
  }
  
  lcd.setCursor(0, 0);
  lcd.print("Retire el dedo  ");
  lcd.setCursor(0, 1);
  lcd.print("                ");
  delay(2000);
  
  p = 0;
  while (p != FINGERPRINT_NOFINGER) {
    p = finger.getImage();
    delay(50); // PAUSA VITAL
  }

  lcd.setCursor(0, 0);
  lcd.print("Ponga de nuevo  ");
  lcd.setCursor(0, 1);
  lcd.print("Confirmar huella");
  
  p = -1;
  tiempoInicio = millis(); 
  
  while (p != FINGERPRINT_OK) {
    p = finger.getImage();
    if (millis() - tiempoInicio > TIEMPO_ESPERA_REGISTRO) {
      mostrarTiempoAgotado();
      return;
    }
    delay(50); // PAUSA VITAL
  }

  // Esta segunda lectura sí va al slot 2
  p = finger.image2Tz(2); 
  
  if (p != FINGERPRINT_OK) {
    lcd.setCursor(0, 0);
    lcd.print("Error confirmand");
    lcd.setCursor(0, 1);
    lcd.print("                ");
    delay(2000);
    return;
  }   

  p = finger.createModel();
  if (p == FINGERPRINT_OK) {
    p = finger.storeModel(id);
    if (p == FINGERPRINT_OK) {
      lcd.setCursor(0, 0);
      lcd.print("Huella Guardada ");
      lcd.setCursor(0, 1);
      lcd.print("Enviando a BD...");

      // --- PETICIÓN AL BACKEND ---
      if(WiFi.status() == WL_CONNECTED){
        HTTPClient http;
        http.begin(SERVER_URL + "registrar-docente-demo/"); 
        http.addHeader("Content-Type", "application/json");
        
        String httpRequestData = "{\"fingerprint_id\":" + String(id) + "}";
        int httpResponseCode = http.POST(httpRequestData);
        http.end();
      }

      lcd.setCursor(0, 0);
      lcd.print("Registro Exitoso");
      lcd.setCursor(0, 1);
      String msjIdNuevo = "Nuevo ID: #" + String(id);
      while(msjIdNuevo.length() < 16) msjIdNuevo += " ";
      lcd.print(msjIdNuevo);
      delay(3000);
    } else {
      // Manejo de error si falla al guardar en el sensor
      lcd.setCursor(0, 0);
      lcd.print("Error al guardar");
      delay(2000);
    }
  } else {
      // Manejo de error si las huellas no coinciden (slot 1 vs slot 2)
      lcd.setCursor(0, 0);
      lcd.print("Huellas no      ");
      lcd.setCursor(0, 1);
      lcd.print("coinciden       ");
      delay(2000);
  }
}

void abrirCerradura() {
  digitalWrite(RELE_PIN, HIGH); 
  delay(TIEMPO_ABIERTO); 
  digitalWrite(RELE_PIN, LOW);   
  Serial.println("Cerradura asegurada nuevamente.");
  intentosFallidos = 0;
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Cerrando puerta");
  delay(1000);
}

void borrarTodosLosRegistros(){  
    finger.emptyDatabase();
    lcd.setCursor(0, 0);
    lcd.print("Datos Eliminados              ");
    lcd.setCursor(0, 1);
    lcd.print("Exitosamente        ");
    Serial.println(finger.templateCount);
    delay(5000);
}