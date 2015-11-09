#!/usr/bin/env python2
"""Implements the local-global attention task 
as described in Weissman, Nature Neurosci. 2006 (doi: 10.1038/nn1727)"""
# LocalGlobalAttention.py
# Created 12/10/14 by DJ based on # RunQandA.py.

import random
from psychopy import visual, event, core

#declare parameters
nTrials = 10
cueDur_sec = 2
preStimDur_sec = 1
stimDur_sec = 2
ITI_min = 2.5 # in seconds
ITI_range = 1.5 # in seconds. ITI will range from ITI_min to (ITI_min+ITI_range)

#declare Q&A
stims_all = ('S   S\nS   S\nS   S\nS   S\nSSSSS\nS   S\nS   S\nS   S\nS   S',
                '  S\n S S\nS   S\n S\n  S\n   S\nS   S\n S S\n  S',
                'H   H\nH   H\nH   H\nH   H\nHHHHH\nH   H\nH   H\nH   H\nH   H',
                '  H\n H H\nH   H\n H\n  H\n   H\nH   H\n H H\n  H')
cues_all = ('small','LARGE')
smallLetter = ('S','S','H','H')
largeLetter = ('H','S','H','S')

#create a window to draw in
win = visual.Window((600,600), allowGUI=False, monitor='TestMonitor',units='deg')
    
message1 = visual.TextStim(win, pos=[0,+3],text="A cue will tell you whether to pay attention to the 'small' letters or the 'LARGE' ones. Then you will see small letters (S or H) arranged in the shape of a large letter (S or H). If the cue was 'LARGE', type the large letter. If it was 'small', type the small letter.")
message2 = visual.TextStim(win, pos=[0,-3], text="When you're ready to begin, press any key.")

textStim = visual.TextStim(win,text='Hit Q or Esc to quit',
    pos=(0,0),font='Monaco')


#Create a clock object.
clock = core.Clock()

# ============================ #
# ======= SUBFUNCTIONS ======= #
# ============================ #

def RunAttentionTrial(cue,stim,cueDur,preStimDur,stimDur):
    # --- SET UP
    #Flush the key buffer and mouse movements
    event.clearEvents()
    #Reset our clock to zero  - I think this call should take less time than window.flip, so resetting after the flip should be slightly more accurate.
    clock.reset()
    
    # --- DISPLAY
    # display cue
    textStim.setText(cue)
    textStim.draw()
    win.flip() #Put the image on the screen
    core.wait(cueDur,cueDur) # tie up the CPU for cueDur seconds.
    # display blank
    textStim.setText('')
    textStim.draw()
    win.flip()
    core.wait(preStimDur,preStimDur) # tie up the CPU for preStimDur seconds.
    # display stimulus
    textStim.setText(stim)
    textStim.draw()
    win.flip() #Put the image on the screen
    #Wait stimDur seconds.  Tie up the CPU the entire time (this is more accurate than letting other processes go)
    core.wait(stimDur,stimDur)
    
    # --- CLEAN UP
    #Get a list of all keys that were pressed during our wait.  Tell it to give also give us the amount of time since our clock was reset when the key was pressed (reaction time).
    keypresses = event.getKeys(None,clock)
    return keypresses



# =========================== #
# ===== MAIN EXPERIMENT ===== #
# =========================== #
#display instructions and wait
message1.draw()
message2.draw()
win.flip()

#check for a keypress
event.waitKeys()

# do ITI before first stimulus
win.flip()
ITI = ITI_min + random.random()*ITI_range
core.wait(ITI)

# Main Experiment
for i in range(0,nTrials):
    
    # select parameters
    iStim = random.randrange(len(stims_all))
    stim = stims_all[iStim]
    iCue = random.randrange(len(cues_all))
    cue = cues_all[iCue]
    # get correct answer
    if cue=='small':
        answer = smallLetter[iStim]
    else:
        answer = largeLetter[iStim]
    # get ITI
    ITI = ITI_min + (ITI_range * random.random())

    
    # print trial number
    print "---Trial %d:" %i
    print "answer = %s:" %answer
    
    #display new question
    keys = RunAttentionTrial(cue,stim,cueDur_sec,preStimDur_sec,stimDur_sec)
    
    # log result
    for key in keys:
        if key[0].lower() == answer.lower(): # case insensitive comparison
            print "Correct!"
        else:
            print "Incorrect."
        print "Key: %s  RT: %.3f" %(key[0],key[1]*1000)
    
        # check for end command
        if key[0] in ['escape','q']:
            # abort experiment
            print 'Experiment aborted by user.'
            win.close()
            core.quit()
    event.clearEvents('mouse')#only really needed for pygame windows
   
    # pause briefly 
    core.wait(ITI) 