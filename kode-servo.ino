#include <Servo.h>

Servo servoX;
Servo servoY;

int posX = 90; // initial position
int posY = 90; // initial position

float filteredX = 90; // initial filtered position
float filteredY = 90; // initial filtered position

// PID constants
float kp = 1.0;
float ki = 0.1;
float kd = 0.1;

float lastErrorX = 0;
float lastErrorY = 0;
float integralX = 0;
float integralY = 0;

void setup() {
  Serial.begin(115200); // Increase baud rate for better communication
  servoX.attach(9); // attach servo on pin 9
  servoY.attach(10); // attach servo on pin 10
  servoX.write(posX);
  servoY.write(posY);
}

void loop() {
  static unsigned long lastReceiveTime = 0;
  static const unsigned long timeout = 1000; // 1 second timeout

  if (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n');
    
    // Validate and parse data
    if (data.indexOf(',') > 0) {
      int commaIndex = data.indexOf(',');
      int xVal = data.substring(0, commaIndex).toInt();
      int yVal = data.substring(commaIndex + 1).toInt();
      
      // Validate the parsed values
      if (xVal >= -90 && xVal <= 90 && yVal >= -90 && yVal <= 90) {
        // Reverse the direction of the servo movement
        int targetX = map(xVal, -90, 90, 180, 0); // Reversed
        int targetY = map(yVal, -90, 90, 0, 180); // Reversed

        // Apply exponential filter
        filteredX = 0.9 * filteredX + 0.1 * targetX;
        filteredY = 0.9 * filteredY + 0.1 * targetY;

        // Apply PID control
        float errorX = filteredX - posX;
        integralX += errorX;
        float derivativeX = errorX - lastErrorX;
        posX += kp * errorX + ki * integralX + kd * derivativeX;
        lastErrorX = errorX;

        float errorY = filteredY - posY;
        integralY += errorY;
        float derivativeY = errorY - lastErrorY;
        posY += kp * errorY + ki * integralY + kd * derivativeY;
        lastErrorY = errorY;

        // Constrain values to valid servo range
        posX = constrain(posX, 0, 180);
        posY = constrain(posY, 0, 180);

        // Write to servos
        servoX.write(posX);
        servoY.write(posY);

        lastReceiveTime = millis(); // update the last receive time
      }
    }
  }

  // Check if no data received for the timeout duration
  if (millis() - lastReceiveTime > timeout) {
    // Keep the servos at their last position
  }
}
