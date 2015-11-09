#!/usr/bin/env python2
"""Implement the modified SART (sustained attention response task) 
described in Morrison 2014 (doi: 10.3389/fnhum.2013.00897)"""
# NumericalSartTask.py
# Created 12/16/14 by DJ based on ThresholdToneDetection.py
# Updated 1/5/15 by DJ - added logging, key options, cleaned up

from psychopy import core, visual, gui, data, event, sound, logging
from psychopy.tools.filetools import fromFile, toFile
import time, numpy as np
import AppKit # for monitor size detection

# ====================== #
# ===== PARAMETERS ===== #
# ====================== #
# Declare primary task parameters
isPractice = False      # give subject feedback when they get it wrong?
nBlocks = 1             # how many blocks will there be?
nTrialsPerBlock = 200   # how many trials between breaks?
fixDur_min = 0          # fixation dot before digit appears
fixDur_range = 1.0      # fixDur will be between fixDur_min and fixDur_min + fixDur_range seconds.
digitDur = 0.100        # time digit is onscreen (in seconds)
respDur = 1.0           # max time (after onset of digit) to respond (in seconds)
ITI = 0                 # time between response period and fixation dot reappearance (in seconds)
IBI = 10                 # time between end of block/probe and beginning of next block (in seconds)
targetDigit = 3         # the only digit to elicit no response
respKey = 'j'           # key to be used for responses
wanderKey = 'z'         # key to be used to indicate mind-wandering
triggerKey = 't'        # key from scanner that says scan is starting
targetFrac = 0.10       # fraction of trials that should be targets
targetProb = 1/(1/targetFrac - 1)  # probability of target on a trial that doesn't follow a target
                                   # (since targets are always followed by non-targets)
fullScreen = True      # run in full screen mode?
screenToShow = 0    # display on primary screen (0) or secondary (1)?
fixCrossSize = 10       # size of cross, in pixels

# declare probe parameters
probeProb = 0 # probablilty that a given block will be followed by a probe
probe1_string = 'Where was your attention focused just before this?'
probe1_options = ('Completely on the task','Mostly on the task','Not sure','Mostly on inward thoughts','Completely on inward thoughts')
probe2_string = 'How aware were you of where your attention was?'
probe2_options = ('Very aware','Somewhat aware','Neutral','Somewhat unaware','Very unaware')

# ========================== #
# ===== SET UP LOGGING ===== #
# ========================== #
try:#try to get a previous parameters file
    expInfo = fromFile('lastSartParams.pickle')
    expInfo['session'] +=1 # automatically increment session number
except:#if not there then use a default set
    expInfo = {'subject':'1', 'session':1, 'target digit':3}
dateStr = time.strftime("%b_%d_%H%M", time.localtime())#add the current time

#present a dialogue to change params
dlg = gui.DlgFromDict(expInfo, title='Numerical SART task', fixed=['date'], order=['subject','session','target digit'])
if dlg.OK:
    toFile('lastSartParams.pickle', expInfo)#save params to file for next time
else:
    core.quit()#the user hit cancel so exit

# get volume from dialogue
targetDigit = expInfo['target digit']

#make a log file to save parameter/event  data
fileName = 'Sart-%s-%d-%s'%(expInfo['subject'], expInfo['session'], dateStr) #'Sart-' + expInfo['subject'] + '-' + expInfo['session'] + '-' + dateStr
logging.LogFile((fileName+'.log'), level=logging.INFO)#, mode='w') # w=overwrite
logging.log(level=logging.INFO, msg='---START PARAMETERS---')
logging.log(level=logging.INFO, msg='subject: %s'%expInfo['subject'])
logging.log(level=logging.INFO, msg='session: %s'%expInfo['session'])
logging.log(level=logging.INFO, msg='date: %s'%dateStr)
logging.log(level=logging.INFO, msg='isPractice: %i'%isPractice)
logging.log(level=logging.INFO, msg='nBlocks: %d'%nBlocks)
logging.log(level=logging.INFO, msg='nTrialsPerBlock: %d'%nTrialsPerBlock)
logging.log(level=logging.INFO, msg='fixDur_min: %f'%fixDur_min)
logging.log(level=logging.INFO, msg='fixDur_range: %f'%fixDur_range)
logging.log(level=logging.INFO, msg='digitDur: %f'%digitDur)
logging.log(level=logging.INFO, msg='respDur: %d'%respDur)
logging.log(level=logging.INFO, msg='ITI: %f'%ITI)
logging.log(level=logging.INFO, msg='IBI: %f'%IBI)
logging.log(level=logging.INFO, msg='targetDigit: %s'%targetDigit)
logging.log(level=logging.INFO, msg='targetFrac: %f'%targetFrac)
logging.log(level=logging.INFO, msg='targetProb: %f'%targetProb)
logging.log(level=logging.INFO, msg='respKey: %s'%respKey)
logging.log(level=logging.INFO, msg='wanderKey: %s'%wanderKey)
logging.log(level=logging.INFO, msg='triggerKey: %s'%triggerKey)
logging.log(level=logging.INFO, msg='fullScreen: %s'%fullScreen)
logging.log(level=logging.INFO, msg='fixCrossSize: %s'%fixCrossSize)
logging.log(level=logging.INFO, msg='probeProb: %f'%probeProb)
logging.log(level=logging.INFO, msg='---END PARAMETERS---')

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
fixation = visual.ShapeStim(win,lineColor='#000000',lineWidth=3.0,vertices=((-fixCrossSize/2,0),(fixCrossSize/2,0),(0,0),(0,fixCrossSize/2),(0,-fixCrossSize/2)),units='pix',closeShape=False);
message1 = visual.TextStim(win, pos=[0,+3], color='#000000', alignHoriz='center', name='topMsg', text="aaa")
message2 = visual.TextStim(win, pos=[0,-3], color='#000000', alignHoriz='center', name='bottomMsg', text="bbb")
# make target stim
digit = visual.TextStim(win,pos=[0,0], color='#000000', alignHoriz='center', name='digit', text = str(targetDigit))
nontargets = list(set(range(0,10))-set([targetDigit])) # get all the integers 0-9 that aren't targetDigit.

# declare list of prompts
topPrompts = ["Keep your eyes on the cross at the center of the screen when it appears. You will then see a series of numbers. Using your right index finger, press %c whenever you see a digit that is NOT %d."%(respKey.upper(),targetDigit), 
    "Please respond as quickly as possible without sacrificing accuracy.",
    "If at any time you notice that your mind has been wandering, press the '%c' key with your left index finger."%wanderKey.upper(),
    "Sometimes, a question may appear. When this happens, answer the question using the number keys."]
bottomPrompts = ["Press any key to continue.",
    "Press any key to continue.",
    "Press any key to continue.",
    "WHEN YOU'RE READY TO BEGIN, press any key."]

# ============================ #
# ======= SUBFUNCTIONS ======= #
# ============================ #

def RunTrial(isTarget):
    
    # get trial time
    tTrial = globalClock.getTime()*1000
    # reset clock
    trialClock.reset()
    
    #draw fixation dot
    fixDur = fixDur_min + np.random.random()*fixDur_range
    if fixDur>0:
        fixation.draw()
        win.logOnFlip(level=logging.EXP, msg='Display Fixation')
        win.flip()
        core.wait(fixDur,fixDur)#wait for specified ms (use a loop of x frames for more accurate timing)
    
    # display digit
    if isTarget:
        digit.text = str(targetDigit)
        win.logOnFlip(level=logging.EXP, msg='Display Target')
    else:
        digit.text = str(np.random.choice(nontargets))
        win.logOnFlip(level=logging.EXP, msg='Display NonTarget')
    digit.draw()
    win.flip()
    core.wait(digitDur,digitDur)
    
    #draw fixation dot
    fixation.draw()
    win.logOnFlip(level=logging.EXP, msg='Display Fixation')
    win.flip()
    core.wait(respDur-digitDur, respDur-digitDur) #wait for specified ms (use a loop of x frames for more accurate timing)
    
    #get response
    allKeys = event.getKeys(timeStamped=trialClock)
    return (tTrial,allKeys)


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

# set up performance variables
wasTarget = False # was the last trial a target?
isTarget_alltrials = np.zeros(nBlocks*nTrialsPerBlock)
isCorrect_alltrials = np.zeros(nBlocks*nTrialsPerBlock)
RT_alltrials = np.zeros(nBlocks*nTrialsPerBlock)

logging.log(level=logging.EXP, msg='---START EXPERIMENT---')

for iBlock in range(0,nBlocks): # for each block of trials
    
    # log new block
    logging.log(level=logging.EXP, msg='Start Block %d'%iBlock)
    
    for iTrial in range(0,nTrialsPerBlock): # for each trial
        
        # determine trial type
        if wasTarget:
            isTarget = False # never have two targets in a row
        else:
            isTarget = (np.random.random() < targetProb)
        
        # Run Trial
        [tTrial, allKeys] = RunTrial(isTarget)
        
        
        # check responses
        keyChar = 0
        RT = 0
        for thisKey in allKeys:
            # check for escape keypresses
            if thisKey[0] in ['q', 'escape']:
                core.quit()#abort experiment
            # check for responses
            elif thisKey[0]==respKey:
                keyChar = thisKey[0] #record key
                RT = thisKey[1]*1000 #in ms
        if (RT==0 and isTarget) or (RT!=0 and not isTarget):
            thisResp = 1 # correct
        else:
            thisResp = 0 # incorrect
        event.clearEvents('mouse')#only really needed for pygame windows
        
        # give feedback if this is practice
        if isPractice and thisResp==0:
            message1.setText("Whoops! That was incorrect. Respond by pressing '%c' when you see any digit except %d."%(respKey,targetDigit))
            message2.setText("Press any key to continue.")
            message1.draw()
            message2.draw()
            win.logOnFlip(level=logging.EXP, msg='Display Feedback')
            win.flip()
            core.wait(0.25) # quick pause to make sure they see it
            event.waitKeys()
        
#        print("Trial %d: key pressed = %s, isTarget = %r, correct = %d, RT= %.1f" %(iTrial+1,keyChar,isTarget,thisResp,RT))
        #log the data
        iLog = (iBlock-1)*nTrialsPerBlock + iTrial
        isTarget_alltrials[iLog] = isTarget
        isCorrect_alltrials[iLog] = thisResp
        RT_alltrials[iLog] = RT
        wasTarget = isTarget
        
        # do ITI
        if ITI > 0:
            win.logOnFlip(level=logging.EXP, msg='Display Blank')
            win.flip()
            core.wait(ITI,ITI)
        #===END TRIAL LOOP===#
    
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




#give some performance output to user
print('Performance:')
print('%d/%d = %.2f%% correct' %(np.sum(isCorrect_alltrials), len(isCorrect_alltrials), 100*np.average(isCorrect_alltrials)))
RT_correct = RT_alltrials[np.logical_and(isCorrect_alltrials, np.logical_not(isTarget_alltrials))]
print('RT: std/mean = %f/%f = %.4f' %(np.std(RT_correct),np.average(RT_correct),np.std(RT_correct)/np.average(RT_correct)))
# exit experiment
core.quit()
