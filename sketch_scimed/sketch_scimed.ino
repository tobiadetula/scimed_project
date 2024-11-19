#include <Arduino.h>
#include <AccelStepper.h>
#include <Wire.h>
#include <Adafruit_INA219.h>
#include <pico/multicore.h>

// Define stepper motor and driver pins
#define DIR_PIN 2   // Direction pin
#define STEP_PIN 3  // Step pin

// Create an INA219 instance
Adafruit_INA219 ina219;

// Initialize AccelStepper with DRIVER mode
AccelStepper stepper(AccelStepper::DRIVER, STEP_PIN, DIR_PIN);

volatile bool motorFinished = false;
volatile bool motorStatusNotified = false;

float shuntvoltage = 0;
float busvoltage = 0;
float current_mA = 0;
float loadvoltage = 0;
float power_mW = 0;

float cumulativePower = 0;
unsigned long motorStartTime = 0;
unsigned long motorRunTime = 0;

int motor_positions = 300;
int experimentduration = 1; // Time in secs
static int iterationCounter = 0;

// Function declarations
void setup_ina219();
void read_ina219();
void blink_led(int times, int delay_ms);
void print_ina219();
void print_ina219_csv();
void check_motor_status();
void notify_motor_status();
void update_cumulative_power();
void update_motor_run_time();


void setup() {
    // Core 0 setup
    stepper.setMaxSpeed(500);      // Maximum speed in steps per second
    stepper.setAcceleration(250);  // Acceleration in steps per second squared
    stepper.setCurrentPosition(0); // Set initial position
}

void loop() {
    // Motor control logic
    iterationCounter++;
    if (iterationCounter == 5){
      experimentduration = 15;
      iterationCounter = 0;
    }
    else {
    experimentduration = 1;
    }
    motorFinished = false;
    stepper.moveTo(motor_positions);

    // Run the motor until it reaches the target position
    while (stepper.distanceToGo() != 0) {
        stepper.run();
    }

    delay(experimentduration*1000); // Pause for 5 second

    // Move back to the starting position
    stepper.moveTo(-motor_positions);

    // Run the motor until it reaches the target position
    while (stepper.distanceToGo() != 0) {
        stepper.run();
    }
        
    delay(experimentduration*1000); // Pause for 5 second


    check_motor_status();
    update_motor_run_time();

    // Notify core 1 about motor status
    if (motorFinished) {
        rp2040.fifo.push(1);
    } else {
        rp2040.fifo.push(0);
    }
}

void setup1() {
    // Core 1 setup
    Serial.begin(115200);
    delay(5000);  // Wait for serial monitor to open
    Serial.printf("SciMed Arduino Application Started!\n");
    pinMode(LED_BUILTIN, OUTPUT);
    setup_ina219();
}
void loop1() {
        // Current measurement logic
        read_ina219();
        print_ina219();
        blink_led(2, 100);  // Blink twice every time data is sent
        notify_motor_status();
        update_cumulative_power();

        uint32_t motorStatus;
        if (rp2040.fifo.pop_nb(&motorStatus)) {
            if (motorStatus == 1) {
                Serial.printf("Motor has finished moving.\n");
                motorStatusNotified = true;
                }
        }

        if (motorStatusNotified) {
            Serial.printf("Cumulative Power: %.2f mJ\n", cumulativePower);
            print_motor_run_time();
            cumulativePower = 0;
            motorStatusNotified = false;

        }

        delay(1000);
    }


void setup_ina219() {
    Serial.printf("Measuring voltage and current with INA219 ...\n");
    if (!ina219.begin()) {
        Serial.printf("Failed to find INA219 chip\n");
        while (1) {
            blink_led(1, 1000);  // Blink slowly if INA219 is not found
        }
    }
}

void read_ina219() {
    shuntvoltage = ina219.getShuntVoltage_mV();
    busvoltage = ina219.getBusVoltage_V();
    current_mA = ina219.getCurrent_mA();
    power_mW = ina219.getPower_mW();
    loadvoltage = busvoltage + (shuntvoltage / 1000);
}

void print_ina219() {
    Serial.printf("Bus Voltage:   %.2f V\n", busvoltage);
    Serial.printf("Shunt Voltage: %.2f mV\n", shuntvoltage);
    Serial.printf("Load Voltage:  %.2f V\n", loadvoltage);
    Serial.printf("Current:       %.2f mA\n", current_mA);
    Serial.printf("Power:         %.2f mW\n\n", power_mW);
}

void blink_led(int times, int delay_ms) {
    for (int i = 0; i < times; i++) {
        digitalWrite(LED_BUILTIN, HIGH);
        delay(delay_ms);
        digitalWrite(LED_BUILTIN, LOW);
        delay(delay_ms);
    }
}

void check_motor_status() {
    if (stepper.distanceToGo() == 0) {
        motorFinished = true;
    }
}

void notify_motor_status() {
    if (motorFinished && !motorStatusNotified) {
        Serial.printf("Motor has finished moving.\n");
        motorStatusNotified = true;
    }
}

void update_cumulative_power() {
    static unsigned long lastUpdateTime = 0;  // Tracks the last update time
    unsigned long currentTime = millis();

    if (!motorFinished) {
        // Accumulate power if the motor is running
        if (lastUpdateTime > 0) {
            cumulativePower += power_mW * (currentTime - lastUpdateTime) / 1000.0; // Convert to mJ
        }
        lastUpdateTime = currentTime;
    } else {
        // Reset update time when motor stops
        lastUpdateTime = 0;
    }
}

void update_motor_run_time() {
    static unsigned long startTime = 0;
    if (!motorFinished) {
        if (startTime == 0) {
            startTime = millis();  // Record start time
        }
    } else {
        if (startTime != 0) {
            motorRunTime += millis() - startTime;  // Accumulate run time
            startTime = 0;  // Reset for the next run
        }
    }
}


void print_motor_run_time() {
    Serial.printf("Motor Run Time: %lu ms\n", motorRunTime);
}