#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

#define SERVO_CLAW 0
#define SERVO_BASE 1
#define SERVO_ARM  2

int clawPos = 300, basePos = 375, armPos = 300;

void setup() {
  Serial.begin(9600);
  pwm.begin();
  pwm.setPWMFreq(50);  
  moveServo(SERVO_CLAW, clawPos);
  moveServo(SERVO_BASE, basePos);
  moveServo(SERVO_ARM, armPos);
}

void loop() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    if (cmd == "OPEN") clawPos = 250;
    else if (cmd == "CLOSE") clawPos = 400;
    else if (cmd == "BASE_LEFT") basePos = constrain(basePos - 5, 250, 500);
    else if (cmd == "BASE_RIGHT") basePos = constrain(basePos + 5, 250, 500);
    else if (cmd == "FORWARD") armPos = constrain(armPos + 5, 250, 500);
    else if (cmd == "BACKWARD") armPos = constrain(armPos - 5, 250, 500);
    else if (cmd == "RESET") basePos = 375;
    else if (cmd == "ARM_UP") armPos = constrain(armPos - 3, 250, 500);
    else if (cmd == "ARM_DOWN") armPos = constrain(armPos + 3, 250, 500);

    // Smooth move
    moveServoSmooth(SERVO_CLAW, clawPos);
    moveServoSmooth(SERVO_BASE, basePos);
    moveServoSmooth(SERVO_ARM, armPos);
  }
}

void moveServo(int servo, int pos) {
  pwm.setPWM(servo, 0, pos);
}

void moveServoSmooth(int servo, int target) {
  static int current[3] = {300, 375, 300};
  while (current[servo] != target) {
    if (current[servo] < target) current[servo]++;
    else if (current[servo] > target) current[servo]--;
    pwm.setPWM(servo, 0, current[servo]);
    delay(5);  // speed control
  }
}
