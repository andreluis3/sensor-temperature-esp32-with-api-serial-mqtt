#include <LiquidCrystal_I2C.h>
#include <Wire.h>
#include <Adafruit_MLX90614.h>
#include <WiFi.h>
#include <HTTPClient.h>

// ====== OBJETOS ======
LiquidCrystal_I2C lcd(0x27, 20, 4);
Adafruit_MLX90614 mlx;

// ====== WIFI / API ======
const char* ssid = "UNIBTA";
const char* password = "uni@bta26";
const char* serverName = "http://192.168.0.159:8000/receber_dados";

// ====== CONTROLE DE TEMPO ======
const unsigned long experimentoDuracao = 60000; // 1 minuto
unsigned long inicioExperimento = 0;

// ====== ESTADOS ======
bool experimentoEmAndamento = false;
float t_ini = 0.0;

// ====== FUNÇÕES ======

void connectWiFi() {
  if (WiFi.status() == WL_CONNECTED) return;

  Serial.print("Conectando ao WiFi");
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi conectado!");
}

float readTemperature() {
  float temp = mlx.readObjectTempC();
  if (isnan(temp)) {
    Serial.println("Erro ao ler MLX90614");
    return -1000;
  }
  return temp;
}

void updateLCD(float temp, unsigned long restante) {
  lcd.setCursor(0, 0);
  lcd.print("Temp: ");
  lcd.print(temp);
  lcd.print(" C     ");

  lcd.setCursor(0, 1);
  lcd.print("Tempo: ");
  lcd.print(restante / 1000);
  lcd.print(" s     ");
}

void sendToServer(float t_ini, float t_fim) {
  if (WiFi.status() != WL_CONNECTED) return;

  HTTPClient http;
  http.begin(serverName);
  http.addHeader("Content-Type", "application/json");

  char json[200];
  snprintf(json, sizeof(json),
           "{\"id_experimento\":1,\"temperatura_inicial\":%.2f,\"temperatura_final\":%.2f}",
           t_ini, t_fim);

  int httpCode = http.POST(json);
  Serial.print("HTTP Code: ");
  Serial.println(httpCode);

  http.end();
}

// ====== SETUP ======

void setup() {
  Serial.begin(115200);

  lcd.init();
  lcd.backlight();

  if (!mlx.begin()) {
    Serial.println("MLX90614 não encontrado!");
    while (1);
  }

  connectWiFi();
}

// ====== LOOP ======

void loop() {
  connectWiFi();

  unsigned long agora = millis();
  float tempAtual = readTemperature();

  // Atualiza LCD sempre
  if (experimentoEmAndamento) {
    unsigned long tempoPassado = agora - inicioExperimento;
    unsigned long restante = experimentoDuracao - tempoPassado;
    updateLCD(tempAtual, restante);
  } else {
    updateLCD(tempAtual, experimentoDuracao);
  }

  // ===== INICIA EXPERIMENTO =====
  if (!experimentoEmAndamento) {
    t_ini = tempAtual;
    inicioExperimento = agora;
    experimentoEmAndamento = true;
    Serial.println("Experimento iniciado");
  }

  // ===== FINALIZA APÓS 1 MINUTO =====
  if (experimentoEmAndamento && (agora - inicioExperimento >= experimentoDuracao)) {
    float t_fim = tempAtual;

    Serial.println("Experimento finalizado");
    sendToServer(t_ini, t_fim);

    experimentoEmAndamento = false; // reinicia ciclo
  }
}