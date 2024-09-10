import pygame, os
text_bubbles = []
buttons = []

base_path = os.path.dirname(os.path.abspath(__file__))
font_path = os.path.join(base_path, '..', 'resources', 'Roboto-Regular.ttf')

class Button:
    def __init__(self, position, action, text, font_size=18, color=(32, 61, 109)) -> None:
        self.position = position
        self.text = text
        self.pressed = False
        self.onePress = True
        self.font = pygame.font.Font(font_path, font_size)
        self.bkg_brightness = (color[0] + color[1] + color[2]) / 3
        if self.bkg_brightness < 255 / 4:
            self.text_bitmap = self.font.render(self.text, True, (255, 255, 255))
        elif self.bkg_brightness < 255 / 2:
            self.text_bitmap = self.font.render(self.text, True, (180, 180, 180))
        elif self.bkg_brightness < 255 / 1.5:
            self.text_bitmap = self.font.render(self.text, True, (90, 90, 90))
        else:
            self.text_bitmap = self.font.render(self.text, True, (13, 13, 13))
        self.color = color
        self.size = (self.text_bitmap.get_width() + 60, self.text_bitmap.get_height() + 40)
        self.action = action  # Rename onclick to action
        self.surface = pygame.Surface(self.size)

        buttons.append(self)

    def bprint(self, screen):
        text_width = self.text_bitmap.get_width()
        text_height = self.text_bitmap.get_height()
        self.surface.blit(self.text_bitmap, (self.size[0] // 2 - text_width // 2, self.size[1] // 2 - text_height // 2))
        screen.blit(self.surface, self.position)

    def change_text(self, new_text):
        self.text = new_text
        if self.bkg_brightness < 255 / 4:
            self.text_bitmap = self.font.render(self.text, True, (255, 255, 255))
        elif self.bkg_brightness < 255 / 2:
            self.text_bitmap = self.font.render(self.text, True, (180, 180, 180))
        elif self.bkg_brightness < 255 / 1.5:
            self.text_bitmap = self.font.render(self.text, True, (90, 90, 90))
        else:
            self.text_bitmap = self.font.render(self.text, True, (13, 13, 13))
        self.size = (self.text_bitmap.get_width() + 60, self.text_bitmap.get_height() + 40)
        self.surface = pygame.Surface(self.size)

    def onclick(self):
        self.pressed = True
        self.action()

class TextPrint:
    def __init__(self, og_pos=(0,0)):
        self.og_pos = og_pos
        self.reset()
        self.font = pygame.font.Font(font_path, 20)

    def tprint(self, screen, text):
        #self.font.set_bold(bold)
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

def print_nameplate():
    print(f'''
 _____ _                _____ _ _     _     
|  _  |_|___ ___ ___   |  _  |_| |___| |_   
|   __| |  _| .'|  _|  |   __| | | . |  _|  
|__|  |_|___|__,|_|    |__|  |_|_|___|_|    
          \n
 _____        _____                         
| __  |_ _   | __  |___ ___ ___ ___ ___ ___ 
| __ -| | |  | __ -|  _| -_|   |   | .'|   |
|_____|_  |  |_____|_| |___|_|_|_|_|__,|_|_|
      |___|                                
          ''')

# Logo by patorjk.com/software/taag
# Font name: Rectangles