import cv2, os, pygame
from datetime import datetime
from src.pilot_ui import *
from src.car_utils import *

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\033[97m'


class PicarCamera():
    def __init__(self) -> None:
        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        self.camera_render = pygame.Surface((320, 240))
        self.image_data = []
        self.directory = "tub/"
        self.image_count = 0
        self.recording = False
        self.cam_text = TextPrint((660, 125))

    def take_picture(self):
        result, image = self.camera.read()
        return result, image

    def toggle_recording(self):
        if self.recording:
            self.recording = False
            self.image_count = 0
            with open(f"{self.directory}metadata.txt", "w") as file:
                file.write(str(self.image_data))
                file.close()
            self.image_data = []
            for button in buttons:
                if button.text == "Stop":
                    button.change_text("Start Recording")
        else:
            self.image_data = []
            self.recording = True
            now = datetime.now()
            nowform = now.strftime("%m-%d-%Y_%H:%M:%S")
            if not os.path.exists(f"tub/{nowform}"):
                os.makedirs(f"tub/{nowform}")
            else:
                print(f"{bcolors.WARNING}Directory already exists!")
            self.directory = f"tub/{nowform}/"
            for button in buttons:
                if button.text == "Start Recording":
                    button.change_text("Stop")

    def record(self, steering_x, throttle, head_x, image, grayscale):
        if self.recording:
            steering_angle = conv_angle_to_servo(steering_x)
            motor_power = conv_throttle_to_power(throttle) if throttle != 0 else 0
            self.image_data.append([f'{self.image_count}.jpg', steering_angle, motor_power, conv_angle_to_servo(head_x), grayscale])
            cv2.imwrite(f'{self.directory}{self.image_count}.jpg', image) 
            self.image_count += 1

    def draw_camera(self, steering_x, throttle, screen, head_x, image_surface, frame_image, grayscale):
        if self.camera:
            if self.recording:
                self.record(steering_x, throttle, head_x, frame_image, grayscale)
                pygame.draw.rect(screen, (0,0,0), (600, 30, 320, 240))
                self.cam_text.reset()
                self.cam_text.tprint(screen, "Recording in progress!")
            else: 
                screen.blit(image_surface, (600, 30))
        else:
            self.cam_text.tprint(screen, "No camera detected!")
            pygame.draw.rect(screen, (0,0,0), (600, 30, 320, 240))
