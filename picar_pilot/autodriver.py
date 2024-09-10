import cv2
import numpy as np
import tflite_runtime.interpreter as tflite

from datetime import datetime
import os, sys, math, pygame
pygame.init()

from picarx import Picarx
from time import sleep
import readchar
from robot_hat import Music, TTS

class Interpreter():
    def __init__(self):
        self.model = None
        self.input_details = None
        self.output_details = None

    def set_model(self, path):
        try:
            self.model = tflite.Interpreter(model_path=path)
            self.model.allocate_tensors()
            self.input_details = self.model.get_input_details()
            self.output_details = self.model.get_output_details()
        except Exception as e:
            print("Model not found: " + str(e))

    def preprocess_image(self, img):
        img = cv2.resize(img, (160, 120))
        img = img[40:120, :]
        img = img / 255.0
        img = np.expand_dims(img, axis=0).astype(np.float32)
        return img

    def make_prediction(self, img):
        preprocessed_img = self.preprocess_image(img)
        self.model.set_tensor(self.input_details[0]['index'], preprocessed_img)
        self.model.invoke()
        prediction = self.model.get_tensor(self.output_details[0]['index'])
        steering = prediction[0][0]
        throttle = prediction[0][1]
        head_pan = prediction[0][2]
        return steering, throttle, head_pan

class TextPrint:
    def __init__(self, og_pos=(0,0)):
        self.og_pos = og_pos
        self.reset()
        self.font = pygame.font.Font(None, 20)

    def tprint(self, screen, text):
        text_bitmap = self.font.render(text, True, (255, 255, 255))
        screen.blit(text_bitmap, (self.x, self.y))
        self.y += self.line_height

    def reset(self):
        self.x = self.og_pos[0]
        self.y = self.og_pos[1]
        self.line_height = 22

    def indent(self):
        self.x += 20

    def unindent(self):
        self.x -= 20

def main():
    camera_resolution = (640, 480)
    screen = pygame.display.set_mode(camera_resolution)
    pygame.display.set_caption("Picar Autodriver")

    clock = pygame.time.Clock()
    predicted_label = TextPrint((10,10))
    interpreter = Interpreter()
    interpreter.set_model("autopilot.tflite")
    
    cam = cv2.VideoCapture(0)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, camera_resolution[0])
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, camera_resolution[1])

    if not cam.isOpened():
        print("Error: Could not open camera.")
        return

    px = Picarx()
    prediction = [0, 0, 0]

    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

        screen.fill((33, 33, 33))

        # Make prediction
        result, image = cam.read()

        if result:
            prediction = interpreter.make_prediction(image)
            px.set_dir_servo_angle(prediction[0]*1.2)
            px.forward(prediction[1]*.8)

            # Convert the image from BGR to RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Convert the image to a Pygame surface
            image_surface = pygame.surfarray.make_surface(image)

            # Rotate and scale the image to match the screen resolution
            image_surface = pygame.transform.rotate(image_surface, -90)
            image_surface = pygame.transform.flip(image_surface, True, False)
            image_surface = pygame.transform.scale(image_surface, camera_resolution)

            # Blit the image surface onto the screen
            screen.blit(image_surface, (0, 0))

            pygame.draw.line(screen, (0,225,87), (320, 480), (math.cos(math.pi/2-prediction[0]*math.pi/180)*prediction[1]+320, 480-math.sin(math.pi/2-prediction[0]*math.pi/180)*prediction[1]+5), 5)
            pygame.draw.line(screen, (0,87,255), (320, 480), (math.cos(math.pi/2-prediction[2]*math.pi/180)*30+320, 480-math.sin(math.pi/2-prediction[2]*math.pi/180)*30), 3)

        predicted_label.reset()
        predicted_label.tprint(screen, "Predicted Data")
        predicted_label.tprint(screen, f"Steering: {prediction[0]}")
        predicted_label.tprint(screen, f"Throttle: {prediction[1]}")

        pygame.display.flip()
        clock.tick(24)

    cam.release()
    px.set_cam_tilt_angle(0)
    px.set_cam_pan_angle(0)  
    px.set_dir_servo_angle(0)  
    px.stop()
    pygame.quit()

if __name__ == "__main__":
    main()
