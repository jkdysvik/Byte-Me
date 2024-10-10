import cv2
import numpy as np

class CameraTracker:
    def __init__(self):
        """
        Initialize the camera tracker and store calibration data.
        """
        self.cap = cv2.VideoCapture(0)  # Adjust the index if necessary
        if not self.cap.isOpened():
            raise IOError("Cannot open camera")

        # Calibration storage for the green dots (corners)
        self.green_dots_calibrated = None

    def capture_and_process(self, return_image=False):
        """
        Capture an image from the camera and process it to find piece positions.

        Args:
            return_image (bool): Whether to return the processed image for visualization.

        Returns:
            red_dots_location (list): List of (row, col) tuples indicating positions of red dots.
            image (numpy.ndarray): The processed image with detected dots (if return_image is True).
        """
        ret, image = self.cap.read()
        if not ret:
            print("Failed to capture image")
            return [], None if return_image else []

        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Adjust the HSV range for green detection
        lower_green = np.array([35, 105, 105])
        upper_green = np.array([120, 255, 255])
        mask_green = cv2.inRange(hsv, lower_green, upper_green)

        # Adjust the HSV range for red detection
        lower_red1 = np.array([0, 120, 170])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 120, 170])
        upper_red2 = np.array([180, 255, 255])

        mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask_red = cv2.bitwise_or(mask_red1, mask_red2)

        # Perform morphological operations to close gaps in both masks
        kernel = np.ones((5, 5), np.uint8)
        mask_green = cv2.morphologyEx(mask_green, cv2.MORPH_CLOSE, kernel)
        mask_green = cv2.morphologyEx(mask_green, cv2.MORPH_OPEN, kernel)

        mask_red = cv2.morphologyEx(mask_red, cv2.MORPH_CLOSE, kernel)
        mask_red = cv2.morphologyEx(mask_red, cv2.MORPH_OPEN, kernel)

        # Function to find dots based on contours
        def find_dots(mask, min_contour_area=50):
            contours = cv2.findContours(mask.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[-2]
            dots_coordinates = []

            for contour in contours:
                area = cv2.contourArea(contour)
                if area > min_contour_area:
                    M = cv2.moments(contour)
                    if M["m00"] != 0:
                        center_x = int(M["m10"] / M["m00"])
                        center_y = int(M["m01"] / M["m00"])
                        dots_coordinates.append((center_x, center_y))
            return dots_coordinates

        # Find green and red dots
        green_dots_coordinates = find_dots(mask_green)
        red_dots_coordinates = find_dots(mask_red)

        # If green dots are found and we haven't calibrated yet, do so
        if self.green_dots_calibrated is None and len(green_dots_coordinates) >= 2:
            self.green_dots_calibrated = green_dots_coordinates
            print("Green dots calibrated:", self.green_dots_calibrated)
        
        # Use stored green dots for calibration
        if self.green_dots_calibrated:
            green_dots_coordinates = self.green_dots_calibrated

        # Merge close points for red dots
        def merge_close_points(points, threshold=100):
            merged_points = []
            while points:
                point = points.pop(0)
                close_points = [p for p in points if np.linalg.norm(np.array(point) - np.array(p)) < threshold]
                points = [p for p in points if p not in close_points]
                all_points = [point] + close_points
                avg_x = int(np.mean([p[0] for p in all_points]))
                avg_y = int(np.mean([p[1] for p in all_points]))
                merged_points.append((avg_x, avg_y))
            return merged_points

        red_dots_coordinates = merge_close_points(red_dots_coordinates)

        # Draw the detected points on the image for visualization (optional)
        for coord in green_dots_coordinates:
            cv2.circle(image, coord, 10, (0, 255, 0), -1)  # Draw green dots
        for coord in red_dots_coordinates:
            cv2.circle(image, coord, 10, (0, 0, 255), -1)  # Draw red dots

        # Map the red dots to board positions using the green dots for calibration
        if len(green_dots_coordinates) < 2:
            print("Not enough green dots detected for calibration.")
            return [], image if return_image else []

        min_x = min([coord[0] for coord in green_dots_coordinates], default=0)
        max_x = max([coord[0] for coord in green_dots_coordinates], default=1)
        min_y = min([coord[1] for coord in green_dots_coordinates], default=0)
        max_y = max([coord[1] for coord in green_dots_coordinates], default=1)

        edges_x = [min_x + i * (max_x - min_x) / 8 for i in range(9)]
        edges_y = [min_y + i * (max_y - min_y) / 8 for i in range(9)]

        red_dots_location = []

        for dot in red_dots_coordinates:
            x, y = dot
            row = next((k for k, edge in enumerate(edges_y) if y < edge), 8)
            col = next((j for j, edge in enumerate(edges_x) if x < edge), 8)
            red_dots_location.append((col-1, 8 - row))

        print("Mapped red dots to board positions:", red_dots_location)

        if return_image:
            return red_dots_location, image
        else:
            return red_dots_location

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()
