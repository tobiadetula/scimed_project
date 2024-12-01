import serial as serial_log # Import the pyserial library
import csv
import re

# Configure the serial port
ser = serial_log.Serial('/dev/ttyACM0', 115200, timeout=1)

# Open the CSV file in append mode
with open('data.csv', 'a', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    
    # Write the header if the file is empty
    if csvfile.tell() == 0:
        csvwriter.writerow(['Bus Voltage (V)', 'Shunt Voltage (mV)', 'Load Voltage (V)', 'Current (mA)', 'Power (mW)'])
    
    while True:
        line = ser.readline().decode('utf-8').strip()
        if line:
            # Use regular expressions to extract the values
            match = re.match(r'Bus Voltage:\s+([\d.]+)\s+V', line)
            if match:
                bus_voltage = float(match.group(1))
                shunt_voltage_match = re.search(r'Shunt Voltage:\s+([\d.]+)\s+mV', ser.readline().decode('utf-8').strip())
                load_voltage_match = re.search(r'Load Voltage:\s+([\d.]+)\s+V', ser.readline().decode('utf-8').strip())
                current_mA_match = re.search(r'Current:\s+([\d.]+)\s+mA', ser.readline().decode('utf-8').strip())
                power_mW_match = re.search(r'Power:\s+([\d.]+)\s+mW', ser.readline().decode('utf-8').strip())

                if shunt_voltage_match and load_voltage_match and current_mA_match and power_mW_match:
                    shunt_voltage = float(shunt_voltage_match.group(1))
                    load_voltage = float(load_voltage_match.group(1))
                    current_mA = float(current_mA_match.group(1))
                    power_mW = float(power_mW_match.group(1))
                else:
                    continue
                
                # Print the values
                print(f'Bus Voltage: {bus_voltage} V, Shunt Voltage: {shunt_voltage} mV, Load Voltage: {load_voltage} V, Current: {current_mA} mA, Power: {power_mW} mW')
                
                # Append the values to the CSV file
                csvwriter.writerow([bus_voltage, shunt_voltage, load_voltage, current_mA, power_mW])
                csvfile.flush()
                # Check for cumulative power
                move_line = ser.readline().decode('utf-8').strip()
                move_match = re.match(r'Move:\s+(\d+),\s+Cumulative Power:\s+([\d.]+)\s+mJ,\s+Loop Duration:\s+(\d+)\s+ms', move_line)
                if move_match:
                    move = int(move_match.group(1))
                    cumulative_power = float(move_match.group(2))
                    loop_duration = int(move_match.group(3))
                    
                    # Open the cumulative power CSV file in append mode
                    with open('cumulative_power.csv', 'a', newline='') as cumulative_csvfile:
                        cumulative_csvwriter = csv.writer(cumulative_csvfile)
                        
                        # Write the header if the file is empty
                        if cumulative_csvfile.tell() == 0:
                            cumulative_csvwriter.writerow(['Move', 'Cumulative Power (mJ)', 'Loop Duration (ms)'])
                        
                        # Append the values to the CSV file
                        cumulative_csvwriter.writerow([move, cumulative_power, loop_duration])
                        cumulative_csvfile.flush()