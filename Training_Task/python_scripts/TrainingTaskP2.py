import sys
import os
import pygame as pg
from pygame.locals import *
sys.path.append(os.path.join("/home", "pi", "Desktop", "ChimpPygames", "PygameTools"))
import PgTools
import random
import time
import glob

# initialize pygame and screen
pg.init()
screen = PgTools.Screen()

# init font for trial counter
font = pg.font.SysFont(None, 48)

file = open("Training_Task/parametersP2.dat")
params = PgTools.get_params(file)
file.close()

subjectName = str(params["subject_name"])
trialsAmt = int(params["number_of_trials"])
stimLength = int(params["stimulus_length"])
stimHeight = int(params["stimulus_height"])
passDelay = int(params["passed_inter_trial_interval"])
failDelay = int(params["failed_inter_trial_interval"])
if "y" in str(params["randomly_shaped_stimuli"]) or "Y" in str(params["randomly_shaped_stimuli"]):
    randShapes = True
else:
    randShapes = False

def start_trial(length, height):
    """
    Initiates a new trial, draws stimulus

    :param length: length of new stimulus
    :param height: width of new stimulus
    """
    screen.refresh()
    global stimulus
    xCoord = PgTools.rand_x_coord(stimLength)
    yCoord = PgTools.rand_y_coord(stimHeight)
    
    s = pg.Surface((length, height))
    s.blit(images[random.randint(0, len(images)-1)], (0, 0))
    # s.blit(test_image, (0, 0))  # use to debug clipart
    screen.fg.blit(s, (xCoord, yCoord))
    stimulus = pg.draw.rect(screen.fg, Color('goldenrod'),(xCoord, yCoord, length, height), 15)
    # randInt = random.choice([0, 1, 2, 3, 4])
    # if randShapes:
    #    PgTools.rand_shape(screen.fg, (xCoord, yCoord), (length, height), randInt)

PgTools.write_ln(
    filename="Training_Task/resultsP2.csv",
    data=["subject_name", "trial", "input_coordinates", "accuracy",],
)

trialNum = 1
passedTrials = 0
# randInt = random.randint(0, 99999) # seed

# load all our images
images = []
list_of_stimuli = glob.glob("/home/pi/Desktop/ChimpPygames/Images/samples/*.jpg")
for filepath in list_of_stimuli:
    images.append(pg.transform.scale(pg.image.load(filepath), (stimLength, stimHeight)))
# test_image = pg.transform.scale(pg.image.load("/home/pi/Desktop/ChimpPygames/Images/samples/80.jpg"), (stimLength, stimHeight))
start_trial(stimLength, stimHeight)

# game loop
running = True

# params for deliberate touch
touched_down = False   # tells us whether the animal has already touched
when_they_started_their_touch = 0
min_touch_ms_required = 150
max_touch_ms = 3000

while running:
# disply trial number in upper left corner
#     text = font.render('Trial #{}'.format(trialNum), True, Color('salmon'))
#     screen.fg.blit(text, (20, 20))    
       
    for event in pg.event.get():
        PgTools.quit_pg(event)
        if event.type == MOUSEBUTTONDOWN:
            xCoord, yCoord = event.pos
            when_they_started_their_touch = pg.time.get_ticks()
            touched_down = True
            
        elif (event.type == MOUSEBUTTONUP):
            touched_down = False
            if (pg.time.get_ticks()-when_they_started_their_touch<min_touch_ms_required) and \
               (pg.time.get_ticks()-when_they_started_their_touch>max_touch_ms):
                continue
            elif (pg.time.get_ticks()-when_they_started_their_touch>min_touch_ms_required) and \
               (pg.time.get_ticks()-when_they_started_their_touch<max_touch_ms): 
                
            if stimulus.collidepoint(xCoord, yCoord):# and screen.fg.get_at((xCoord, yCoord)) != (0,0,0):
                PgTools.response(screen, True, passDelay)
                PgTools.write_ln(
                    filename="Training_Task/resultsP2.csv",
                    data=[subjectName, trialNum, ("\"" + str(xCoord) + ", " + str(yCoord) + "\""), "passed",],
                )
                passedTrials += 1
            else:
                PgTools.response(screen, False, failDelay)
                PgTools.write_ln(
                    filename="Training_Task/resultsP2.csv",
                    data=[subjectName, trialNum, ("\"" + str(xCoord) + ", " + str(yCoord) + "\""), "failed",],
                )
            trialNum += 1
            
            if passedTrials == trialsAmt:
                PgTools.end_screen(screen)
                while True:
                    for event in pg.event.get():
                        PgTools.quit_pg(event)
            start_trial(stimLength, stimHeight)
    pg.display.update()
