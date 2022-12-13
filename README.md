# Cheap_Saber

Design Overview:

This design is a game resembling "Beat Saber". "Beat Saber" is a VR game, where the player swibes at incoming cubes to the rhythm of a song. This design is similar, except it uses the webcam, calculates the timestamps of onsets in a chosen song, calibrates on and tracks an object provided by the user using the webcam, and checks if the user touches objects that are shown onscreen based on the timestamps of the onsets.

Initially, I was planning on tracking an object using colors. In this way, the user would calibrate based on a specific color, and then the location of the color would be found in each frame of the webcame. This design was simple, but would require a distnct color that was ot present in the background. So instead, I utilized template matching using OpenCV. This algorithm is doing template matching, which is a technique used to find and locate a template, or reference, image within a larger image.

Furthermore, I was planning on detecting the overall tempo of the song, but I found an algorithm discussed in the following link, to detect timestamps of beats:

http://archive.gamedev.net/archive/reference/programming/features/beatdetection/index.html

This algorithm models how humans detect beats and rythms, by detecting deviations in sound energy. It takes the integral over the first 1024 samples of the signal to get an "instant" energy, and compares it to the average energy over the last second (48000 samples).

Preliminary Design Verification:

My initial prototyping of this design was implementing the template detection algorithm. My first itartion was the color thresholding technique, the function for that can be found in Test_Scripts/ObjectTrackTest.py. The find_color_coordinates function returns all coordiantes of the same color, and assuming that color is unique, one of those coordinates describes the location of the user marker. I eventually used the template finding technique also found in the same file and described in the over view. 

As part of the preliminary design, I also set up the game states modeled as a FSM, and implemented it using the Pygame library. 

Design Implementation:

The design of the system was implemented as a single class (CheapSaber) with the following attributes:

- A pygame object (to get display)
- A pygame mixer (to play music)
- All songs in Source_Music folder

The CheapSaber class also contains the following functions:

- pick_song (allow user to scroll through avaialable music)
- object_tracking (find template of object given a window as coordinates, the current frame, and previous frame from video stream)
- get_tempo (find all timestamps of onsets given a filepath for a .wav music file)
- game (contains FSM to play game once game has started)
- main_menu (launch main menu with all user options)

Design Testing:

Testing was done iteratively throughout the desing process. The Test_Scripts folder contains scripts used to test the object tracking algorithm and get onsets and tempo algorithm. The get onset and tempo algorithm was tested by providing a .wav file of a simple 120 bpm metronome, and plotting the signal and time stamps. This is shown below:

![image](https://user-images.githubusercontent.com/54084895/207452467-2c0acdb0-3277-4045-a116-611a13f294c7.png)

A demonstration video is included in the Final Presentation.

Summary, Conclusion, and Future Work:

This design seems to be running well, but in the future, I would like to explore other ways of tracking beats in a song. The method used here is best for beat tracking when streaming music, but there are other more complex methods that track beats much faster. There are also libraries like librosa to do that automatically, so the detect_tempo function can be swapped out if the user wishes to do so.


