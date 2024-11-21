import cv2
import numpy as np
import os
from datetime import datetime
import matplotlib.pyplot as plt

def load_and_preprocess_image(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    return image, edges

def find_largest_contour(edges):
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        return max(contours, key=cv2.contourArea)
    return None

def get_perspective_transform(contour):
    epsilon = 0.02 * cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, epsilon, True)
    if len(approx) == 4:
        points = approx.reshape(4, 2)
        rect = np.zeros((4, 2), dtype="float32")
        s = points.sum(axis=1)
        rect[0] = points[np.argmin(s)]
        rect[2] = points[np.argmax(s)]
        diff = np.diff(points, axis=1)
        rect[1] = points[np.argmin(diff)]
        rect[3] = points[np.argmax(diff)]
        return rect
    return None

def warp_image(image, rect):
    (tl, tr, br, bl) = rect
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]
    ], dtype="float32")
    M = cv2.getPerspectiveTransform(rect, dst)
    return cv2.warpPerspective(image, M, (maxWidth, maxHeight))

def process_image(image_path, output_path):
    image, edges = load_and_preprocess_image(image_path)
    contour = find_largest_contour(edges)
    if contour is not None:
        rect = get_perspective_transform(contour)
        if rect is not None:
            warped = warp_image(image, rect)
            cv2.imwrite(output_path, warped)
            print(f"Cropped image saved at {output_path}")
            return warped
    print(f"The paper in {image_path} was not detected correctly. Try adjusting parameters or preprocessing.")
    return None

def process_images_in_directory(directory):
    image_files = [f for f in os.listdir(directory) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    output_directory = os.path.join(directory, 'cropped_images')
    os.makedirs(output_directory, exist_ok=True)
    for image_file in image_files:
        image_path = os.path.join(directory, image_file)
        output_path = os.path.join(output_directory, image_file)
        process_image(image_path, output_path)

def main():
    directory = 'actual_test/planetary_gear/test_1kg'
    process_images_in_directory(directory)

if __name__ == "__main__":
    main()
