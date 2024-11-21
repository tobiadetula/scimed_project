import os
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
from math import sqrt
import csv
import cv2


def crop_image(image_path):
    """
    Crop the image to the area of the grey sheet used for plotting.
    """
    image = cv2.imread(image_path)
    original = image.copy()

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Use Canny edge detection
    edges = cv2.Canny(blurred, 50, 150)

    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Find the largest contour
    contour = max(contours, key=cv2.contourArea)

    # Approximate the contour to a polygon
    epsilon = 0.02 * cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, epsilon, True)

    # If the contour has four corners, it is likely the paper
    if len(approx) == 4:
        # Rearrange the points for perspective transformation
        points = approx.reshape(4, 2)
        rect = np.zeros((4, 2), dtype="float32")

        # Top-left point has the smallest sum, bottom-right has the largest sum
        s = points.sum(axis=1)
        rect[0] = points[np.argmin(s)]
        rect[2] = points[np.argmax(s)]

        # Top-right point has the smallest difference, bottom-left has the largest difference
        diff = np.diff(points, axis=1)
        rect[1] = points[np.argmin(diff)]
        rect[3] = points[np.argmax(diff)]

        # Compute the width and height of the new image
        (tl, tr, br, bl) = rect
        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        maxWidth = max(int(widthA), int(widthB))

        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        maxHeight = max(int(heightA), int(heightB))

        # Define the destination points
        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]
        ], dtype="float32")

        # Perform the perspective transformation
        M = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(original, M, (maxWidth, maxHeight))

        return warped
    else:
        print("The paper was not detected correctly. Returning the original image.")
        return original

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

    return int(x), int(y)
    

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
    distances = [
        calculate_distance(initial_point, point) * pixel_to_mm_ratio for point in red_points
    ]
    
    # Annotate images and save them
    for i, (image_path, point, distance) in enumerate(zip(images, red_points, distances)):
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
        writer.writerow(["Image", "Red Point (x, y)", "Distance from Initial Point (mm)"])
        for i, (image, point, distance) in enumerate(zip(images, red_points, distances)):
            writer.writerow([os.path.basename(image), point, distance])
    
    # Print results
    for i, (image, point, distance) in enumerate(zip(images, red_points, distances)):
        print(f"Image {i + 1}: {os.path.basename(image)}")
        print(f"  Red Point: {point}")
        print(f"  Distance from Initial Point: {distance:.2f} mm")
    return red_points, distances

# Replace 'your_directory_path_here' with the path to your images folder
image_directory = "./actual_test/planetary_gear/test_1kg/cropped_images"
# Assuming each pixel represents 0.1 mm
pixel_to_mm_ratio = 0.1
process_images(image_directory, pixel_to_mm_ratio)
