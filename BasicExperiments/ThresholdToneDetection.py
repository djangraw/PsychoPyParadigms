#!/usr/bin/env python2
"""Measure your ability to detect tones near your threshold"""
# ThresholdToneDetection.py
# Created 12/16/14 by DJ based on GetPerceptualThreshold.py

from psychopy import core, visual, gui, data, event, sound
from psychopy.tools.filetools import fromFile, toFile
import time, numpy as np

# ====================== #
# ===== PARAMETERS ===== #
# ====================== #
# Declare parameters
nTrials = 3
ITI_min = 5
ITI_range = 2
tone_freq = 880 # in Hz
min_hit_RT = 200 # in ms
max_hit_RT = 1500 # in ms
#tone_volume = 0.0003


# ========================== #
# ===== SET UP STIMULI ===== #
# ========================== #
try:#try to get a previous parameters file
    expInfo = fromFile('lastThresholdToneParams.pickle')
except:#if not there then use a default set
    expInfo = {'subject':'abc', 'volume':1}
dateStr = time.strftime("%b_%d_%H%M", time.localtime())#add the current time

#present a dialogue to change params
dlg = gui.DlgFromDict(expInfo, title='threshold tone detection', fixed=['date'])
if dlg.OK:
    toFile('lastThresholdToneParams.pickle', expInfo)#save params to file for next time
else:
    core.quit()#the user hit cancel so exit

# get volume from dialogue
tone_volume = expInfo['volume']

#make a text file to save data
fileName = 'ThresholdTone-' + expInfo['subject'] + '-' + dateStr
dataFile = open(fileName+'.txt', 'w')
dataFile.write('key	RT	AbsTime\n')

#create window and stimuli
globalClock = core.Clock()#to keep track of time
trialClock = core.Clock()#to keep track of time
win = visual.Window([800,600],allowGUI=False, monitor='testMonitor', units='deg')
#foil = visual.GratingStim(win, sf=1, size=4, mask='gauss', ori=expInfo['refOrientation'])
#target = visual.GratingStim(win, sf=1,  size=4, mask='gauss', ori=expInfo['refOrientation'])
fixation = visual.GratingStim(win, color='black', tex=None, mask='circle',size=0.2)
message1 = visual.TextStim(win, pos=[0,+3],text='Hit a key when ready.')
message2 = visual.TextStim(win, pos=[0,-3], text="Then press j when you hear a tone.")
# make tone
tone = sound.Sound(value=tone_freq, volume=tone_volume)
# set up hit/miss/false alarm tallies
nHits = np.zeros(nTrials)
nMisses = np.zeros(nTrials)
nFalseAlarms = np.zeros(nTrials)

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

#draw fixation dot
fixation.draw()
win.flip()
core.wait(2) #wait before playing first tone

for iTrial in range(0,nTrials): #will step through the staircase
    
    # get trial time
    tTrial = globalClock.getTime()*1000
    # reset clock
    trialClock.reset()
    
    # play tone
    tone.play()
    
    # do ITI
    ITI = ITI_min + np.random.random()*ITI_range
    core.wait(ITI, ITI)
    
    #get response(s)
    allKeys = event.getKeys(timeStamped=trialClock)
    event.clearEvents()
    print( "Trial %d: t=%f" %(iTrial,tTrial) )
    for thisKey in allKeys:
        key_char = thisKey[0]
        RT = thisKey[1]*1000
        # look for abort
        if key_char in ['q', 'escape']:
            core.quit()#abort experiment
        print "key = %s, RT= %.1f" %(key_char, RT)
        #log the data
        dataFile.write('%s	%.1f	%.1f\n' %(key_char, RT, RT+tTrial))
        # log as hit/miss/falsealarm
        if RT > min_hit_RT and RT < max_hit_RT:
            nHits[iTrial] = 1 # =1 so you can't count two hits per trial.
        else:
            nFalseAlarms[iTrial] += 1
            
    if nHits[iTrial]==0: # if there were no hits on this trial
        nMisses[iTrial] = 1
        


#staircase has ended
dataFile.close()

#give some output to user
print 'Performance:'
print '%d hits, %d misses, %d false alarms' %(np.sum(nHits), np.sum(nMisses), np.sum(nFalseAlarms))

core.quit()
