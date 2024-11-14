#include <Arduino.h>
#include <AccelStepper.h>
#include <Wire.h>
#include <Adafruit_INA219.h>
#include <Stepper.h>

// #define ACCEL_STEPPER
#define ULN2003_STEPPER


// Create an INA219 instance
Adafruit_INA219 ina219;

#ifdef ACCEL_STEPPER
// Define some steppers and the pins the will use
AccelStepper stepper(AccelStepper::DRIVER, 6, 7);
// AccelStepper stepper2(AccelStepper::FULL4WIRE, 8, 9, 10, 11);
#endif

#ifdef ULN2003_STEPPER
// Defines the number of steps per rotation
const int stepsPerRevolution = 2038;
// Creates an instance of stepper class
// Pins entered in sequence IN1-IN3-IN2-IN4 for proper step sequence
Stepper myStepper = Stepper(stepsPerRevolution, 8, 10, 9, 11);
#endif

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
  Serial.begin(115200);
  while (!Serial)
  {
    // will pause Zero, Leonardo, etc until serial console opens
    delay(1);
  }

  Serial.println("SciMed Arduino Application Started!");
  // stepper.setMaxSpeed(200.0);
  // stepper.setAcceleration(100.0);
  // // stepper.setSpeed(50);
  // stepper.moveTo(24);


  // stepper2.setMaxSpeed(300.0);
  // stepper2.setAcceleration(100.0);
  // stepper2.moveTo(1000000);


  setup_ina219();
}

void loop()
{
  // Change direction at the limits
  // if (stepper.distanceToGo() == 0)
  //   stepper.moveTo(-stepper.currentPosition());
  // stepper.run();
  // stepper.runSpeed();

	// Rotate CW slowly at 5 RPM
	// myStepper.setSpeed(5);
	// myStepper.step(stepsPerRevolution);

  print_ina219();
  read_ina219();
  delay(1000);
}

int setup_ina219()
{

  // Initialize the INA219.
  // By default the initialization will use the largest range (32V, 2A).  However
  // you can call a setCalibration function to change this range (see comments).
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