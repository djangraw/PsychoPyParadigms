#!/usr/bin/env python2
"""Implement an association task based on the game BopIt:
    Each tone matches a different button press."""
# BopItTask.py
# Created 12/17/14 by DJ based on fourLetterTask.py
# Updated 12/29/14 by DJ - new sounds, debugging, logging
# Updated 1/2/15 by DJ - practice mode, custom respKeys, triggerKey

from psychopy import core, visual, gui, data, event, sound, logging
from psychopy.tools.filetools import fromFile, toFile
import time, numpy as np
import AppKit # for monitor size detection

# ====================== #
# ===== PARAMETERS ===== #
# ====================== #
# Declare primary task parameters
isPractice = False      # give subject feedback when they get it wrong?
respKeys = ['j','k','l'] # 3 keys for tones 1, 2, and 3
triggerKey = 't'        # key from scanner that says scan is starting
wanderKey = 'z'         # key to be used to indicate mind-wandering
nBlocks = 1             # how many blocks will there be?
nTrialsPerBlock = 200   # how many trials between breaks?
fixDur_min = 0.0        # min time between one trial ending and the next starting (in seconds)
fixDur_range = 1.0      # fixDur will be between fixDur_min and fixDur_min + fixDur_range seconds.
toneDur = 0.2           # duration of tone (in seconds)
respDur = 1.0           # max time (after start of tone) to respond (in seconds)
preBlockDur = 3              # time that fixation dot is displayed before starting a block of trials (in seconds)
IBI = 4                 # time between end of block/probe and beginning of next block (in seconds)
fullScreen = True       # run in full screen mode?
screenToShow = 1    # display on primary screen (0) or secondary (1)?

#tones = ['c','f','a'] # note options
tones = ['chirps/up.wav','chirps/updown.wav','chirps/updownup.wav'] # wav file options
#tones = ['one.wav','two.wav','three.wav'] # speech options
toneVolume = 0.5


# declare probe parameters
probeProb = 0 # probablilty that a given trial will be preceded by a probe
probe1_string = 'Where was your attention focused just before this?'
probe1_options = ('Completely on the task','Mostly on the task','Not sure','Mostly on inward thoughts','Completely on inward thoughts')
probe2_string = 'How aware were you of where your attention was?'
probe2_options = ('Very aware','Somewhat aware','Neutral','Somewhat unaware','Very unaware')


# ========================== #
# ===== SET UP LOGGING ===== #
# ========================== #

try:#try to get a previous parameters file
    expInfo = fromFile('lastBopItParams.pickle')
    expInfo['session'] +=1 # increment session number
except:#if not there then use a default set
    expInfo = {'subject':'1', 'session':1}
dateStr = time.strftime("%b_%d_%H%M", time.localtime())#add the current time

#present a dialogue to change params
dlg = gui.DlgFromDict(expInfo, title='BopIt Task', fixed=['date'], order=['subject','session'])
if dlg.OK:
    toFile('lastBopItParams.pickle', expInfo)#save params to file for next time
else:
    core.quit()#the user hit cancel so exit

# Start log file
fileName = 'BopIt-%s-%d-%s'%(expInfo['subject'],expInfo['session'],dateStr) #'BopIt-' + expInfo['subject'] + '-' + expInfo['session'] + '-' + dateStr
logging.LogFile((fileName+'.log'), level=logging.INFO)#, mode='w') # w=overwrite
logging.log(level=logging.INFO, msg='---START PARAMETERS---')
logging.log(level=logging.INFO, msg='subject: %s'%expInfo['subject'])
logging.log(level=logging.INFO, msg='session: %s'%expInfo['session'])
logging.log(level=logging.INFO, msg='date: %s'%dateStr)
logging.log(level=logging.INFO, msg='isPractice: %i'%isPractice)
logging.log(level=logging.INFO, msg='respKeys: %s'%respKeys)
logging.log(level=logging.INFO, msg='triggerKey: %s'%triggerKey)
logging.log(level=logging.INFO, msg='wanderKey: %s'%wanderKey)
logging.log(level=logging.INFO, msg='nBlocks: %d'%nBlocks)
logging.log(level=logging.INFO, msg='nTrialsPerBlock: %d'%nTrialsPerBlock)
logging.log(level=logging.INFO, msg='fixDur_min: %f'%fixDur_min)
logging.log(level=logging.INFO, msg='fixDur_range: %f'%fixDur_range)
logging.log(level=logging.INFO, msg='toneDur: %f'%toneDur)
logging.log(level=logging.INFO, msg='respDur: %f'%respDur)
logging.log(level=logging.INFO, msg='preBlockDur: %f'%preBlockDur)
logging.log(level=logging.INFO, msg='IBI: %f'%IBI)
logging.log(level=logging.INFO, msg='tones: %s'%tones)
logging.log(level=logging.INFO, msg='toneVolume: %f'%toneVolume)
logging.log(level=logging.INFO, msg='probeProb: %s'%probeProb)
logging.log(level=logging.INFO, msg='---END PARAMETERS---')

#make a text file to save data
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
trialClock = core.Clock()#to keep track of time
win = visual.Window(screenRes, fullscr=fullScreen, allowGUI=False, monitor='testMonitor', screen=screenToShow, units='deg', name='win')
#fixation = visual.GratingStim(win, color='black', tex=None, mask='circle',size=0.2)
fixation = visual.ShapeStim(win,lineColor='#000000',lineWidth=3.0,vertices=((-30,0),(30,0),(0,0),(0,30),(0,-30)),units='pix',closeShape=False);

message1 = visual.TextStim(win, pos=[0,+3], color='#000000', alignHoriz='center', name='topMsg', text="aaa")
message2 = visual.TextStim(win, pos=[0,-3], color='#000000', alignHoriz='center', name='bottomMsg', text="bbb")

topPrompts = ["Keep your eyes on the cross at the center of the screen when it appears. Then listen for one of the following three sounds.",
    "When you hear this sound, press %c as quickly as you can."%respKeys[0].upper(),
    "When you hear this sound, press %c as quickly as you can."%respKeys[1].upper(),
    "When you hear this sound, press %c as quickly as you can."%respKeys[2].upper(), 
    "Please respond as quickly as possible without sacrificing accuracy.",
    "If at any time you notice that your mind has been wandering, press the 'z' key with your left index finger.",
    "Sometimes, a question may appear. When this happens, answer the question using the number keys."]
bottomPrompts = ["Press any key to continue.",
    "Press any key to continue.",
    "Press any key to continue.",
    "Press Backspace to hear the sounds again or any other key to continue.",
    "Press any key to continue.",
    "Press any key to continue.",
    "WHEN YOU'RE READY TO BEGIN, press any key."]
promptTones = [""] + tones + ["", "",""]


# ============================ #
# ======= SUBFUNCTIONS ======= #
# ============================ #

def RunBlock(nTrials):
    
    # get trial start time
    tBlock = globalClock.getTime()*1000
    # clear event buffer
    event.clearEvents()
    allKeys = []
    for i in range(0,nTrials):
        # reset trial clock
        trialClock.reset()
        # wait for fixDur
        fixDur = fixDur_min + np.random.random()*fixDur_range
        if fixDur>0:
#            fixation.draw()
#            win.logOnFlip(level=logging.EXP, msg='Display Fixation')
#            win.flip()
            core.wait(fixDur,fixDur)#wait for specified ms (use a loop of x frames for more accurate timing)
        
        # make tone
        iTone = np.random.choice(range(0,len(tones)))
        tone = sound.Sound(value=tones[iTone], secs=toneDur, volume=toneVolume, name='tone%d'%(iTone+1))
        tone.play()
        
        # pause brielfy
        core.wait(respDur,respDur) 
        
        # get responses
        newKeys = event.getKeys(timeStamped=trialClock)
        endBlock = False # check for escape character
        for thisKey in newKeys:
            if thisKey[0] in ['q','escape']:
                endBlock = True
        allKeys.append(newKeys[:])
        # obey escape character, if one was entered.
        if endBlock:
            break
        
        if isPractice:
            # if wrong answer, inform the subject!
            if len(newKeys) != 1 or newKeys[0][0] != respKeys[iTone]:
                print("WRONG!")
                tone = sound.Sound(150, secs=1,volume=toneVolume, name='buzzer')
                tone.play()
                message1.text = 'WRONG! The correct button was %c.'%respKeys[iTone].upper()
                message2.text  = 'Press any key to resume.'
                message1.draw()
                message2.draw()
                win.logOnFlip(level=logging.EXP, msg='Display WrongAnswer')
                win.flip()
                event.waitKeys()
                # end block
    #            break
                # do brief wait before resuming stimuli
                fixation.draw()
                win.logOnFlip(level=logging.EXP, msg='Display Fixation')
                win.flip()
                core.wait(preBlockDur,preBlockDur)
            else:
                allKeys.append(newKeys[:])
    #    allKeys = event.getKeys(timeStamped=trialClock)
    return (tBlock,allKeys)


def RunProbes():
    # reset clock
    trialClock.reset()
    # set up stimuli
    message1.setText(probe1_string)
    message2.setText("1) %s\n2) %s\n3) %s\n4) %s\n5) %s" % probe1_options)
    message1.draw()
    message2.draw()
    win.logOnFlip(level=logging.EXP, msg='Display Probe1')
    win.flip()
    
    # get response
    key1 = event.waitKeys(keyList=['1','2','3','4','5','q','escape'],timeStamped=trialClock)
    
    # reset clock
    trialClock.reset()
    # set up stimuli
    message1.setText(probe2_string)
    message2.setText("1) %s\n2) %s\n3) %s\n4) %s\n5) %s" % probe2_options)
    message1.draw()
    message2.draw()
    win.logOnFlip(level=logging.EXP, msg='Display Probe2')
    win.flip()
    
    # get response
    key2 = event.waitKeys(keyList=['1','2','3','4','5','q','escape'],timeStamped=trialClock)
    
    # return results
    return (key1[0],key2[0])
    

# =========================== #
# ======= RUN PROMPTS ======= #
# =========================== #


# display prompts and play corresponding tones
iPrompt=0
while iPrompt < len(topPrompts):
    #set instructions
    message1.setText(topPrompts[iPrompt])
    message2.setText(bottomPrompts[iPrompt])
    #display instructions
    message1.draw()
    message2.draw()
    win.logOnFlip(level=logging.EXP, msg='Display Instructions%d'%(iPrompt+1))
    win.flip()
    
    if len(promptTones[iPrompt]) > 0:
        tone = sound.Sound(value=promptTones[iPrompt], secs=0.5, volume=toneVolume, name='tone')
        tone.play()
    # display for at least 0.5s so they don't automatically skip
    core.wait(0.5)
    # wait for a keypress
    thisKey = event.waitKeys()
    # look for special character
    if thisKey[0] in ['q','escape']:
        core.quit()
    elif thisKey[0] == 'backspace':
        iPrompt=1
    else:
        iPrompt+=1

# wait for scanner
message1.setText("Waiting for scanner to start...")
message2.setText("(Press '%c' to override.)"%triggerKey.upper())
message1.draw()
message2.draw()
win.logOnFlip(level=logging.EXP, msg='Display WaitingForScanner')
win.flip()
event.waitKeys(keyList=triggerKey)


# =========================== #
# ===== MAIN EXPERIMENT ===== #
# =========================== #

# Run the main experiment!
logging.log(level=logging.EXP, msg='---START EXPERIMENT---')

for iBlock in range(0,nBlocks): #will step through the blocks
    
    # log new block
    logging.log(level=logging.EXP, msg='Start Block %d'%(iBlock+1))
    
    # do brief wait before first stimulus
    fixation.draw()
    win.logOnFlip(level=logging.EXP, msg='Display Fixation')
    win.flip()
    core.wait(preBlockDur,preBlockDur)
    
    # play sequence
    (tBlock,allKeys) = RunBlock(nTrialsPerBlock)
    for thisKey in allKeys:
        if len(thisKey)>0 and (thisKey[0] in ['q', 'escape']):
            core.quit() # abort experiment
    
    # Run probe trial
    if (np.random.random() < probeProb):
        # run probe trial
        allKeys = RunProbes()
        # check for escape keypresses
        for thisKey in allKeys:
            if thisKey[0] in ['q', 'escape']:
                core.quit() #abort experiment
        event.clearEvents('mouse')#only really needed for pygame windows
        # record keypresses
        attentionLevel = allKeys[0][0]
        attentionRT = allKeys[0][1]*1000
        awarenessLevel = allKeys[1][0]
        awarenessRT = allKeys[1][1]*1000
    
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

# exit experiment
core.quit()
