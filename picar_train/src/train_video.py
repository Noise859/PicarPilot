import pygame, os, cv2, math
from multiprocessing import Process, Event
from src.video_player import VideoPlayer
from src.ui import Button, TextBubble, TextPrint
from src.interpreter import Interpreter
from src.train import Trainer

class Train_Video():
    def __init__(self, total_frames, screen_size):
        self.total_frames = total_frames
        self.frame_text = TextPrint((900, 75))
        self.position = (screen_size[0] // 2 + 20, 340)
        self.video_player = VideoPlayer((screen_size[0] // 2 + 20, 60), False, False)
        self.surface = pygame.Surface((520, 300))
        self.train_button = Button((60, 40), self.start_train, 18, (0, 160, 25))
        self.controls = [self.train_button]
        self.interpreter = Interpreter()
        self.interpreter.set_model("autopilot.tflite")
        self.train_process = None
        self.trainer = Trainer(self.total_frames)
        self.training_complete = Event()
    
    def start_train(self):
        self.training_complete.clear()
        self.train_process = Process(target=self.trainer.train)
        self.train_process.start()
        self.training_complete.set()
        self.interpreter.set_model("autopilot.tflite")

    def render(self, screen, screen_size):
        frame_speed, frame_angle_rad, frame_head_angle_rad = 0,0,0
        prediction = [0,0,0]
        self.surface.fill((33, 33, 33))
        self.video_player.render(screen, screen_size)
        if self.interpreter.model is not None:
            img_path = os.path.join("data", f"{self.video_player.frame}.jpg")
            if os.path.exists(img_path):
                img = cv2.imread(img_path)
                prediction = self.interpreter.make_prediction(img)
                frame_speed =  prediction[1]
                frame_angle_rad = prediction[0] * math.pi / 180
                frame_head_angle_rad = prediction[2] * math.pi / 180
                pygame.draw.line(screen, (225, 50, 0), (720, 300), (math.cos(math.pi / 2 - frame_angle_rad) * frame_speed + 720, 300 - math.sin(math.pi / 2 - frame_angle_rad) * frame_speed), 5)
                pygame.draw.line(screen, (200, 175, 30), (720, 300), (math.cos(math.pi / 2 - frame_head_angle_rad) * 30 + 720, 300 - math.sin(math.pi / 2 - frame_head_angle_rad) * 30), 3)
        self.train_button.bprint(self.surface, "Train!")
        self.frame_text.reset()
        self.frame_text.tprint(screen, "Predicted Move")
        self.frame_text.tprint(screen, f"Steering: {prediction[0]:.0f}")
        self.frame_text.tprint(screen, f"Throttle: {prediction[1]:.0f}")
        self.frame_text.tprint(screen, f"Head pan: {prediction[2]:.0f}")
        screen.blit(self.surface, self.position)
        if self.video_player.playing:
            self.video_player.frame += 1 
            if self.video_player.frame == self.video_player.total_frames:
                self.video_player.frame = 0

    def check_buttons(self, screen_size, position):
        for button in self.controls:
            if button.position[0] + self.position[0] - button.size[0] // 2 < position[0] < button.position[0] + self.position[0] + button.size[0] // 2:
                if button.position[1] + self.position[1] - button.size[1] // 2 < position[1] < button.position[1] + self.position[1] + button.size[1] // 2:
                    if button.onePress:
                        button.onclick()
                    elif not button.pressed:
                        button.onclick()
                        button.pressed = True

    def uncheck_buttons(self):
        for button in self.controls:
            if button.pressed:
                button.pressed = False