% Load the datasets from the CSV files
% data1 = readtable('/home/tobiadetula/Documents/PlatformIO/Projects/scimed_project/distances_planetary_2kg.csv');
% data2 = readtable('/home/tobiadetula/Documents/PlatformIO/Projects/scimed_project/distances_planetary_1kg.csv');
% data3 = readtable('/home/tobiadetula/Documents/PlatformIO/Projects/scimed_project/distances_capstan_2kg.csv');
% data4 = readtable('/home/tobiadetula/Documents/PlatformIO/Projects/scimed_project/distances_capstan_1kg.csv');

% Extract the distance column (assuming the first column contains distances)
distances1 = data1{:, 1};
distances2 = data2{:, 1};
distances3 = data3{:, 1};
distances4 = data4{:, 1};

% Combine the distances into a matrix
combined_distances = [distances1, distances2, distances3, distances4];

% Create a box plot
figure;
boxplot(combined_distances, 'Labels', {'Planetary 2kg', 'Planetary 1kg', 'Capstan 2kg', 'Capstan 1kg'});
title('Box Plot of Distances from Initial Point');
xlabel('Dataset');
ylabel('Distance from Initial Point (mm)');

% Create the matrix plot
figure;
plotmatrix(combined_distances);

% Label the axes
xlabel('Dataset');
ylabel('Dataset');
title('Matrix Plot of Distances from Initial Point');

% Optionally, set axis labels for better clarity
xticklabels({'Planetary 2kg', 'Planetary 1kg', 'Capstan 2kg', 'Capstan 1kg'});
yticklabels({'Planetary 2kg', 'Planetary 1kg', 'Capstan 2kg', 'Capstan 1kg'});