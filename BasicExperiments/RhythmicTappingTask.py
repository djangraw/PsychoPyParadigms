#!/usr/bin/env python2
"""Implement a timed tapping task."""
# RhythmicTappingTask.py
# Created 12/17/14 by DJ based on NumericalSartTask.py
# Updated 12/29/14 by DJ - debugging, logging
# Updated 1/2/15 by DJ - practice mode, custom respKeys, triggerKey

from psychopy import core, visual, gui, data, event, sound, logging
from psychopy.tools.filetools import fromFile, toFile
import time, numpy as np
import AppKit # for monitor size detection

# ====================== #
# ===== PARAMETERS ===== #
# ====================== #
# Declare primary task parameters
nBlocks = 1         # How many blocks?
toneInterval = 1.0  # time between tones/taps
nTones = 5          # tones in each reminder
fixDur = 3          # time after fixation dot before tone starts
blockDurMin = 300   # seconds before a reminder hapens will be randomly chosen...
blockDurRange = 0   # between blockDurMin and blockDurMin + blockDurRange seconds.
IBI = 2             # time between end of block/probe and beginning of next block
respKey = 'j'       # key to be used for tapping
wanderKey = 'z'     # key to be used to indicate mind-wandering
triggerKey = 't'    # key from scanner that says scan is starting
fullScreen = True   # run in full screen mode?
screenToShow = 1    # display on primary screen (0) or secondary (1)?

# declare tone parameters
toneDur = .250      # duration of tone
toneFreq = 880      # frequency of tone
toneVolume = 1      # volume of tone

# declare probe parameters
probeProb = 0 # probablilty that a given block will be preceded by a probe
probe1_string = 'Where was your attention focused just before this?'
probe1_options = ('Completely on the task','Mostly on the task','Not sure','Mostly on inward thoughts','Completely on inward thoughts')
probe2_string = 'How aware were you of where your attention was?'
probe2_options = ('Very aware','Somewhat aware','Neutral','Somewhat unaware','Very unaware')

# ========================== #
# ===== SET UP LOGGING ===== #
# ========================== #
try:#try to get a previous parameters file
    expInfo = fromFile('lastTappingParams.pickle')
    expInfo['session'] +=1 # increment session number
except:#if not there then use a default set
    expInfo = {'subject':'1', 'session':'1'}
dateStr = time.strftime("%b_%d_%H%M", time.localtime())#add the current time

#present a dialogue to change params
dlg = gui.DlgFromDict(expInfo, title='Rhythmic tapping task', fixed=['date'], order=['subject','session'])
if dlg.OK:
    toFile('lastTappingParams.pickle', expInfo)#save params to file for next time
else:
    core.quit()#the user hit cancel so exit

# Start log file
fileName = 'Tapping-' + expInfo['subject'] + '-' + expInfo['session'] + '-' + dateStr
logging.LogFile((fileName+'.log'), level=logging.INFO)#, mode='w') # w=overwrite
logging.log(level=logging.INFO, msg='---START PARAMETERS---')
logging.log(level=logging.INFO, msg='subject: %s'%expInfo['subject'])
logging.log(level=logging.INFO, msg='session: %s'%expInfo['session'])
logging.log(level=logging.INFO, msg='date: %s'%dateStr)
logging.log(level=logging.INFO, msg='nBlocks: %d'%nBlocks)
logging.log(level=logging.INFO, msg='fixDur: %f'%fixDur)
logging.log(level=logging.INFO, msg='toneInterval: %f'%toneInterval)
logging.log(level=logging.INFO, msg='nTones: %d'%nTones)
logging.log(level=logging.INFO, msg='blockDurMin: %f'%blockDurMin)
logging.log(level=logging.INFO, msg='blockDurRange: %f'%blockDurRange)
logging.log(level=logging.INFO, msg='IBI: %f'%IBI)
logging.log(level=logging.INFO, msg='respKey: %s'%respKey)
logging.log(level=logging.INFO, msg='wanderKey: %s'%wanderKey)
logging.log(level=logging.INFO, msg='triggerKey: %s'%triggerKey)
logging.log(level=logging.INFO, msg='fullScreen: %s'%fullScreen)
logging.log(level=logging.INFO, msg='screenToShow: %s'%screenToShow)
logging.log(level=logging.INFO, msg='toneDur: %f'%toneDur)
logging.log(level=logging.INFO, msg='toneFreq: %f'%toneFreq)
logging.log(level=logging.INFO, msg='toneVolume: %f'%toneVolume)
logging.log(level=logging.INFO, msg='probeProb: %f'%probeProb)
logging.log(level=logging.INFO, msg='---END PARAMETERS---')

#make a text file to save data
#fileName = 'RhythmicTapping-' + expInfo['subject'] + '-' + expInfo['session'] + '-' + dateStr
#dataFile = open(fileName+'.txt', 'w')
#dataFile.write('key	RT	AbsTime\n')


# ========================== #
# ===== SET UP STIMULI ===== #
# ========================== #

# kluge for secondary monitor
if fullScreen and screenToShow>0: 
    screens = AppKit.NSScreen.screens()
    screenRes = screens[screenToShow].frame().size.width, screens[screenToShow].frame().size.height
#    screenRes = [1920, 1200]
    fullScreen = False
else:
    screenRes = [800,600]

#create window and stimuli
globalClock = core.Clock()#to keep track of time
blockClock = core.Clock()#to keep track of time
win = visual.Window(screenRes, monitor='testMonitor', screen=screenToShow, units='deg', name='win', fullscr=fullScreen, allowGUI=False)
fixation = visual.GratingStim(win, color='black', tex=None, mask='circle',size=0.2)
message1 = visual.TextStim(win, pos=[0,+3], alignHoriz='center', name='topMsg', text="aaa")
message2 = visual.TextStim(win, pos=[0,-3], alignHoriz='center', name='bottomMsg', text="bbb")

topPrompts = ["Keep your eyes on the dot at the center of the screen when it appears. You will then hear a series of beeps. Using your right index finger, tap '%c' along with the beeps, then tap at the same interval (as closely as you can) until the dot disappears."%respKey.upper(), 
    "If at any time you notice that your mind has been wandering, press the '%c' key with your left index finger."%wanderKey.upper(),
    "Sometimes, a question may appear. When this happens, stop tapping and answer the question using the number keys."]
bottomPrompts = ["Press any key to continue.",
    "Press any key to continue.",
    "WHEN YOU'RE READY TO BEGIN, press any key."]

# make tone
tone = sound.Sound(value=toneFreq, volume=toneVolume, secs=toneDur, name='tone')

# ============================ #
# ======= SUBFUNCTIONS ======= #
# ============================ #

def RunBlock(blockDur):
    
    # get block time
    tBlock = globalClock.getTime()*1000
    # reset clock
    blockClock.reset()
    
    #draw fixation dot
    fixation.draw()
    win.logOnFlip(level=logging.EXP, msg='Display Fixation')
    win.flip()
    core.wait(fixDur, fixDur)#wait for specified ms (use a loop of x frames for more accurate timing)
    
    # play tone repeatedlyj
    for i in range(0,nTones):
        tone.play()
        core.wait(toneInterval, toneInterval)
    
    core.wait(blockDur, blockDur)#wait for specified ms (use a loop of x frames for more accurate timing)
    
    #get response
    allKeys = event.getKeys(timeStamped=blockClock)
    return (tBlock,allKeys)


def RunProbes():
    # reset clock
    blockClock.reset()
    # set up stimuli
    message1.setText(probe1_string)
    message2.setText("1) %s\n2) %s\n3) %s\n4) %s\n5) %s" % probe1_options)
    message1.draw()
    message2.draw()
    win.logOnFlip(level=logging.EXP, msg='Display Probe1')
    win.flip()
    
    # get response
    key1 = event.waitKeys(keyList=['1','2','3','4','5','q','escape'],timeStamped=blockClock)
    
    # reset clock
    blockClock.reset()
    # set up stimuli
    message1.setText(probe2_string)
    message2.setText("1) %s\n2) %s\n3) %s\n4) %s\n5) %s" % probe2_options)
    message1.draw()
    message2.draw()
    win.logOnFlip(level=logging.EXP, msg='Display Probe2')
    win.flip()
    
    # get response
    key2 = event.waitKeys(keyList=['1','2','3','4','5','q','escape'],timeStamped=blockClock)
    
    # return results
    return (key1[0],key2[0])
    

# =========================== #
# ======= RUN PROMPTS ======= #
# =========================== #

# display prompts
iProbe = 0
while iProbe < len(topPrompts):
    message1.setText(topPrompts[iProbe])
    message2.setText(bottomPrompts[iProbe])
    #display instructions and wait
    message1.draw()
    message2.draw()
    win.logOnFlip(level=logging.EXP, msg='Display Instructions%d'%(iProbe+1))
    win.flip()
    #check for a keypress
    thisKey = event.waitKeys()
    if thisKey[0] in ['q','escape']:
        core.quit()
    elif thisKey[0] == 'backspace':
        iProbe = 0
    else:
        iProbe += 1

# wait for scanner
message1.setText("Waiting for scanner to start...")
message2.setText("(Press '%c' to override.)"%triggerKey.upper())
message1.draw()
message2.draw()
win.logOnFlip(level=logging.EXP, msg='Display WaitingForScanner')
win.flip()
event.waitKeys(keyList=triggerKey)

# do brief wait before first stimulus
#fixation.draw()
#win.logOnFlip(level=logging.EXP, msg='Display Fixation')
#win.flip()
#core.wait(IBI, IBI)


# =========================== #
# ===== MAIN EXPERIMENT ===== #
# =========================== #

logging.log(level=logging.EXP, msg='---START EXPERIMENT---')

for iBlock in range(0,nBlocks): #Run blocks
    
    # log new block
    logging.log(level=logging.EXP, msg='Start Block %d'%iBlock)
    
    # determine block duration
    blockDur = blockDurMin + np.random.random()*blockDurRange
    
    # Run Block
    (tBlock,allKeys) = RunBlock(blockDur)
    
    # Evaluate results
    for thisKey in allKeys:
        keyChar = thisKey[0]
        RT = thisKey[1]*1000 # in ms
        #log the data
#        dataFile.write('%s	%.1f	%.1f\n' %(keyChar, RT, RT+tBlock))
        print("key=%s, RT=%.1f"%(keyChar,RT))
        # look for escape character
        if thisKey[0] in ['q', 'escape']:
            core.quit()#abort experiment
    event.clearEvents('mouse')#only really needed for pygame windows
    
    # Run probe trial
    if (np.random.random() < probeProb):
        # run probe trial
        allKeys = RunProbes()
        # check for escape keypresses
        for thisKey in allKeys:
            if thisKey[0] in ['q', 'escape']:
                core.quit()#abort experiment
        event.clearEvents('mouse')#only really needed for pygame windows
        # record keypresses
        attentionLevel = allKeys[0][0]
        attentionRT = allKeys[0][1]*1000
        awarenessLevel = allKeys[1][0]
        awarenessRT = allKeys[1][1]*1000
        #log the data
        print('Probe: attention %s, awareness %s'%(attentionLevel,awarenessLevel))
#        dataFile.write('Probe1	%.1f	%s\n' %(attentionRT, attentionLevel))
#        dataFile.write('Probe2	%.1f	%s\n' %(awarenessRT, awarenessLevel))
    
    # skip IBI on last block
    if iBlock < (nBlocks-1):
        # Display wait screen
        message1.setText("Take a break! When you're ready to begin a new block, press any key.")
        message1.draw()
        win.logOnFlip(level=logging.EXP, msg='Display BreakTime')
        win.flip()
        thisKey = event.waitKeys()
        if thisKey[0] in ['q', 'escape']:
            core.quit() #abort experiment
        # do IBI (blank screen)
        win.logOnFlip(level=logging.EXP, msg='Display Blank')
        win.flip()
        core.wait(IBI,IBI)

# close log file
#dataFile.close()

# exit experiment
core.quit()
