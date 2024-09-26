# Picar Pilot

Welcome to PiCar Pilot. This is a tool I developed specifically for the Sunfounder PiCar (with an upgraded wide angle camera, [like this one](https://www.amazon.com/Smraza-Raspberry-Megapixels-Adjustable-Fish-Eye)), or potentially any system using the SunFounder Robot Hat or their libraries. The tool allows you to control your motors and servos via a Joystick controller, as well as stream and record video. The tool also comes with PiCar Train. PiCar Train allows you to import data recorded from PiCar Pilot and train a Tensorflow model, which can then be uploaded to the car and used to create an AI RC car that follows a track, similar to the popular Donkeycar project.

## How to use PiCar Pilot

PiCar Pilot needs the [SunFounder Robot Hat Library](https://github.com/sunfounder/robot-hat) and additional libraries installed on a Raspberry Pi according to their instructions [here.](https://docs.sunfounder.com/projects/picar-x/en/latest/python/python_start/what_do_we_need.html) Once installed, PiCar Pilot can be cloned saved anywhere on the Pi, and, after navigating to the folder via the command line on the Pi, it can be ran via the command:
   > python picar_pilot.py
 
 
 If correctly launched, the Picar Pilot should lauch and look like the image below.
![Image of Picar Pilot](https://github.com/Noise859/PicarPilot/blob/main/instruction_images/picar_dash.jpg?raw=true "Picar Pilot")

Now that PiCar Pilot has launched, an [F710](https://www.logitechg.com/en-us/products/gamepads/f710-wireless-gamepad.940-000117.html) controller can be plugged into the Pi and used to control the car. The Pilot should show you the current position and values of your controller. If you have a camera correctly installed, you should also see a livestream. 

### Available Options
  > 1. **Start Training Mode**
  > Starting training mode simply aims the tilt head servo of the PiCar downward, and locks the pan head servo in sync with the steering of the car, for smoother video and so the track is in the video more.
  > 2. **Start Recording**
  > Starting the  recording starts capturing images and vehicle telemetry data and saves it to the "tub" folder
  > 3. **Start Autopilot**
  > Start autopilot looks for an "autopilot.tflite" file within the picar_pilot directory, and starts driving the car based on the interpreted data from the camera.

Once data has been collected, it will be saved under the date and start time of the recording. To continue with training a model, you will need to move this folder over to another PC **with an Nvidia GPU only**(if you don't have one, it may still work but would take hours). This can be achieved with VNC Viewer, or rsync(or rsync adjacent) commands.

### Appropriate Data
For PiCar Autopilot to work properly, it is recommended that you record around 15,000 images, or 10 minutes of video. The track must be within the frame for >95% of the images. For specifics on the track, see the "Building an Appropriate Track" section below.

## How to use PiCar Train
This program is intended to work on a Windows PC, running the custom picartf Conda environment. You will need to [install Miniconda](https://docs.anaconda.com/miniconda/), and use the yml file included in the picar_train directory. All of your images as well as the configuration file from the folder you hopefully already transferred to your PC from the Pi need to be in the "data" folder. **Note:** Do not put a folder in the data folder, i.e. the date and time folder that the images are initially saved in. Drop only the raw images and the configuration file into the data folder.

Using a command prompt with the picartf environment active, cd to the picar_train folder and run the program with:
> python picar_train.py

If it properly ran, it should look something like this:
![Image of Picar Train](https://github.com/Noise859/PicarPilot/blob/main/instruction_images/picar_train.jpg?raw=true "Picar Train")

### Available Options
  > 1. **Pause/Play Button**
  >  This button will pause and play both video players at once
  >  2. **Time bar**
  >  By clicking on the time bar on the video player on the left, you can skip to certain parts of the video.
  >  3. **Save Timestamp**
  >  Save Timestamp allows the user to save up to 2 timestamps at exact frames. This will eventually be used to allow cutting of the video in between the timestamps
  >  4. **Train!**
  > This button spawns a new process for Tensorflow to begin the training. Picar Train may still be used during this time. The console will update you on Tensorflow's progress and when the final model is saved. It will be called "autopilot.tflite" and it will be in the same directory as "picar_train.py"



## Building an Appropriate Track
It's not too hard to build a track, but there are a few important points.

**What does the track need to have?**

1. It needs to be black (for now, this will ideally be adjustable later)
2. It needs to ***highly*** contrast the floor surface that it is on for the best results, i.e. black track on a white floor
3. The room must be well lit, but not reflective of bright light. This can blow out your images
4. It must be ~3in wide

**What can't it have?**

1. For a camera with <120 degree field of view, no turns that are >45 deg
2. No turns >70 deg for all cameras
3. Other similarly colored rugs or other floor items, or significant shadows next to the track

**What should it be made of?**
Whatever you want, black electrical tape works great. You could cut a vinyl track. 

Here are a few examples of some great data:
![Image 1 of good track](https://github.com/Noise859/PicarPilot/blob/main/instruction_images/t2.jpg?raw=true "Picar Track 1")![Image 2 of good track](https://github.com/Noise859/PicarPilot/blob/main/instruction_images/t1.jpg "Picar Track 2")![Image 3 of good track](https://github.com/Noise859/PicarPilot/blob/main/instruction_images/t3.jpg "Picar Track 3")

## Potential Improvements
Here contains a list of potential improvements to the program as a whole, whether UI, functionality, or tweaking the model.

1. Tweak the hyperparameters. This will probably always be a part of this list.
2. Grayscale sensor data is already recorded along with speed and steering, this data can be used in the training and interpretation. It may be a very easy function to train - all grayscale sensors must read black, if not, turn away from that direction.
3. Add a color picker to choose the color of the track, and make a range out of it based on the RGB value, so the track can be any color as long as it contrasts the background.
4. Tweak the training mode head pan algorithm so it both follows the wheels into turns, but does not have any sudden movements for better picture quality.


Many thanks to the engineers at Sunfounder and the developers from Donkeycar for the inspiration and help.
