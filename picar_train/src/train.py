import math, random, cv2, ast, os, numpy as np
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
from multiprocessing import Process, Event
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Conv2D, Flatten, Dense, Dropout, Input
from tensorflow.keras.optimizers import Adam

def background_color_change(image):
    upper_black = np.array([100, 100, 100])
    mask = cv2.inRange(image, upper_black, np.array([255, 255, 255]))

    r, g, b = random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
    tint_color = np.full_like(image, (b, g, r), dtype=np.uint8)
    tinted_image = cv2.addWeighted(image, 0.7, tint_color, 0.3, 0)
    
    image[mask > 0] = tinted_image[mask > 0]

    return image

class Trainer():

    def __init__(self, total_frames):
        self.total_frames = total_frames
        self.image_folder = "data/"
        self.label_file = "data/metadata.txt"

    def create_model(self):
        # Image input
        image_input = Input(shape=(80, 160, 3), name='image_input')
        x = Conv2D(24, kernel_size=(5, 5), strides=(2, 2), activation='relu')(image_input)
        x = Dropout(0.2)(x)
        x = Conv2D(32, kernel_size=(5, 5), strides=(2, 2), activation='relu')(x)
        x = Dropout(0.2)(x)
        x = Conv2D(64, kernel_size=(5, 5), strides=(2, 2), activation='relu')(x)
        x = Dropout(0.2)(x)
        x = Conv2D(64, kernel_size=(3, 3), strides=(1, 1), activation='relu')(x)
        x = Dropout(0.2)(x)
        x = Conv2D(64, kernel_size=(3, 3), strides=(1, 1), activation='relu')(x)
        x = Dropout(0.2)(x)
        x = Flatten()(x)

        x = Dense(100, activation='relu')(x)
        x = Dropout(.2)(x)
        x = Dense(50, activation='relu')(x)
        x = Dropout(.2)(x)
        x = Dense(3, activation='linear')(x)

        model = Model(inputs=[image_input], outputs=x)
        model.compile(optimizer=Adam(learning_rate=1e-4), loss='mse')
        return model

    def load_images(self):
        images = []
        for img_num in range(self.total_frames):
            img_path = os.path.join(self.image_folder, f"{img_num}.jpg")
            if os.path.exists(img_path):
                img = cv2.imread(img_path)
                if img is not None:
                    img = cv2.resize(img, (160, 120))
                    img = img[40:120, :]
                    if random.random() < .9:
                        img = background_color_change(img)
                    img = img / 255.0
                    images.append(img)
        return np.array(images)

    def load_labels(self):
        img_arr = []
        with open(self.label_file) as metadata:
            data = metadata.read()
            image_data = ast.literal_eval(data)
        for img in image_data:
            img_arr.append([img[1], img[2], img[3]])
        return np.array(img_arr)
    
    def train(self):

        images = self.load_images()
        labels = self.load_labels()

        split_index = int(.8 * len(images))
        train_images, val_images = images[:split_index], images[split_index:]
        train_labels, val_labels = labels[:split_index], labels[split_index:]

        model = self.create_model()

        model.fit(
            x=train_images,
            y=train_labels,
            batch_size = 24,
            epochs=8,
            validation_data=(val_images, val_labels),
        )

        converter = tf.lite.TFLiteConverter.from_keras_model(model)
        tflite_model = converter.convert()
        with open('autopilot.tflite', 'wb') as f:
            f.write(tflite_model)
        print(f"Model saved")
