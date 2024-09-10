import pygame, os, ast
text_bubbles = []

class Button:
    def __init__(self, position, action, font_size=18, color=(32, 61, 109)) -> None:
        self.position = position
        self.pressed = False
        self.onePress = True
        self.font = pygame.font.Font("resources/Roboto-Regular.ttf", font_size)
        self.color = color
        self.action = action  # Rename onclick to action

    def bprint(self, surface, text):
        if text == "play_button":
            self.surface = pygame.Surface((62,62))
            self.size = (62, 62)
            self.rect = self.surface.get_rect()
            pygame.draw.polygon(self.surface, (255,255,255), [(18, 18), (18, 44), (44, 31)])
        elif text == "pause_button":
            self.surface = pygame.Surface((62,62))
            self.size = (62, 62)
            self.rect = self.surface.get_rect()
            pygame.draw.rect(self.surface, (255,255,255), (17, 16, 4, 30))
            pygame.draw.rect(self.surface, (255,255,255), (40, 16, 4, 30))
        else:
            self.text_bitmap = self.font.render(text, True, (255, 255, 255))
            self.size = (self.text_bitmap.get_width() + 60, self.text_bitmap.get_height() + 40)
            self.surface = pygame.Surface(self.size)
            text_width = self.text_bitmap.get_width()
            text_height = self.text_bitmap.get_height()
            self.surface.fill(self.color)
            self.surface.blit(self.text_bitmap, (self.size[0] // 2 - text_width // 2, self.size[1] // 2 - text_height // 2))
            
        surface.blit(self.surface, (self.position[0]-self.size[0]//2, self.position[1]-self.size[1] //2))

    def onclick(self):
        self.pressed = True
        self.action()

class TextBubble:
    def __init__(self, og_pos=(0,0)):
        self.og_pos = og_pos
        self.font = pygame.font.Font("resources/Roboto-Regular.ttf", 20)

    def tprint(self, surface, text):
        #self.font.set_bold(bold)
        text_bitmap = self.font.render(text, True, (255, 255, 255))
        surface.blit(text_bitmap, (self.og_pos[0], self.og_pos[1]))

class TextPrint:
    def __init__(self, og_pos=(0,0)):
        self.og_pos = og_pos
        self.reset()
        self.font = pygame.font.Font("resources/Roboto-Regular.ttf", 20)
        self.line_height = 24

    def tprint(self, screen, text):
        #self.font.set_bold(bold)
        text_bitmap = self.font.render(text, True, (255, 255, 255))
        screen.blit(text_bitmap, (self.x, self.y))
        self.y += self.line_height

    def reset(self):
        self.x = self.og_pos[0]
        self.y = self.og_pos[1]
        self.line_height = 24

    def indent(self):
        self.x += 20

    def unindent(self):
        self.x -= 20

def print_nameplate():
    print(f'''                         
 _____ _                _____        _             
|  _  |_|___ ___ ___   |_   _|__ ___|_|___ ___ ___ 
|   __| |  _| .'|  _|    | ||  _| .'| |   | -_|  _|
|__|  |_|___|__,|_|      |_||_| |__,|_|_|_|___|_|  
          \n
 _____        _____                         
| __  |_ _   | __  |___ ___ ___ ___ ___ ___ 
| __ -| | |  | __ -|  _| -_|   |   | .'|   |
|_____|_  |  |_____|_| |___|_|_|_|_|__,|_|_|
      |___|                                
          ''')
    
# Logo by patorjk.com/software/taag
# Font name: Rectangles