#include "Arduino_BMI270_BMM150.h"

const int totalSamples = 200;
const unsigned long sampleIntervalMs = 10;

void setup() {
  Serial.begin(115200);
  while (!Serial);

  if (!IMU.begin()) {
    Serial.println("IMU FAIL");
    while (1);
  }

  Serial.println("LISTO");
}

void loop() {

  if (Serial.available()) {
    Serial.read();

    Serial.println("EVENT_START");

    unsigned long nextSampleTime = millis();

    int count = 0;

    while (count < totalSamples) {

      if (millis() >= nextSampleTime &&
          IMU.accelerationAvailable() &&
          IMU.gyroscopeAvailable()) {

        float aX,aY,aZ,gX,gY,gZ;

        IMU.readAcceleration(aX,aY,aZ);
        IMU.readGyroscope(gX,gY,gZ);

        Serial.print(aX,3); Serial.print(",");
        Serial.print(aY,3); Serial.print(",");
        Serial.print(aZ,3); Serial.print(",");
        Serial.print(gX,3); Serial.print(",");
        Serial.print(gY,3); Serial.print(",");
        Serial.println(gZ,3);

        count++;
        nextSampleTime += sampleIntervalMs;
      }
    }

    Serial.println("EVENT_END");
  }
}