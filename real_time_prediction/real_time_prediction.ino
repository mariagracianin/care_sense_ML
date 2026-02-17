#include "Arduino_BMI270_BMM150.h"

#include <TensorFlowLite.h>
#include <tensorflow/lite/micro/all_ops_resolver.h>
#include <tensorflow/lite/micro/micro_error_reporter.h>
#include <tensorflow/lite/micro/micro_interpreter.h>
#include <tensorflow/lite/schema/schema_generated.h>
#include <tensorflow/lite/version.h>

#include "model.h"

// ================= CONFIG =================

const int SAMPLE_RATE_HZ = 100;        // ~100 Hz IMU real
const int WINDOW_SAMPLES = 200;        // 2 segundos
const int FEATURES = 6;                // ax ay az gx gy gz
const int INFERENCE_STEP = 20;         // cada 0.5 s → 50 muestras

// ===========================================

float circularBuffer[WINDOW_SAMPLES][FEATURES];
int writeIndex = 0;
int totalSamples = 0;
int samplesSinceLastInference = 0;

// -------- TFLM --------

tflite::MicroErrorReporter tflErrorReporter;
tflite::AllOpsResolver tflOpsResolver;

const tflite::Model* tflModel = nullptr;
tflite::MicroInterpreter* tflInterpreter = nullptr;
TfLiteTensor* tflInputTensor = nullptr;
TfLiteTensor* tflOutputTensor = nullptr;

// Ajusta si hace falta (modelos de 200x6 suelen necesitar más)
constexpr int tensorArenaSize = 24 * 1024;
byte tensorArena[tensorArenaSize] __attribute__((aligned(16)));

const char* CLASSES[] = {
  "fall",
  "lie_down",
  "walk",
  "sit"
};

#define NUM_CLASSES 4

// -------- Timing --------

unsigned long lastSampleMicros = 0;
const unsigned long samplePeriodMicros = 1000000UL / SAMPLE_RATE_HZ;

// ===========================================

void setup() {
  Serial.begin(115200);
  while (!Serial);

  if (!IMU.begin()) {
    Serial.println("IMU init failed!");
    while (1);
  }

  Serial.println("IMU OK");

  tflModel = tflite::GetModel(model);
  if (tflModel->version() != TFLITE_SCHEMA_VERSION) {
    Serial.println("Schema mismatch!");
    while (1);
  }

  tflInterpreter = new tflite::MicroInterpreter(
    tflModel,
    tflOpsResolver,
    tensorArena,
    tensorArenaSize,
    &tflErrorReporter
  );

  tflInterpreter->AllocateTensors();

  tflInputTensor  = tflInterpreter->input(0);
  tflOutputTensor = tflInterpreter->output(0);

  Serial.println("TFLM ready");
}

// ===========================================

void copyWindowToInputTensor() {
  // Copiar buffer circular → tensor en orden temporal correcto
  int idx = writeIndex;

  for (int i = 0; i < WINDOW_SAMPLES; i++) {
    for (int f = 0; f < FEATURES; f++) {
      tflInputTensor->data.f[i * FEATURES + f] =
        circularBuffer[idx][f];
    }

    idx++;
    if (idx >= WINDOW_SAMPLES) idx = 0;
  }
}

// ===========================================

void runInference() {

  copyWindowToInputTensor();

  if (tflInterpreter->Invoke() != kTfLiteOk) {
    Serial.println("Invoke failed");
    return;
  }

  // buscar clase ganadora
  int bestIdx = 0;
  float bestScore = tflOutputTensor->data.f[0];

  for (int i = 1; i < NUM_CLASSES; i++) {
    float v = tflOutputTensor->data.f[i];
    if (v > bestScore) {
      bestScore = v;
      bestIdx = i;
    }
  }

  Serial.print("Prediction: ");
  Serial.print(CLASSES[bestIdx]);
  Serial.print("  score=");
  Serial.println(bestScore, 4);
}

// ===========================================

void loop() {

  if (micros() - lastSampleMicros < samplePeriodMicros) return;
  lastSampleMicros = micros();

  if (!(IMU.accelerationAvailable() && IMU.gyroscopeAvailable()))
    return;

  float ax, ay, az, gx, gy, gz;

  IMU.readAcceleration(ax, ay, az);
  IMU.readGyroscope(gx, gy, gz);

  // -------- normalización (igual que training) --------

  circularBuffer[writeIndex][0] = (ax + 4.0) / 8.0;
  circularBuffer[writeIndex][1] = (ay + 4.0) / 8.0;
  circularBuffer[writeIndex][2] = (az + 4.0) / 8.0;

  circularBuffer[writeIndex][3] = (gx + 2000.0) / 4000.0;
  circularBuffer[writeIndex][4] = (gy + 2000.0) / 4000.0;
  circularBuffer[writeIndex][5] = (gz + 2000.0) / 4000.0;

  writeIndex++;
  if (writeIndex >= WINDOW_SAMPLES) writeIndex = 0;

  totalSamples++;
  samplesSinceLastInference++;

  // esperar a tener ventana completa
  if (totalSamples < WINDOW_SAMPLES) return;

  // inferencia cada 0.5 s
  if (samplesSinceLastInference >= INFERENCE_STEP) {
    samplesSinceLastInference = 0;
    runInference();
  }
}