import pygame, ast, math
from pygame.sprite import *
from src.ui import Button, TextBubble, TextPrint

pygame.init()

CLICK_TIMEBAR = pygame.USEREVENT + 1
TOGGLE_PLAY = pygame.USEREVENT + 2

class Sprite_Mouse_Location(Sprite):
    def __init__(self,x,y):
        Sprite.__init__(self)
        self.rect = pygame.Rect(x,y,1,1)

class TimeBar(Sprite):
    def __init__(self, position):
        Sprite.__init__(self)
        self.position = position
        self.surface = pygame.Surface((320, 50))
        self.rect = pygame.Rect(position[0]+40,position[1]+60,320,10)
        self.frame_counter = TextBubble((10, 15))
        self.timer = TextBubble((200, 15))
        self.pressed = False
        self.onePress = True

    def render(self, surface, frame, total_frames):
        self.surface.fill((33,33,33))
        pygame.draw.rect(self.surface, (5,5,5), (0,0,320, 10))
        pygame.draw.rect(self.surface, (255,0,0), (0,0,frame/total_frames*320, 10))
        self.frame_counter.tprint(self.surface, f"{frame} / {total_frames}")
        self.timer.tprint(self.surface, f"{frame_to_time(frame, 24)} / {frame_to_time(total_frames, 24)}")
        surface.blit(self.surface, self.position)

    def check_click(self, position, total_frames):
        x,y = position
        mouse_sprite = Sprite_Mouse_Location(x, y)
        if pygame.sprite.collide_rect(self, mouse_sprite):
            if self.onePress:
                pygame.event.post(pygame.event.Event(CLICK_TIMEBAR, position=math.floor((x-40) / 320 * total_frames))) 
                return x-40
            elif not self.pressed:
                pygame.event.post(pygame.event.Event(CLICK_TIMEBAR, position=math.floor((x-40) / 320 * total_frames)))
                self.pressed = True
                return x-40
        return False
        
class VideoPlayer():
    def __init__(self, position, show_controls = True, autoplay = False) -> None:
        
        if show_controls:
            self.surface = pygame.Surface((520,460))
            self.frame_text = TextPrint((340, 20))
        else:
            self.surface = pygame.Surface((320,280))
        self.video = pygame.Surface((320, 240))
        self.playing = autoplay
        self.directory = "data"
        self.frame = 0
        self.framerate = 24
        self.play_button = Button((30, 320), self.play)
        self.timestamp_button = Button((210, 320), self.make_stamp)
        self.timestamp_one = False
        self.timestamp_two = False
        self.timestamp_text = TextPrint((0, 360))
        self.controls = []
        self.show_controls = show_controls
        if self.show_controls:
            self.controls.append(self.timestamp_button)
        self.controls.append(self.play_button)
        self.time_bar = TimeBar((0, 240))
        self.position = position

        with open(f"{self.directory}/metadata.txt", "r") as file:
            data = file.read()
            self.image_data = ast.literal_eval(data)
            self.total_frames = len(self.image_data) - 1

    def play(self):
        if self.playing:
            self.playing = False
        else:
            self.playing = True

    def render(self, screen, screen_size):
        self.surface.fill((33,33,33))
        self.video.blit(pygame.image.load(f"{self.directory}/{self.frame}.jpg"), (0,0))
        frame_info = self.image_data[self.frame]
        frame_speed = frame_info[2]
        frame_angle = frame_info[1]
        frame_head_angle = frame_info[3]
        frame_angle_rad = frame_angle * math.pi / 180
        frame_head_angle_rad = frame_head_angle * math.pi / 180
        if self.show_controls:
            pygame.draw.line(self.video, (0,225,87), (160, 240), (math.cos(math.pi/2-frame_angle_rad)*frame_speed+160, 240-math.sin(math.pi/2-frame_angle_rad)*frame_speed+5), 5)
            pygame.draw.line(self.video, (0,87,255), (160, 240), (math.cos(math.pi/2-frame_head_angle_rad)*30+160, 240-math.sin(math.pi/2-frame_head_angle_rad)*30), 3)
        self.surface.blit(self.video, (0,0))
        self.time_bar.render(self.surface, self.frame, self.total_frames)
        if self.show_controls:
            self.frame_text.reset()
            self.frame_text.tprint(self.surface, "Input Data")
            self.frame_text.tprint(self.surface, f"Steering: {frame_angle}")
            self.frame_text.tprint(self.surface, f"Throttle: {frame_speed}")
            self.frame_text.tprint(self.surface, f"Head Pan: {frame_angle}")
            if self.playing:
                self.play_button.bprint(self.surface, "pause_button")
                self.frame += 1 
                if self.frame == self.total_frames:
                    self.frame = 0
            else:
                self.play_button.bprint(self.surface, "play_button")
            
            if not self.timestamp_one:
                self.timestamp_button.bprint(self.surface, "Save Timestamp 1")
            elif not self.timestamp_two:
                self.timestamp_button.bprint(self.surface, "Save Timestamp 2")
                self.timestamp_text.reset()
                self.timestamp_text.tprint(self.surface, f"Timestamp One: {self.timestamp_one} ({frame_to_time(self.timestamp_one, 24)})")
            else:
                self.timestamp_button.bprint(self.surface, f"Reset Timestamps")
                self.timestamp_text.reset()
                self.timestamp_text.tprint(self.surface, f"Timestamp One: {self.timestamp_one} ({frame_to_time(self.timestamp_one, 24)})")
                self.timestamp_text.tprint(self.surface, f"Timestamp Two: {self.timestamp_two} ({frame_to_time(self.timestamp_two, 24)})")
        screen.blit(self.surface, self.position)

    def check_buttons(self, screen_size, position):
        x = self.time_bar.check_click(position, self.total_frames)
        if x:
            self.frame = math.floor(x / 320 * self.total_frames)
        for button in self.controls:
            if position[0] > button.position[0] + self.position[0] - button.size[0]//2 and position[0] < button.position[0] + self.position[0] + button.size[0]//2:
                if position[1] > button.position[1]+self.position[1]-button.size[1]//2 and position[1] < button.position[1]+self.position[1] + button.size[1]//2:
                    if button.onePress:
                        button.onclick()
                    elif not button.pressed:
                        button.onclick()
                        button.pressed = True

    def uncheck_buttons(self):
        self.time_bar.pressed = False
        for button in self.controls:
            if button.pressed == True:
                button.pressed = False

    def make_stamp(self):
        if not self.timestamp_one:
            self.timestamp_one = self.frame
        elif not self.timestamp_two:
            if self.timestamp_one > self.frame:
                self.timestamp_two = self.timestamp_one
                self.timestamp_one = self.frame
            else:
                self.timestamp_two = self.frame
        else:
            self.timestamp_one = False
            self.timestamp_two = False

def frame_to_time(frame, framerate):
    total_seconds = math.floor(frame / framerate)
    minutes = total_seconds // 60
    seconds_remainder = total_seconds % 60
    return f"{int(minutes):02}:{int(seconds_remainder):02}"

