#include <ESP32Servo.h>
#include <DHT.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <WiFi.h>
#include <HTTPClient.h>

// --- Pin definitions ---
#define SERVO_PIN 13
#define TILT_PIN 5
#define DHTPIN 4
#define DHTTYPE DHT11
#define CURRENT_SENSOR_PIN 35
#define VIB_PIN 14
//#define IR_PIN 27
#define MQ132_PIN 34
#define HALL_PIN 15

// Motor pins
#define MOTOR_IN1 18
#define MOTOR_IN2 19
#define MOTOR_ENA 21

// --- ThingSpeak + WiFi ---
const char* WIFI_SSID  = "KP";
const char* WIFI_PASS  = "01072005";
const char* THINGSPEAK_API_KEY = "FPM9WFK9RVJI8WJ2";
const char* THINGSPEAK_URL = "http://api.thingspeak.com/update";

// --- Telegram Bot ---
String TELEGRAM_BOT_TOKEN = "8777769949:AAHQIKeVSjPlWjdhlYtb2xOfkISqLmzpAOs";
String TELEGRAM_CHAT_ID   = "1591370287";
String TELEGRAM_API_URL   = "https://api.telegram.org/bot";

// --- Objects ---
DHT dht(DHTPIN, DHTTYPE);
LiquidCrystal_I2C lcd(0x27, 16, 2);
Servo myServo;

volatile int pulseCount = 0;
unsigned long lastRPMCheck = 0, lastUpload = 0;
int rpm = 0;
bool motorRunning = true;
bool lastFaultState = false;

// Thresholds
float TEMP_THRESHOLD = 40.0;
float CURRENT_THRESHOLD = 15.0;
int MQ132_THRESHOLD = 3000;
int RPM_THRESHOLD = 2000;

// --- ISR ---
void IRAM_ATTR countPulse() { pulseCount++; }

// --- WiFi ---
void connectWiFi() {
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n✅ Connected to WiFi");
}

// --- Telegram Alert ---
void sendTelegram(String msg) {
  if (WiFi.status() != WL_CONNECTED) return;
  HTTPClient http;
  String url = TELEGRAM_API_URL + TELEGRAM_BOT_TOKEN + "/sendMessage?chat_id=" + TELEGRAM_CHAT_ID + "&text=" + msg;
  http.begin(url);
  int code = http.GET();
  if (code > 0) Serial.println("📨 Telegram Sent");
  else Serial.println("❌ Telegram failed: " + String(code));
  http.end();
}

// --- ThingSpeak Upload ---
void uploadToThingSpeak(float t, float c, int r, int til ,int smoke) {
  if (WiFi.status() != WL_CONNECTED) return;
  String url = String(THINGSPEAK_URL) + "?api_key=" + THINGSPEAK_API_KEY +
               "&field1=" + String(t,1) +
               "&field2=" + String(c,2) +
               "&field3=" + String(r) +
               "&field4=" + String(til) +
               "&field5=" + String(smoke);
  HTTPClient http; http.begin(url);
  int code = http.GET();
  Serial.println(code > 0 ? "📡 ThingSpeak Updated" : "⚠ Upload Failed");
  http.end();
}

// --- Motor Control ---
void startMotor() {
  digitalWrite(MOTOR_IN1, HIGH);
  digitalWrite(MOTOR_IN2, LOW);
  analogWrite(MOTOR_ENA, 180);   // PWM speed control (0–255)
  motorRunning = true;
  Serial.println("✅ Motor Started");
}

void stopMotor() {
  digitalWrite(MOTOR_IN1, LOW);
  digitalWrite(MOTOR_IN2, LOW);
  analogWrite(MOTOR_ENA, 0);
  motorRunning = false;
  Serial.println("🛑 Motor Stopped Due to Fault");
}

// --- Read Current ---
float readCurrent() {
  float voltage = analogRead(CURRENT_SENSOR_PIN) * (3.3 / 4095.0);
  float current = fabs((voltage - 2.5) / 0.185);
  return (current < 0.05) ? 0.0 : current;
}

// --- Setup ---
void setup() {
  Serial.begin(115200);
  dht.begin();
  lcd.init();
  lcd.backlight();
  myServo.attach(SERVO_PIN);

  pinMode(TILT_PIN, INPUT);
  pinMode(VIB_PIN, INPUT);
 // pinMode(IR_PIN, INPUT);
  pinMode(HALL_PIN, INPUT_PULLUP);
  pinMode(MQ132_PIN, INPUT);
  pinMode(CURRENT_SENSOR_PIN, INPUT);
  pinMode(MOTOR_IN1, OUTPUT);
  pinMode(MOTOR_IN2, OUTPUT);
  pinMode(MOTOR_ENA, OUTPUT);
  attachInterrupt(digitalPinToInterrupt(HALL_PIN), countPulse, RISING);

  connectWiFi();
  startMotor();
}

// --- Loop ---
void loop() {
  // Servo sweep
  static int angle = 120; static bool up = true;
  angle += up ? 5 : -5;
  if (angle >= 180) up = false;
  if (angle <= 120) up = true;
  myServo.write(angle);

  // Sensors
  float temp = dht.readTemperature();
  int tilt = digitalRead(TILT_PIN);
  int vib  = digitalRead(VIB_PIN);
 // int ir   = digitalRead(IR_PIN);
  float current = readCurrent();
  int smoke = analogRead(MQ132_PIN);

  // RPM every 1 s
  if (millis() - lastRPMCheck >= 1000) {
    rpm = pulseCount * 60;
    pulseCount = 0;
    lastRPMCheck = millis();
  }

  // Fault Detection
  bool fault = false;
  String msg = "";
  String faultMessage = "";
  if (!isnan(temp) && temp > TEMP_THRESHOLD) { fault = true; msg += "🔥 Temp "; faultMessage = "Temp High: " + String(temp) + "C";}
  if (tilt == HIGH) { fault = true; msg += "⚠ Tilt ";faultMessage = "Tilt Fault"; }
  if (current > CURRENT_THRESHOLD) { fault = true; msg += "⚡ Current "; faultMessage = "Over Current: " + String(current) + "A";}
  if (vib == HIGH) { fault = true; msg += "💥 Vib ";faultMessage = "Vibration Fault"; }
 // if (ir == LOW) { fault = true; msg += "🚫 IR ";faultMessage = "Obstacle Fault" ;}
  if (smoke > MQ132_THRESHOLD) { fault = true; msg += "💨 Smoke ";faultMessage = "Smoke Fault" ;}
  if (rpm > RPM_THRESHOLD) { fault = true; msg += "⚙ RPM ";faultMessage = "High RPM"; }

  // --- LCD display ---
  lcd.clear();
  if (!fault) {
    lcd.init(); // Initialize the LCD 
    lcd.backlight(); // Turn on backlight
    lcd.setCursor(0,0);
    lcd.print("Motor Status:");
    lcd.setCursor(0,1);
    lcd.print("NO FAULTS");
  } else {
    lcd.backlight(); // Turn on backlight
    lcd.setCursor(0,0);
    lcd.print("FAULT DETECTED");
    lcd.setCursor(0,1);
    lcd.print(faultMessage);
  }


  // Motor Control + Telegram Alerts
  if (fault) {
    if (!lastFaultState) {
        stopMotor();  // stop motor if running
        sendTelegram("⚠ Fault Detected: " + faultMessage);
        lastFaultState = true;
    }
} else {
    if (lastFaultState) {
        startMotor(); // restart motor
        sendTelegram("✅ System normal. Motor restarted.");
        lastFaultState = false;
    }
}

  // ThingSpeak upload every 15s
  if (millis() - lastUpload >= 10000) {
    uploadToThingSpeak(temp, current, rpm,tilt, smoke);
    lastUpload = millis();
  }

  delay(1000);
}