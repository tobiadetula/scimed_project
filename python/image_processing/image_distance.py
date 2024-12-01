import os
from PIL import Image, ImageDraw
import numpy as np
from math import sqrt
import csv

def find_red_point(image_path):
    """
    Locate the brightest red point in the image.
    Returns the coordinates (x, y) of the point.
    """
    image = Image.open(image_path)
    # Convert to numpy array for pixel-level analysis
    img_array = np.array(image)
    
    # Extract RGB channels
    red_channel = img_array[..., 0]
    green_channel = img_array[..., 1]
    blue_channel = img_array[..., 2]
    
    # Find red-intensity by reducing interference of green/blue
    red_intensity = red_channel - (green_channel + blue_channel) / 2.0
    
    # Locate the brightest red point
    y, x = np.unravel_index(np.argmax(red_intensity), red_intensity.shape)
    return x, y

def calculate_distance(point1, point2):
    """
    Calculate the Euclidean distance between two points.
    """
    return sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

def process_images(directory, pixel_to_mm_ratio):
    """
    Process all images in the given directory, calculate the red point
    and distances from the first red point, and annotate images.
    """
    # Get a list of image paths sorted by name
    images = sorted(
        [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(".png")]
    )
    
    if not images:
        print("No images found in the directory.")
        return
    
    # Find red points in all images
    red_points = [find_red_point(image) for image in images]
    
    # Calculate distances from the first red point
    initial_point = red_points[0]
    distances_from_initial = [
        calculate_distance(initial_point, point) * pixel_to_mm_ratio for point in red_points
    ]
    
    # Calculate distances between consecutive points
    distances_between_points = [
        calculate_distance(red_points[i], red_points[i + 1]) * pixel_to_mm_ratio
        for i in range(len(red_points) - 1)
    ]
    distances_between_points.insert(0, 0)  # No distance for the first point
    
    # Annotate images and save them
    for i, (image_path, point, distance) in enumerate(zip(images, red_points, distances_from_initial)):
        image = Image.open(image_path)
        draw = ImageDraw.Draw(image)
        draw.ellipse((point[0] - 5, point[1] - 5, point[0] + 5, point[1] + 5), outline="red", width=2)
        draw.text((point[0] + 10, point[1]), f"{i + 1}", fill="red")
        draw.text((10, 10), f"Distance from Initial Point: {distance:.2f} mm", fill="red")
        image.save(os.path.join(directory, f"annotated_image_{i + 1}.png"))
    
    # Create a final image with all points annotated
    final_image = Image.open(images[0]).convert("RGBA")
    final_draw = ImageDraw.Draw(final_image)
    for i, point in enumerate(red_points):
        final_draw.ellipse((point[0] - 5, point[1] - 5, point[0] + 5, point[1] + 5), outline="red", width=2)
        final_draw.text((point[0] + 10, point[1]), f"{i + 1}", fill="red")
    final_image.save(os.path.join(directory, "final_annotated_image.png"))
    
    # Save distances to a CSV file
    csv_path = os.path.join(directory, "distances.csv")
    with open(csv_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Image", "Red Point (x, y)", "Distance from Initial Point (mm)", "Distance from Previous Point (mm)"])
        for i, (image, point, distance_from_initial, distance_between) in enumerate(zip(images, red_points, distances_from_initial, distances_between_points)):
            writer.writerow([os.path.basename(image), f"({point[0]}, {point[1]})", f"{distance_from_initial:.2f}", f"{distance_between:.2f}"])
    
    # Print results
    for i, (image, point, distance_from_initial, distance_between) in enumerate(zip(images, red_points, distances_from_initial, distances_between_points)):
        print(f"Image {i + 1}: {os.path.basename(image)}")
        print(f"  Red Point: ({point[0]}, {point[1]})")
        print(f"  Distance from Initial Point: {distance_from_initial:.2f} mm")
        print(f"  Distance from Previous Point: {distance_between:.2f} mm")
    return red_points, distances_from_initial

# Replace 'your_directory_path_here' with the path to your images folder
image_directory = "actual_test/capstan_drive/test_2kg"
# Assuming each pixel represents 0.1 mm
pixel_to_mm_ratio = 0.1
process_images(image_directory, pixel_to_mm_ratio)