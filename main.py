import pygame
import pygame.camera
from pygame import mixer
import pygame_menu
import glob
import numpy as np
import wave
import cv2
import time
import random

class CheapSaber:
    def __init__(self):
        # Initialize pygame
        pygame.init()

        # Initialize mixer
        mixer.init()

        # Create screen, title, icon
        self.screen = pygame.display.set_mode((1200, 600)) 
        pygame.display.set_caption("Cheap Saber")
        icon = pygame.image.load("Source_Images/wave.png")
        pygame.display.set_icon(icon)
        self.my_font = pygame.font.SysFont('Comic Sans MS', 30)

        # Get songs
        self.songs = []
        counter = 0
        for file in glob.glob("Source_Music/*.wav"):
            self.songs.append((file, counter))
            counter+=1

        # Initialize first song
        self.song = self.songs[0]

        

    def pick_song(self, value, song_idx):
        self.song = self.songs[song_idx]

    def object_tracking(self, window, current_frame, previous_frame):
        previous_frame = pygame.surfarray.array3d(previous_frame)
        current_frame = pygame.surfarray.array3d(current_frame)

        previous_frame = previous_frame.swapaxes(0,1)
        current_frame = current_frame.swapaxes(0,1)

        # Convert frames to grayscale
        old_frame_gray = cv2.cvtColor(previous_frame, cv2.COLOR_BGR2GRAY)
        current_frame_gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
        
        # Get template image from the old frame
        template_img = old_frame_gray[window[1]:window[3], window[0]:window[2]]
        
        # Create a matching template
        w, h = template_img.shape[::-1]

        res = cv2.matchTemplate(current_frame_gray, template_img, cv2.TM_CCOEFF_NORMED)
        
        # Get the location of the object in the current frame 
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        
        return ([max_loc[0], max_loc[1]])

    def get_tempo(self, filename, threshold):
        
        # Sensitivity constant 
        C = 1 
        # History buffer 
        B = np.zeros(44032) 
        
        # Read wav file
        wavFile = wave.open(filename, 'r')
        data = wavFile.readframes(-1)
        data = np.frombuffer(data, dtype=np.int32)
        sampling_rate = wavFile.getframerate()
        Te = 1/sampling_rate
        wavFile.close()

        # Detect beats
        beats = []
        prev = 0
        for n in range(len(data)):
            # Compute instant energy
            e = np.sum(data[n:n+1024]**2)/1024
            # Compute average energy 
            E_avg = np.sum(B[:(44032-1024)]**2)/44032
            # Detect beat 
            if e > C*E_avg and (n*Te - prev) > threshold:
                beats.append(n*Te)
                prev = n*Te
                print("Beat detected at time {}".format(n*Te))
            # Shift history buffer 
            B[:(44032-1024)] = B[1024:]
            # Add new samples to history buffer
            if n + 1024 < len(data):
                B[44032-1024:] = data[n:n+1024]
        
        return beats

    def game(self):

        im_height = 600
        im_width = 1200

        # Show loading screen
        self.screen.fill((255,255,255))
        text_surface = self.my_font.render('LOADING...', False, (0, 0, 0))
        self.screen.blit(text_surface, (0,0))
        pygame.display.update()

        # Calculate tempo
        mixer.music.load(self.song[0])
        tempo = self.get_tempo(self.song[0], 0.4)
        # tempo = [3, 8, 12, 16, 20]

        # Reset screen
        self.screen.fill((255,255,255))
        pygame.display.update()

        # Intitialize and get camera
        pygame.camera.init()
        clist = pygame.camera.list_cameras()
        cam = pygame.camera.Camera(clist[0], (im_height, im_width))

        # Start camera and get first image
        cam.start()
        cam.set_controls(hflip = True, vflip = False)
        snapshot = cam.get_image()
        last_snapshot = snapshot

        # Variable initilization
        rect_size = 100
        rect_left = int(im_width/2-rect_size/2)
        rect_top = int(im_height/2-rect_size/2)
        start_time = 0
        calibrated = False
        random_pos = []
        end_game_flag = False
        score = 0
        total = len(tempo)

        while True:
            # Event loop
            events = pygame.event.get()
            for e in events:
                if e.type == pygame.QUIT:
                    # close the camera safely
                    pygame.quit()
                    quit()
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_RETURN:
                        # Get previous snapshot
                        last_snapshot = snapshot
                        calibrated = True

                        # Start song
                        mixer.music.play()

                        # Start time index
                        start_time = time.time()
                        
            if end_game_flag == True:
                # Show final score screen
                self.screen.fill((255,255,255))
                text_surface = self.my_font.render('Game Over: ' + str(score) + "/" + str(total), False, (0, 0, 0))

                self.screen.blit(text_surface, (0,0))
                pygame.display.update()

            else:
                # Show snapshot to display surface
                self.screen.blit(snapshot, (0,0))

                # Draw circles on screen
                for i in random_pos:
                    pygame.draw.circle(self.screen, (0,255,0), i, 20)

                # Start game after calibration
                if calibrated == True:
                    # Track opbject once calibrated on object
                    rect_coord = self.object_tracking([rect_left, rect_top, rect_left + rect_size, rect_top + rect_size], snapshot, last_snapshot)
                    last_snapshot = snapshot

                    rect_left = rect_coord[0]
                    rect_top = rect_coord[1]

                    rect = pygame.Rect(rect_left, rect_top, rect_size, rect_size)
                    pygame.draw.rect(self.screen, (255,0,0), rect, 4)

                    # Create circle on beat
                    if abs((time.time() - start_time) - tempo[0]) <= 0.2:
                        # Draw circle in random positon
                        pos = (random.randint(300, im_width - 300), random.randint(50, im_height - 50))

                        # Remove last circle pos
                        if len(random_pos) > 0:
                            random_pos.pop(0)

                        # Add random position to list 
                        random_pos.append(pos)

                        # Pop cur tempo
                        tempo.pop(0)

                        # Check if beats are finished
                        if (len(tempo) == 0):
                            end_game_flag = True

                    # Check if rectangle is around circle
                    for i in random_pos.copy():
                        circle_x = i[0]
                        circle_y = i[1]
                        if (abs(circle_x - rect_left) < rect_size/2) and (abs(circle_y - rect_top) < rect_size/2):
                            random_pos.remove(i)
                            print("GOOD")
                            score += 1

                else:
                    # Keep calibration window at center of screen
                    rect = pygame.Rect(rect_left, rect_top, rect_size, rect_size)
                    pygame.draw.rect(self.screen, (255,0,0), rect, 4)

                # Display image and get next snapshot
                pygame.display.flip()
                snapshot = cam.get_image()

    def main_menu(self):
        # Menu setup
        menu = pygame_menu.Menu('Main Menu', 1200, 600,
                            theme=pygame_menu.themes.THEME_BLUE)

        menu.add.selector('Pick Song :', self.songs, onchange=self.pick_song)
        menu.add.button('Play', self.game)
        menu.add.button('Quit', pygame_menu.events.EXIT)

        # Start game
        menu.mainloop(self.screen)

cheap_saber_game = CheapSaber()
cheap_saber_game.main_menu()