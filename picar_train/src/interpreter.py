import cv2
import numpy as np
import tflite_runtime.interpreter as tflite

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
            print("Model not found. Model will reload after training: " + str(e))

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