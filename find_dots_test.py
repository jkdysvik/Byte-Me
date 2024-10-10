def find_dots(imgnr):
    import cv2
    import numpy as np

    image = cv2.imread(imgnr)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Refine the HSV range for green detection
    lower_green = np.array([35, 105, 105])
    upper_green = np.array([120, 255, 255])
    mask_green = cv2.inRange(hsv, lower_green, upper_green)
    cv2.imwrite("mask_green.jpg", mask_green)

    # Adjust the HSV range for red detection
    lower_red1 = np.array([0, 120, 170])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 120, 170])
    upper_red2 = np.array([180, 255, 255])

    mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask_red = cv2.bitwise_or(mask_red1, mask_red2)

    cv2.imwrite("mask_red.jpg", mask_red)

    # Perform morphological operations to close gaps in both masks
    kernel = np.ones((5, 5), np.uint8)
    mask_green = cv2.morphologyEx(mask_green, cv2.MORPH_CLOSE, kernel)
    mask_green = cv2.morphologyEx(mask_green, cv2.MORPH_OPEN, kernel)

    mask_red = cv2.morphologyEx(mask_red, cv2.MORPH_CLOSE, kernel)
    mask_red = cv2.morphologyEx(mask_red, cv2.MORPH_OPEN, kernel)

    # Simplified function to find dots based on contours
    def find_dots(mask, min_contour_area=50):
        contours = cv2.findContours(mask.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[-2]
        print(f"Found {len(contours)} contours")
        dots_coordinates = []

        for contour in contours:
            area = cv2.contourArea(contour)
            print("Contour area:", area)
            if area > min_contour_area:
                M = cv2.moments(contour)
                if M["m00"] != 0:
                    center_x = int(M["m10"] / M["m00"])
                    center_y = int(M["m01"] / M["m00"])
                    dots_coordinates.append((center_x, center_y))
        print("Dots coordinates:", dots_coordinates)
        return dots_coordinates

    # Find green and red dots
    green_dots_coordinates = find_dots(mask_green)
    red_dots_coordinates = find_dots(mask_red)

    # Merge close points for both green and red dots
    # (Assuming you still need this function)
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

    green_dots_coordinates = merge_close_points(green_dots_coordinates)
    print("Merged Green dots:", green_dots_coordinates)
    red_dots_coordinates = merge_close_points(red_dots_coordinates)
    print("Merged Red dots:", red_dots_coordinates)

    # Draw the detected points on the image for visualization
    for coord in green_dots_coordinates:
        cv2.circle(image, coord, 10, (0, 255, 0), -1)  # Draw green dots
    for coord in red_dots_coordinates:
        cv2.circle(image, coord, 10, (0, 0, 255), -1)  # Draw red dots

    # Save the final image with detected dots
    cv2.imwrite("dots_detected.jpg", image)

    # Continue with the rest of your code...


    min_x = min([coord[0] for coord in green_dots_coordinates], default=0)
    max_x = max([coord[0] for coord in green_dots_coordinates], default=1)
    min_y = min([coord[1] for coord in green_dots_coordinates], default=0)
    max_y = max([coord[1] for coord in green_dots_coordinates], default=1)

    edges_x = [min_x + i * (max_x - min_x) / 8 for i in range(9)]
    edges_y = [min_y + i * (max_y - min_y) / 8 for i in range(9)]

    red_dots_location = []

    for dot in red_dots_coordinates:
        x, y = dot
        # Find the row index by comparing y with vertical edges
        row = next(k for k, edge in enumerate(edges_y) if y < edge)
        # Find the column index by comparing x with horizontal edges
        col = next(j for j, edge in enumerate(edges_x) if x < edge)
        red_dots_location.append((col, 8 - row + 1, 1))

    print(red_dots_location)

find_dots("att1.jpg")
