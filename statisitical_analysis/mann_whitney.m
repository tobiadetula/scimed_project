% Load the datasets
data_capstan = readtable('distances_capstan_2kg.csv');
data_planetary = readtable('distances_planetary_2kg.csv');

% Extract the 'Distance from Initial Point' column
distances_capstan = data_capstan{1:end-1, 1};
distances_planetary = data_planetary{:, 1};

% Perform the Mann-Whitney U test
[p, h, stats] = ranksum(distances_capstan, distances_planetary);

% Display the results
if h == 0
    fprintf('The distributions are not significantly different (p = %.4f).\n', p);
else
    fprintf('The distributions are significantly different (p = %.4f).\n', p);
end

% Determine which system has higher accuracy
mean_capstan = mean(distances_capstan);
mean_planetary = mean(distances_planetary);

if mean_capstan < mean_planetary
    fprintf('The capstan system has higher accuracy.\n');
else
    fprintf('The planetary system has higher accuracy.\n');
end

% Plot the data
figure;
subplot(1, 2, 1);
boxplot([distances_capstan, distances_planetary], 'Labels', {'Capstan', 'Planetary'});
title('Boxplot of Distances');
ylabel('Distance from Initial Point (mm)');

subplot(1, 2, 2);
histogram(distances_capstan, 'Normalization', 'probability');
hold on;
histogram(distances_planetary, 'Normalization', 'probability');
hold off;
legend('Capstan', 'Planetary');
title('Histogram of Distances');
xlabel('Distance from Initial Point (mm)');
ylabel('Probability');