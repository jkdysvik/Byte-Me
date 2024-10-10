import cv2

class CameraCapture:
    def __init__(self, camera_index=0):
        """
        Initialize the camera capture using the Logitech BRIO webcam.

        Args:
            camera_index (int): Index of the camera to use. Defaults to 0.
        """
        self.camera_index = camera_index
        self.cap = cv2.VideoCapture(self.camera_index)

        if not self.cap.isOpened():
            raise IOError(f"Cannot open camera with index {self.camera_index}")

        # Optionally set camera resolution (BRIO supports high resolutions)
        # Uncomment and adjust the resolution if needed
        # self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        # self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    def capture_and_show(self):
        """
        Capture a single image from the camera and display it in a window.
        """
        ret, frame = self.cap.read()
        if not ret:
            print("Failed to capture image")
            return False

        # Display the image in a window
        cv2.imshow('Captured Image', frame)
        print("Press any key in the image window to close.")

        # Wait indefinitely until a key is pressed
        cv2.waitKey(0)

        # Close the window
        cv2.destroyAllWindows()
        return True

    def release(self):
        """Release the camera resource."""
        self.cap.release()
        cv2.destroyAllWindows()

    @staticmethod
    def test_camera_indices(max_index=10):
        """
        Test available camera indices.

        Args:
            max_index (int): Maximum camera index to test. Defaults to 10.
        """
        available_indices = []
        for idx in range(max_index):
            cap = cv2.VideoCapture(idx)
            if cap.isOpened():
                print(f"Camera index {idx} is available.")
                cap.release()
                available_indices.append(idx)
        if not available_indices:
            print("No camera indices found.")
        return available_indices

# Example usage
if __name__ == "__main__":
    # Test available camera indices
    print("Testing camera indices...")
    available_indices = CameraCapture.test_camera_indices()

    if not available_indices:
        print("No available cameras detected. Please ensure your webcam is connected and try again.")
    else:
        print("Available camera indices:", available_indices)
        # If you know the camera index you want to use, you can specify it
        camera_index = int(input("Enter the camera index to use: "))

        try:
            cam_capture = CameraCapture(camera_index=camera_index)
            cam_capture.capture_and_show()
        except IOError as e:
            print(e)
        finally:
            cam_capture.release()
