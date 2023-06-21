import os
import cv2
from datetime import datetime

class Config:
    angle: float = 0
    brightness: float = 0.0
    contrast: float = 1.0


# simple class example
# all parameters from method must be typed
class ProcessImage:
    # You must type your available attribute here
    file_path: os.path = None
    config: Config = Config()  # Define attribute as a Config class
    show: bool = True

    def __init__(self, file_path: os.path = "", show: bool = True):
        self.file_path = file_path
        self.image = None
        self.original_image = None
        self.show = show
        self.load_image()

    def load_image(self):
        if os.path.exists(self.file_path):
            self.image = cv2.imread(self.file_path)
            self.original_image = self.image.copy()
            if self.show:
                cv2.imshow("Image Loaded", self.image)
                cv2.waitKey(0)

    def rotate_image(self, angle: float):
        if self.image is not None:
            print(angle)
            (height, width) = self.image.shape[:2]
            (center_x, center_y) = (width // 2, height // 2)
            rotation_matrix = cv2.getRotationMatrix2D((center_x, center_y), angle, 1.0)
            self.image = cv2.warpAffine(self.image, rotation_matrix, (width, height), flags=cv2.INTER_LINEAR,
                                        borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
            if self.show:
                cv2.imshow(f"Image Rotated by {angle} degrees", self.image)
                cv2.waitKey(0)

    def adjust_contrast(self, contrast: float):
        if self.image is not None:
            self.image = cv2.convertScaleAbs(self.image, alpha=contrast, beta=0)
            if self.show:
                cv2.imshow(f"Image Contrast Adjusted with scale {contrast}", self.image)
                cv2.waitKey(0)

    def adjust_brightness(self, brightness: float):
        if self.image is not None:
            self.image = cv2.convertScaleAbs(self.image, alpha=1, beta=brightness)
            if self.show:
                cv2.imshow(f"Image Brightness Adjusted with value {brightness}", self.image)
                cv2.waitKey(0)

    def save_image(self):
        if self.image is not None:
            file_name = self.file_path.split("/")[-1].split(".")[0]
            current_date = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
            new_file_path = f"{file_name}_{current_date}.png"
            cv2.imwrite(new_file_path, self.image)
            print("Writing on " + os.path.abspath(new_file_path))

    def process_with_config(self):
        show = self.show
        self.show = False
        self.adjust_brightness(self.config.brightness)
        self.adjust_contrast(self.config.contrast)
        self.rotate_image(self.config.angle)
        self.save_image()
        self.show = show



