import cv2
import numpy as np
import matplotlib.pyplot as plt

def detect_and_crop_largest_grid(image_path, output_path):
    # Load the image
    image = cv2.imread(image_path)
    original = image.copy()

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Threshold the image to make grid lines prominent
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Initialize variables for the largest grid
    largest_area = 0
    best_contour = None

    # Loop through contours to find the largest grid-like rectangle
    for contour in contours:
        # Approximate contour to a polygon
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)

        # Check if the contour has four corners (rectangle)
        if len(approx) == 4:
            # Compute the area of the contour
            area = cv2.contourArea(contour)
            if area > largest_area:
                largest_area = area
                best_contour = approx

    if best_contour is not None:
        # Rearrange points for perspective transformation
        points = best_contour.reshape(4, 2)
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

        # Save and display the result
        cv2.imwrite(output_path, warped)
        plt.imshow(cv2.cvtColor(warped, cv2.COLOR_BGR2RGB))
        plt.title("Cropped Grid")
        plt.axis("off")
        plt.show()
        print(f"Cropped grid saved to {output_path}")
    else:
        print("No suitable grid was detected.")

# Paths
image_path = './2.png'
output_path = './2_c.png'

# Run the function
detect_and_crop_largest_grid(image_path, output_path)
