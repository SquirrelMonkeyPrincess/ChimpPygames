import sys
import os
import pygame as pg
from pygame.locals import *
sys.path.append(os.path.join("/home", "pi", "Desktop", "ChimpPygames", "PygameTools"))
import PgTools
import time

# initialize pygame and screen
pg.init()
screen = PgTools.Screen()

# init font for trial counter
font = pg.font.SysFont(None, 48)

file = open("Training_Task/parametersP1.dat")
params = PgTools.get_params(file)
file.close()

subjectName = str(params["subject_name"])
trialsAmt = int(params["number_of_trials"]) + 1
stimLength = int(params["first_stimulus_length"])
stimHeight = int(params["first_stimulus_height"])
lastLength = int(params["last_stimulus_length"])
lastHeight = int(params["last_stimulus_height"])
passDelay = int(params["passed_inter_trial_interval"])
failDelay = int(params["failed_inter_trial_interval"])
if "y" in str(params["randomly_shaped_stimuli"]) or "Y" in str(params["randomly_shaped_stimuli"]):
    randShapes = True
else:
    randShapes = False

# lengthDecrease = (stimLength - lastLength) / (trialsAmt - 1)
# heightDecrease = (stimHeight - lastHeight) / (trialsAmt - 1)
lengthDecrease = 5
heightDecrease = 5

def start_trial(length, height):
    """
    Initiates a new trial, draws stimulus
    :param length: length of new stimulus
    :param height: width of new stimulus
    """
    screen.refresh()
    global stimulus
    stimulus = pg.draw.rect(screen.fg,PgTools.BLUE,((int((PgTools.SCREEN_SIZE[0] - length) / 2),
            int((PgTools.SCREEN_SIZE[1] - height) / 2),),
            (length, height),),)
        
    if randShapes:
        PgTools.rand_shape(screen.fg, (
                    int((PgTools.SCREEN_SIZE[0] - length) / 2),
                    int((PgTools.SCREEN_SIZE[1] - height) / 2),
                    ),(length, height))


PgTools.write_ln(
    filename="Training_Task/resultsP1.csv",
    data=["subject_name", "trial", "stimulus_size", "input_coordinates", "accuracy",],
)

trialNum = 1
start_trial(stimLength, stimHeight)

# game loop
running = True

# params for deliberate touch
touched_down = False   # tells us whether the animal has already touched
when_they_started_their_touch = 0
min_touch_ms_required = 50
max_touch_ms = 3000

# int to track color changes
color_tracker = 0

while running:
    # ensure stimulus does not get smaller than specified size
    if stimHeight < lastHeight:
        stimHeight = lastHeight
    if stimLength < lastLength:
        stimLength = lastLength    

# disply trial number and stimulus size in upper left corner
    text = font.render('Trial #{} ({}, {})'.format(trialNum, stimLength, stimHeight), True, Color('salmon'))
    screen.fg.blit(text, (20, 20))
    
    # set stimulus flicker rate and colors
    color_tracker = color_tracker + 1
    
    if color_tracker % 10 == 0:
        pg.draw.rect(screen.fg, PgTools.AQUA,((int((PgTools.SCREEN_SIZE[0] - stimLength) / 2),
                                            int((PgTools.SCREEN_SIZE[1] - stimHeight) / 2),), (stimLength, stimHeight),),)
    else:
        pg.draw.rect(screen.fg, PgTools.BLUE,((int((PgTools.SCREEN_SIZE[0] - stimLength) / 2),
                                            int((PgTools.SCREEN_SIZE[1] - stimHeight) / 2),), (stimLength, stimHeight),),)
    
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

                if stimulus.collidepoint(xCoord, yCoord) and screen.fg.get_at((xCoord, yCoord)) != (0,0,0):
                    PgTools.response(screen, True, passDelay)
                    PgTools.write_ln(
                        filename="Training_Task/resultsP1.csv",
                        data=[
                            subjectName,
                            trialNum,
                            "\"" + str((stimLength, stimHeight)) + "\"",
                            "\"" + str((xCoord, yCoord)) + "\"",
                            "passed",
                        ],
                    )
                    stimLength -= lengthDecrease
                    stimHeight -= heightDecrease
                else:
                    PgTools.response(screen, False, failDelay)
                    PgTools.write_ln(
                        filename="Training_Task/resultsP1.csv",
                        data=[
                            subjectName,
                            trialNum,
                            "\"" + str((stimLength, stimHeight)) + "\"",
                            "\"" + str((xCoord, yCoord)) + "\"",
                            "failed",
                        ],
                    )
                trialNum += 1
            
                if trialNum == trialsAmt:
                    PgTools.end_screen(screen)
                    while True:
                        for event in pg.event.get():
                            PgTools.quit_pg(event)
                start_trial(stimLength, stimHeight)
    pg.display.update()
    pg.time.delay(100)
    
