#!/usr/bin/env python2
"""
SmiExampleForPuja.py

Illustrate usage of the LibSmi_PsychoPy library from start to finish during an experiment.

Created 8/27/15 by DJ.
"""

# import libraries
from LibSmi_PsychoPy import LibSmi_PsychoPy # for tracker interface
from psychopy import visual, core # for stimuli, events
import time # for filename suffix
import AppKit # for monitor size detection

# declare parameters
params = {
    'fullScreen': True,       # run in full screen mode?
    'screenToShow': 0,        # display on primary screen (0) or secondary (1)?
    'portName': '/dev/tty.usbserial', # name of serial port
    'portBaud': 115200, # speed of serial port (must match iViewX software settings)
    'screenColor': (255,255,255), # color of screen background (in both calibration and stimuli)
    'textColor': (0,0,0) # color of stimuli (in both calibration and stimuli)
}


# Get screen res to allow secondary monitor fullscreen
if params['fullScreen']: 
    screens = AppKit.NSScreen.screens()
    screenRes = (int(screens[params['screenToShow']].frame().size.width), int(screens[params['screenToShow']].frame().size.height))
    if params['screenToShow']>0:
        params['fullScreen'] = False
else:
    screenRes = [800,600]
# print results
print "screenRes = [%d,%d]"%(screenRes[0],screenRes[1])


# Set up serial port by declaring LibSmi object
myTracker = LibSmi_PsychoPy(experiment='PujasExperiment',port=params['portName'], baudrate=params['portBaud'], useSound=True, w=screenRes[0], h=screenRes[1], 
    bgcolor=params['screenColor'],fgcolor=params['textColor'],fullScreen=params['fullScreen'],screenToShow=params['screenToShow'])
print "Port %s isOpen = %d"%(myTracker.tracker.name,myTracker.tracker.isOpen())

# Set up window and experimental stimuli
win = myTracker.win # get the window already declared in the LibSmi initialization
myText = visual.TextStim(win, pos=[0,+.5], wrapWidth=1.5, color=params['textColor'], colorSpace='rgb255', alignHoriz='center', 
    name='myText', text='This is the stimulus',units='norm')

# run calibration and validation
myTracker.run_calibration()

# start recording via serial port
myTracker.start_recording(stream=False)

# Display stimulus (a quick example to show logging)
myText.draw()
win.callOnFlip(myTracker.log,'DisplayStimulus') # log the event in the SMI file
win.flip()
core.wait(2)
win.callOnFlip(myTracker.log,'DisplayBlank') # log the event in the SMI file
win.flip()
core.wait(2)

# Stop recording, save and close serial port
myTracker.stop_recording() # stop recording via serial port
filename = 'PujasExperiment' + time.strftime('_%m_%d_%Y_%H_%M') + '.idf'
myTracker.save_data(filename) # save result (haven't tested this)
myTracker.cleanup() # close serial port