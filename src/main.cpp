#include <Arduino.h>
#include <AccelStepper.h>
#include <Wire.h>
#include <Adafruit_INA219.h>
#include <Stepper.h>
#include "pinDefinitions.h"

// Create an INA219 instance
Adafruit_INA219 ina219;

// Initialize AccelStepper with DRIVER mode
AccelStepper stepper(AccelStepper::DRIVER, STEP_PIN, DIR_PIN);

// // NOTE: The sequence 1-3-2-4 is required for proper sequencing of 28BYJ-48
// AccelStepper stepper1(AccelStepper::HALF4WIRE, motorPin1, motorPin3, motorPin2, motorPin4);

int endPoint = 1024; // Move this many steps - 1024 = approx 1/4 turn

float shuntvoltage = 0;
float busvoltage = 0;
float current_mA = 0;
float loadvoltage = 0;
float power_mW = 0;

// put function declarations here:
int setup_ina219();
int read_ina219();
int print_ina219();

void setup()
{
  pinMode(ENABLE_PIN, OUTPUT);
  Serial.begin(115200);
  while (!Serial)
  {
    // will pause Zero, Leonardo, etc until serial console opens
    delay(1);
  }

  Serial.println("SciMed Arduino Application Started!");
  digitalWrite(ENABLE_PIN, HIGH);
  // Set the maximum speed and acceleration for the stepper motor
  Serial.println("Setting up stepper motor");
  stepper.setMaxSpeed(1000);    // Maximum speed in steps per second
  stepper.setAcceleration(500); // Acceleration in steps per second squared

  // Set initial position
  stepper.setCurrentPosition(0);

  // stepper1.setMaxSpeed(200.0);
  // stepper1.setAcceleration(100.0);
  // stepper1.setSpeed(10);
  // stepper1.moveTo(endPoint);

  setup_ina219();
}

void loop()
{
  // Change direction at the limits
  // if (stepper.distanceToGo() == 0)
  //   stepper.moveTo(-stepper.currentPosition());
  // stepper.run();
  // stepper.runSpeed();

  // Change direction at the limits
  //    if (stepper1.distanceToGo() == 0)
  //   {
  //     Serial.println(stepper1.currentPosition());
  //     stepper1.setCurrentPosition(0);
  //     endPoint = -endPoint;
  //     stepper1.moveTo(endPoint);
  //     Serial.println(stepper1.currentPosition());
  //   }
  //    stepper1.run();

  // Move to 1000 steps in one direction
  stepper.moveTo(10000);

  // Run the motor until it reaches the target position
  while (stepper.distanceToGo() != 0)
  {
    stepper.run();
  }

  delay(1000); // Pause for 1 second

  // Move back to the starting position
  stepper.moveTo(0);

  // Run the motor until it reaches the target position
  while (stepper.distanceToGo() != 0)
  {
    stepper.run();
  }

  delay(1000); // Pause for 1 second

  print_ina219();
  read_ina219();
  delay(1000);
}

int setup_ina219()
{

  // Initialize the INA219.
  // By default the initialization will use the largest range (32V, 2A).  However
  // you can call a setCalibration function to change this range (see comments).
  Serial.println("Measuring voltage and current with INA219 ...");
  if (!ina219.begin())
  {
    Serial.println("Failed to find INA219 chip");
    while (1)
    {
      delay(10);
    }
  }
  // To use a slightly lower 32V, 1A range (higher precision on amps):
  // ina219.setCalibration_32V_1A();
  // Or to use a lower 16V, 400mA range (higher precision on volts and amps):
  // ina219.setCalibration_16V_400mA();

  Serial.println("Measuring voltage and current with INA219 ...");
} // end setup_ina219

int read_ina219()
{
  shuntvoltage = ina219.getShuntVoltage_mV();
  busvoltage = ina219.getBusVoltage_V();
  current_mA = ina219.getCurrent_mA();
  power_mW = ina219.getPower_mW();
  loadvoltage = busvoltage + (shuntvoltage / 1000);
}

int print_ina219()
{
  Serial.print("Bus Voltage:   ");
  Serial.print(busvoltage);
  Serial.println(" V");
  Serial.print("Shunt Voltage: ");
  Serial.print(shuntvoltage);
  Serial.println(" mV");
  Serial.print("Load Voltage:  ");
  Serial.print(loadvoltage);
  Serial.println(" V");
  Serial.print("Current:       ");
  Serial.print(current_mA);
  Serial.println(" mA");
  Serial.print("Power:         ");
  Serial.print(power_mW);
  Serial.println(" mW");
  Serial.println("");
}