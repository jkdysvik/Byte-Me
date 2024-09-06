def find_dots(imgnr):
    import cv2
    import numpy as np

    image = cv2.imread("IMG_" + imgnr + ".jpg")
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Adjust the HSV range for green detection (more restrictive)
    lower_green = np.array([40, 50, 50])  # Increased the minimum saturation and value
    upper_green = np.array([80, 255, 255])
    mask_green = cv2.inRange(hsv, lower_green, upper_green)

    # Adjust the HSV range for red detection (red spans around the hue 0/180 boundary)
    lower_red1 = np.array([0, 70, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 70, 50])
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

    # Function to find and filter dots based on color and contour area
    def find_dots(mask, lower_hue, upper_hue, min_contour_area=100):
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        dots_coordinates = []

        for contour in contours:
            if cv2.contourArea(contour) > min_contour_area:
                # Calculate the average color of the contour in the original image
                mask_temp = np.zeros(mask.shape, np.uint8)
                cv2.drawContours(mask_temp, [contour], -1, 255, -1)
                mean_val = cv2.mean(image, mask=mask_temp)

                # Convert mean color to HSV
                mean_hsv = cv2.cvtColor(np.uint8([[mean_val[:3]]]), cv2.COLOR_BGR2HSV)[0][0]

                # Ensure the average color is within the correct range
                if lower_hue <= mean_hsv[0] <= upper_hue:
                    M = cv2.moments(contour)
                    if M["m00"] != 0:
                        center_x = int(M["m10"] / M["m00"])
                        center_y = int(M["m01"] / M["m00"])
                        dots_coordinates.append((center_x, center_y))

        return dots_coordinates

    # Find green and red dots
    green_dots_coordinates = find_dots(mask_green, lower_green[0], upper_green[0])
    red_dots_coordinates = find_dots(mask_red, lower_red1[0], upper_red2[0])

    def merge_close_points(points, threshold=50):
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

    # Merge close points for both green and red dots
    green_dots_coordinates = merge_close_points(green_dots_coordinates)
    red_dots_coordinates = merge_close_points(red_dots_coordinates)



    # Optional: draw the detected points on the image for visualization
    for coord in green_dots_coordinates:
        cv2.circle(image, coord, 10, (0, 255, 0), -1)  # Draw green dots on the detected points
    for coord in red_dots_coordinates:
        cv2.circle(image, coord, 10, (0, 0, 255), -1)  # Draw red dots on the detected points

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
        red_dots_location.append((col, 8 - row+1, 1))

    return red_dots_location