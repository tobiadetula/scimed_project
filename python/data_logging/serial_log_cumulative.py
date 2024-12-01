import serial  # Import the pyserial library
import csv
import re

# Configure the serial port
ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)

try:
    # Open the cumulative power CSV file in append mode
    with open('cumulative_power.csv', 'a', newline='') as cumulative_csvfile:
        cumulative_csvwriter = csv.writer(cumulative_csvfile)
        
        # Write the header if the file is empty
        if cumulative_csvfile.tell() == 0:
            cumulative_csvwriter.writerow(['Move', 'Cumulative Power (mJ)', 'Loop Duration (ms)'])
        # Forward serial data to terminal
        while True:
            line = ser.readline().decode('utf-8').strip()
            if line:
                # Use regular expressions to extract the values
                # print(line)
                match = re.match(r'Move:\s+(\d+),\s+Cumulative Power:\s+([\d.]+)\s+W,\s+Loop Duration:\s+(\d+)\s+ms', line)
                if match:
                    move = int(match.group(1))
                    cumulative_power = float(match.group(2))
                    loop_duration = int(match.group(3))
                                      
                    # Print the values
                    print(f'Move: {move}, Cumulative Power: {cumulative_power} mJ, Loop Duration: {loop_duration} ms')
                    
                    # Append the values to the CSV file
                    cumulative_csvwriter.writerow([move, cumulative_power, loop_duration])
                    cumulative_csvfile.flush()
except KeyboardInterrupt:
    print("Program interrupted by user")
finally:
    ser.close()
    print("Serial connection closed")
