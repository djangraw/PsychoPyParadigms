#!/usr/bin/env python2
"""Measure your perceptual threshold for tones using a staircase method"""
# GetPerceptualThreshold.py
# Created 12/16/14 by DJ based on JND_staircase_exp.py

from psychopy import core, visual, gui, data, event, sound
from psychopy.tools.filetools import fromFile, toFile
import time, numpy

# ====================== #
# ===== PARAMETERS ===== #
# ====================== #
# Declare parameters
ITI_min = 1
ITI_range = 1
tone_freq = 880 # in Hz
tone_prob = 0.5 # probability that tone will be heard on a given trial
tone_startvol = 0.01

# ========================== #
# ===== SET UP STIMULI ===== #
# ========================== #
try:#try to get a previous parameters file
    expInfo = fromFile('lastThresholdParams.pickle')
except:#if not there then use a default set
    expInfo = {'subject':'abc', 'refOrientation':0}
dateStr = time.strftime("%b_%d_%H%M", time.localtime())#add the current time

#present a dialogue to change params
dlg = gui.DlgFromDict(expInfo, title='perceptual threshold staircase', fixed=['date'])
if dlg.OK:
    toFile('lastThresholdParams.pickle', expInfo)#save params to file for next time
else:
    core.quit()#the user hit cancel so exit

#make a text file to save data
fileName = 'GetThreshold-' + expInfo['subject'] + '-' + dateStr
dataFile = open(fileName+'.txt', 'w')
dataFile.write('isOn	Increment	correct\n')

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
tone = sound.Sound(value=tone_freq,volume=1)

#create the staircase handler
staircase = data.StairHandler(startVal = tone_startvol,
                          stepType = 'lin', stepSizes=[.002,.001,.001,.0005,.0005,.0001,.0001], #reduce step size every two reversals
                          minVal=0, maxVal=1,
                          nUp=1, nDown=1,  #(1,1) -> 50% threshold, (1,3)will home in on the 80% threshold
                          nTrials=50)


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

for thisIncrement in staircase: #will step through the staircase
    # do ITI
    win.flip()
    ITI = ITI_min + numpy.random.random()*ITI_range
    core.wait(ITI)
    
    # determine trial type
    isOn = (numpy.random.random() < tone_prob)
    print "volume = %f"%thisIncrement

    #set orientation of probe
    tone.setVolume(thisIncrement)

    #draw all stimuli
    fixation.draw()
    win.flip()
    
    core.wait(0.5)#wait 500ms (use a loop of x frames for more accurate timing)
    
    # play tone
    if isOn:
        tone.play()
    
    #get response
    thisResp=None
    while thisResp is None:
        allKeys=event.waitKeys()
        for thisKey in allKeys:
            if (thisKey=='j' and isOn) or (thisKey=='k' and not isOn):
                thisResp = 1#correct
            elif (thisKey=='j' and not isOn) or (thisKey=='k' and isOn):
                thisResp = 0#incorrect
            elif thisKey in ['q', 'escape']:
                core.quit()#abort experiment
        event.clearEvents('mouse')#only really needed for pygame windows
    
    print "key pressed = %s, isOn = %r, correct = %d" %(thisKey,isOn,thisResp)
    #add the data to the staircase so it can calculate the next level
    staircase.addResponse(thisResp)
    dataFile.write('%i	%.5f	%i\n' %(isOn, thisIncrement, thisResp))

#staircase has ended
dataFile.close()
staircase.saveAsPickle(fileName)#special python binary file to save all the info

#give some output to user
print 'reversals:'
print staircase.reversalIntensities
print 'mean of final 6 reversals = %.4f' %(numpy.average(staircase.reversalIntensities[-6:]))

core.quit()
