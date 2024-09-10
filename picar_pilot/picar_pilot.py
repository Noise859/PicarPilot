from datetime import datetime
import os, sys, math, cv2, pygame, pygame.camera
pygame.init()

# Comment out here
from picarx import Picarx
from time import sleep
import readchar
from robot_hat import Music, TTS
# To here

from src.pilot_ui import *
from src.camera import *
from src.car_utils import *

screen_width = 1000
screen_height = 600

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


sounds = Music()

def main():
    global image_data, directory, px
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Picar Pilot")
    
    picar = NewPicar(px)

    print_nameplate()

    clock = pygame.time.Clock()


    joystick_count = pygame.joystick.get_count()
    if joystick_count < 1:
        print(bcolors.FAIL + "ERR: No controller detected")

    picar_camera = PicarCamera()

    if picar_camera:
        print(f"{bcolors.OKGREEN}Camera 0 connected.")

    steering_x, steering_y, head_x, head_y = 0, 0, 0, 0
    throttle_backwards, throttle_forwards, throttle = 0, 0, 0

    text_print = TextPrint((30, 250))
    toggle_recording_btn = Button((600, 300), picar_camera.toggle_recording, "Start Recording")
    link_head_wheels_btn = Button((30, 500), picar.link_head_wheels, "Start Training Mode")
    autopilot_btn = Button((600, 380), picar.toggle_autopilot, "Start Autopilot")

    joysticks = {}
    done = False
    while not done:
        # Possible joystick events: JOYAXISMOTION, JOYBALLMOTION, JOYBUTTONDOWN,
        # JOYBUTTONUP, JOYHATMOTION, JOYDEVICEADDED, JOYDEVICEREMOVED
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print(bcolors.RESET + "Exiting...")
                if picar_camera.recording:
                    picar_camera.toggle_recording()
                done = True

            # Handle hotplugging
            if event.type == pygame.JOYDEVICEADDED:
                joy = pygame.joystick.Joystick(event.device_index)
                joysticks[joy.get_instance_id()] = joy
                print(f"{bcolors.OKGREEN}Joystick {joy.get_instance_id()} connected.")

            if event.type == pygame.JOYDEVICEREMOVED:
                del joysticks[event.instance_id]
                print(f"Joystick {event.instance_id} disconnected.")

            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    if event.pos[0] > button.position[0] and event.pos[0] < button.position[0] + button.size[0]:
                        if event.pos[1] > button.position[1] and event.pos[1] < button.position[1] + button.size[1]:
                            if button.onePress:
                                button.onclick()
                            elif not button.pressed:
                                button.onclick()
                                button.pressed = True
            if event.type == pygame.MOUSEBUTTONUP:
                for button in buttons:
                    if button.pressed == True:
                        button.pressed = False
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:
                    picar.toggle_autopilot()

        result, frame_image = picar_camera.take_picture()

        # Car movement
        for joystick in joysticks.values():

            steering_x = joystick.get_axis(0) if abs(joystick.get_axis(0)) > 0.05 else 0 # Adds 5% deadzone
            steering_y = joystick.get_axis(1) # For rendering only
            head_x = joystick.get_axis(3) if abs(joystick.get_axis(3)) > 0.05 else 0 # Adds 5% deadzone
            head_y = joystick.get_axis(4) if abs(joystick.get_axis(4)) > 0.05 else 0 # Adds 5% deadzone
            throttle_backwards = (joystick.get_axis(2) + 1)/2 # Value returns [-1, 1], adjusting to be [0, 1]
            throttle_forwards = (joystick.get_axis(5) + 1)/2 # Value returns [-1, 1], adjusting to be [0, 1]
            throttle = throttle_forwards - throttle_backwards if abs(throttle_forwards - throttle_backwards) > 0.05 else 0 # Total throttle value is the difference between gas and brake, 5% deadzone
            if picar.autopilot:
                picar.move_car(px, steering_x, steering_y, head_x, head_y, throttle, frame_image)
            else:
                picar.move_car(px, steering_x, steering_y, head_x, head_y, throttle)

        # Renders UI
        screen.fill((33, 33, 33))
        text_print.reset()
        #Draws dashboard
        pygame.draw.circle(screen, (13,13,13), (130, 125), 100)
        pygame.draw.circle(screen, (13,13,13), (400, 125), 100)
        pygame.draw.rect(screen, (13,13,13), (250, 25, 30, 200))
        pygame.draw.circle(screen, (225,225,225), (130+(steering_x*100), 125+(steering_y*100)), 15) 
        pygame.draw.circle(screen, (225,225,225), (400+(head_x*100), 125+(head_y*100)), 15) 
        if throttle > 0:
            pygame.draw.rect(screen, (225,225,225), (250, 125-(throttle*100), 30, 1+(throttle*100))) 
        else:
            pygame.draw.rect(screen, (225,225,225), (250, 125, 30, 1+(abs(throttle)*100)))

        text_print.tprint(screen, f"Raw Data")
        text_print.indent()
        text_print.tprint(screen, f"[LEFT STICK] Steering: {steering_x:>6.2f}, {steering_y:>6.2f}")
        text_print.tprint(screen, f"[RIGHT/LEFT TRIGGER] Throttle: {throttle:>6.2f}")
        text_print.tprint(screen, f"[RIGHT STICK] Head: {head_x:>6.2f}, {head_y:>6.2f}")

        text_print.unindent()
        text_print.tprint(screen, "Data to Car")
        text_print.indent()
        
        text_print.tprint(screen, f"Steering Servo Angle: {conv_angle_to_servo(steering_x)}")
        if throttle > 0.05:
            text_print.tprint(screen, "Direction: Forwards")
        elif throttle < -0.05:
            text_print.tprint(screen, "Direction: Backwards")
        else:
            text_print.tprint(screen, "Direction: Neutral")
        text_print.tprint(screen, f"Throttle Strength: {conv_throttle_to_power(abs(throttle))}")
        text_print.tprint(screen, f"Head Pan: {conv_angle_to_servo(head_x)}")
        text_print.tprint(screen, f"Head Tilt: {conv_angle_to_servo(head_y)}")

        drawn_image = cv2.cvtColor(frame_image, cv2.COLOR_BGR2RGB)
        image_surface = pygame.surfarray.make_surface(drawn_image)
        image_surface = pygame.transform.rotate(image_surface, -90)
        image_surface = pygame.transform.flip(image_surface, True, False)
        image_surface = pygame.transform.scale(image_surface, (360, 240))

        picar_camera.draw_camera(steering_x, throttle, screen, picar.head_x, image_surface, frame_image, px.get_grayscale_data())

        for button in buttons:
            button.bprint(screen)

        pygame.display.flip()

        clock.tick(24)


if __name__ == "__main__":
    global px
    px = Picarx()
    main()
    px.set_cam_tilt_angle(0)
    px.set_cam_pan_angle(0)  
    px.set_dir_servo_angle(0)  
    px.stop()
    pygame.quit()
