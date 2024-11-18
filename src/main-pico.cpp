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


float shuntvoltage = 0;
float busvoltage = 0;
float current_mA = 0;
float loadvoltage = 0;
float power_mW = 0;

// Function declarations
int setup_ina219();
int read_ina219();
int print_ina219();
void print_ina219_csv();

void setup() {
    Serial.begin(115200);
    while (!Serial) {
        // will pause Zero, Leonardo, etc until serial console opens
        delay(1);
    }

  Serial.println("SciMed Arduino Application Started!");
  // Set the maximum speed and acceleration for the stepper motor
  Serial.println("Setting up stepper motor");

  stepper.setMaxSpeed(20000);    // Maximum speed in steps per second
  stepper.setAcceleration(10000); // Acceleration in steps per second squared
  // Set initial position
  stepper.setCurrentPosition(0);

}

void loop() {
    // Motor control logic
        if (stepper.distanceToGo() == 0)
    {
      // Move to the next position
      if (stepper.currentPosition() == 0)
      {
        stepper.moveTo(10000);
      }
      else
      {
        stepper.moveTo(0);
      }
    }
      stepper.run();


}

void setup1() {
    // Setup for core 1
        setup_ina219();

}

void loop1() {
    // Current measurement logic
    read_ina219();
    print_ina219();
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
  return 0;
} // end setup_ina219

int read_ina219()
{
  shuntvoltage = ina219.getShuntVoltage_mV();
  busvoltage = ina219.getBusVoltage_V();
  current_mA = ina219.getCurrent_mA();
  power_mW = ina219.getPower_mW();
  loadvoltage = busvoltage + (shuntvoltage / 1000);
  return 0;
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
  return 0;
}

void print_ina219_csv()
{
  static bool firstRun = true;
  if (firstRun)
  {
    Serial.println("Bus Voltage (V),Shunt Voltage (mV),Load Voltage (V),Current (mA),Power (mW)");
    firstRun = false;
  }
  Serial.print(busvoltage);
  Serial.print(",");
  Serial.print(shuntvoltage);
  Serial.print(",");
  Serial.print(loadvoltage);
  Serial.print(",");
  Serial.print(current_mA);
  Serial.print(",");
  Serial.print(power_mW);
  Serial.println();
}