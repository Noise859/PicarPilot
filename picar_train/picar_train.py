import pygame
from src.ui import *
from src.video_player import *
from src.train import *
from src.interpreter import *
from src.train_video import *

screen_size = (1080, 600)

global_framerate = 24

pygame.init()

buttons = []

def main(Done):
    global screen_size, global_framerate
    screen = pygame.display.set_mode(screen_size)
    clock = pygame.time.Clock()
    pygame.display.set_caption("Picar Training Utility")
    video_player = VideoPlayer((screen_size[0] // 2 - 500,60))
    train_video = Train_Video(video_player.total_frames + 1, screen_size)
    input_text = TextPrint((320, 20))
    while not Done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                Done = True
            elif event.type == pygame.WINDOWRESIZED:
                screen_size = pygame.display.get_surface().get_size()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                video_player.check_buttons(screen_size, event.pos)
                train_video.check_buttons(screen_size, event.pos)
                for button in buttons:
                    if event.pos[0] > button.position[0]+screen_size[0] // 2 - 160 - button.size[0]//2 and event.pos[0] < button.position[0]+screen_size[0] // 2 - 160 + button.size[0]//2:
                        if event.pos[1] > button.position[1]+40-button.size[1]//2 and event.pos[1] < button.position[1]+40 + button.size[1]//2:
                            if button.onePress:
                                button.onclick()
                            elif not button.pressed:
                                button.onclick()
                                button.pressed = True
            elif event.type == pygame.MOUSEBUTTONUP:
                video_player.uncheck_buttons()
                for button in buttons:
                    if button.pressed == True:
                        button.pressed = False
            elif event.type == CLICK_TIMEBAR:
                train_video.video_player.frame = event.position

        if video_player.playing and not train_video.video_player.playing:
            train_video.video_player.playing = True
        if not video_player.playing and train_video.video_player.playing:
            train_video.video_player.playing = False

        screen.fill((33,33,33))

        #Render UI

        video_player.render(screen, screen_size)
        train_video.render(screen, screen_size)

        pygame.display.flip()
        clock.tick(global_framerate)


if __name__ == "__main__":
    main(False)
    pygame.quit()

