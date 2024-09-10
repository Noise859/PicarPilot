import math, picarx
from src.pilot_ui import *
from src.interpreter import *

def conv_angle_to_servo(angle):
    return math.trunc(angle*35)

def conv_throttle_to_power(throttle):
    return math.trunc(throttle*100)

class NewPicar():
    def __init__(self, px):
        self.linked_wheels = False
        self.px = px
        self.head_x = 0
        self.head_y = 0
        self.steering_x = 0
        self.steering_y = 0
        self.throttle = 0
        self.old_head_x = 0
        self.old_head_y = 0
        self.autopilot = False
        self.interpreter = Interpreter()
        self.interpreter.set_model("autopilot.tflite")

    def move_car(self, px, steering_x, steering_y, head_x, head_y, throttle, img = None):
        if not self.autopilot:
            # Moves Car
            old_head_x = self.head_x 
            old_head_y = self.head_y
            self.head_x = head_x
            self.head_y = head_y
            self.steering_x = steering_x
            self.steering_y = steering_y
            self.throttle = throttle
            if self.linked_wheels:
                if self.steering_x < old_head_x - .2:
                    self.head_x = old_head_x - .1
                elif self.steering_x > old_head_x + .2:
                    self.head_x = old_head_x + .1
                else:
                    self.head_x = old_head_x

                self.px.set_cam_tilt_angle(-15)
            else:
                self.px.set_cam_tilt_angle(-conv_angle_to_servo(self.head_y))

            self.px.set_dir_servo_angle(conv_angle_to_servo(self.steering_x))
            self.px.set_cam_pan_angle(conv_angle_to_servo(self.head_x))
            

            if throttle > 0:
                px.forward(conv_throttle_to_power(throttle))
            elif throttle < 0:
                px.backward(conv_throttle_to_power(abs(throttle)))
            else:
                px.forward(0)
        else:
            if self.interpreter.model is not None:
                prediction = self.interpreter.make_prediction(img)
                steering_x2 = prediction[0] * 1.2
                throttle2 = prediction[1]
                head_x2 = prediction[2] * 1.2
                
                if steering_x != 0:
                    self.px.set_dir_servo_angle(conv_angle_to_servo(steering_x))
                    self.px.set_cam_tilt_angle(-15)
                else:
                    self.px.set_dir_servo_angle(steering_x2)
                    self.px.set_cam_pan_angle(head_x2)
                    self.px.set_cam_tilt_angle(-15)

                if head_x != 0:
                    self.px.set_cam_pan_angle(conv_angle_to_servo(head_x))
                else:
                    self.px.set_cam_pan_angle(conv_angle_to_servo(steering_x))


                if throttle != 0:
                    if throttle > 0:
                        px.forward(conv_throttle_to_power(throttle))
                    elif throttle < 0:
                        px.backward(conv_throttle_to_power(abs(throttle)))
                    else:
                        px.forward(0)
                else:
                    if throttle2 > 0:
                        px.forward(throttle2)
                    elif throttle < 0:
                        px.backward(abs(throttle2))
                    else:
                        px.forward(0)
            
    def toggle_autopilot(self):
        if self.autopilot:
            self.autopilot = False
            for button in buttons:
                if button.text == "Stop Autopilot":    
                    button.change_text("Start Autopilot")
        else:
            self.autopilot = True
            for button in buttons:
                if button.text == "Start Autopilot":
                    button.change_text("Stop Autopilot")

    def link_head_wheels(self):
        if self.linked_wheels:
            self.linked_wheels = False
            for button in buttons:
                if button.text == "Exit Training Mode":    
                    button.change_text("Start Training Mode")
        else:
            self.linked_wheels = True
            for button in buttons:
                if button.text == "Start Training Mode":
                    button.change_text("Exit Training Mode")
