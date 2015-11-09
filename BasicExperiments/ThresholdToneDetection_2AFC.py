#!/usr/bin/env python2
"""Measure your ability to detect tones near your threshold"""
# ThresholdToneDetection_2AFC.py
# Created 12/16/14 by DJ based on GetPerceptualThreshold.py

from psychopy import core, visual, gui, data, event, sound
from psychopy.tools.filetools import fromFile, toFile
import time, numpy

# ====================== #
# ===== PARAMETERS ===== #
# ====================== #
# Declare parameters
nTrials = 10
ITI_min = 1
ITI_range = 1
tone_freq = 880 # in Hz
tone_prob = 0.5 # probability that tone will be heard on a given trial
#tone_volume = 0.0003

# ========================== #
# ===== SET UP STIMULI ===== #
# ========================== #
try:#try to get a previous parameters file
    expInfo = fromFile('lastThresholdTone2afcParams.pickle')
except:#if not there then use a default set
    expInfo = {'subject':'abc', 'volume':1}
dateStr = time.strftime("%b_%d_%H%M", time.localtime())#add the current time

#present a dialogue to change params
dlg = gui.DlgFromDict(expInfo, title='threshold tone detection', fixed=['date'])
if dlg.OK:
    toFile('lastThresholdTone2afcParams.pickle', expInfo)#save params to file for next time
else:
    core.quit()#the user hit cancel so exit

# get volume from dialogue
tone_volume = expInfo['volume']

#make a text file to save data
fileName = 'ThresholdTone2afc-' + expInfo['subject'] + '-' + dateStr
dataFile = open(fileName+'.txt', 'w')
dataFile.write('isOn	RT	correct\n')

#create window and stimuli
globalClock = core.Clock()#to keep track of time
trialClock = core.Clock()#to keep track of time
win = visual.Window([800,600],allowGUI=False, monitor='testMonitor', units='deg')
#foil = visual.GratingStim(win, sf=1, size=4, mask='gauss', ori=expInfo['refOrientation'])
#target = visual.GratingStim(win, sf=1,  size=4, mask='gauss', ori=expInfo['refOrientation'])
fixation = visual.GratingStim(win, color='black', tex=None, mask='circle',size=0.2)
message1 = visual.TextStim(win, pos=[0,+3],text='Hit a key when ready.')
message2 = visual.TextStim(win, pos=[0,-3], text="Then press j when you hear a tone, k if you don't.")
# make tone
tone = sound.Sound(value=tone_freq, volume=tone_volume)


# =========================== #
# ===== MAIN EXPERIMENT ===== #
# =========================== #
#display instructions and wait
message1.draw()
message2.draw()
fixation.draw()
win.flip()
#check for a keypress
event.waitKeys()
performance = []

for iTrial in range(0,nTrials): #will step through the staircase
    # do ITI
    win.flip()
    ITI = ITI_min + numpy.random.random()*ITI_range
    core.wait(ITI)
    
    # determine trial type
    isOn = (numpy.random.random() < tone_prob)
    
    # reset clock
    trialClock.reset()
    
    #draw fixation dot
    fixation.draw()
    win.flip()
    
    core.wait(0.5)#wait 500ms (use a loop of x frames for more accurate timing)
    
    # play tone
    if isOn:
        tone.play()
    
    #get response
    thisResp=None
    RT = None
    while thisResp is None:
        allKeys=event.waitKeys(timeStamped=trialClock)
        for thisKey in allKeys:
            if (thisKey[0]=='j' and isOn) or (thisKey[0]=='k' and not isOn):
                thisResp = 1#correct
                RT = thisKey[1]*1000
            elif (thisKey[0]=='j' and not isOn) or (thisKey[0]=='k' and isOn):
                thisResp = 0#incorrect
                RT = thisKey[1]*1000
            elif thisKey[0] in ['q', 'escape']:
                core.quit()#abort experiment
        event.clearEvents('mouse')#only really needed for pygame windows
    
    print "key pressed = %s, isOn = %r, correct = %d, RT= %.1f" %(thisKey[0],isOn,thisResp,RT)
    #log the data
    dataFile.write('%i	%.1f	%i\n' %(isOn, RT, thisResp))
    performance.append(thisResp)

#staircase has ended
dataFile.close()

#give some output to user
print 'Performance:'
print '%d/%d = %.2f%% correct' %(numpy.sum(performance), len(performance), 100*numpy.average(performance))

core.quit()
