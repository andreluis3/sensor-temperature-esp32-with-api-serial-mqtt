#include <LiquidCrystal_I2C.h>
#include <Wire.h>
#include <Adafruit_MLX90614.h>
#include <WiFi.h>
#include <HTTPClient.h>

LiquidCrystal_I2C lcd(0x27,20,4);
Adafruit_MLX90614 mlx = Adafruit_MLX90614();

const char* ssid = "Joao";
const char* password = "stefany1511";
const char* serverName = "http://192.168.200.227:8000/receber_dados";

void setup() {

  mlx.begin();
  lcd.init();
  lcd.backlight();

  Serial.begin(115200);
  WiFi.begin(ssid, password);
  while(WiFi.status() != WL_CONNECTED) { delay(500); Serial.print("."); }
  Serial.println("Conectado!");
}

void loop() {

  int httpResponseCode = 0;
  
  lcd.setCursor(0,0);
  lcd.print("Capsula: ");
  lcd.print(mlx.readObjectTempC());
  lcd.print("C");

  if(WiFi.status() == WL_CONNECTED){
    HTTPClient http;
    http.begin(serverName);
    http.addHeader("Content-Type", "application/json");
    
    // Simulação ou leitura real do sensor
    float t_ini = mlx.readObjectTempC(); 
    lcd.clear();
    delay(2000);
    float t_fim = mlx.readObjectTempC();
    
    String json_data = "{\"id_experimento\": 1, \"temperatura_inicial\": " + String(t_ini) + ", \"temperatura_final\": " + String(t_fim) + "}";
    int httpResponseCode = http.POST(json_data);
    Serial.println(httpResponseCode);
    http.end();
  }

  delay(1000);

}
