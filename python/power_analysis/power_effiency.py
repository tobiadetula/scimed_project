import pandas as pd
import matplotlib.pyplot as plt

# Constants
mass_arm = 120  # Mass of the arm in kg
g = 9.81  # Gravitational acceleration in m/s^2
center_of_mass = 0.33  # Center of mass in meters

# Theoretical energy calculation
height_moved = center_of_mass  # Assuming vertical lift is equal to center of mass
E_theoretical = mass_arm * g * height_moved

# Read CSV file
csv_file = '/home/tobiadetula/Documents/PlatformIO/Projects/scimed_project/cumulative_power_test_1kg.csv'
data = pd.read_csv(csv_file)

# Filter out every 20th row
data = data[~((data.index + 1) % 20 == 0)]

# Convert Cumulative Power from mJ to J
data['Cumulative Power (J)'] = data['Cumulative Power (mJ)'] / 1000

# Divide each power measurement by the loop duration
data['Power per Duration (J/s)'] = data['Cumulative Power (J)'] / (data['Loop Duration (ms)']/(1000))

# Calculate efficiency
data['Efficiency (%)'] = (E_theoretical / data['Power per Duration (J/s)']) * 100

# Plot efficiency
plt.plot(data['Move'], data['Efficiency (%)'], marker='o')
plt.xlabel('Move')
plt.ylabel('Efficiency (%)')
plt.title('Power Efficiency')
plt.grid(True)
plt.show()