#!/usr/bin/env python2
"""Implement an audio version of the SART (sustained attention response task) 
described in Morrison 2014 (doi: 10.3389/fnhum.2013.00897)"""
# AuditorySartTask.py
# Created 12/16/14 by DJ based on ThresholdToneDetection.py
# Updated 1/5/15 by DJ - added logging, key options, cleaned up
# Updated 11/9/15 by DJ - cleanup

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
nTrialsPerBlock = 100   # how many trials between breaks?
blockLengths = [100]     # how many trials in each block? The length of this list will be the number of blocks.
randomizeBlocks = True   # scramble the blockLengths list, or perform blocks in order given?
ITI_min = 2.5#4.5           # fixation dot before arrows appear
ITI_range = 1#3.0         # ITI will be between ITI_min and ITI_min + ITI_range (in seconds)
respDur = 1.0           # max time (after onset of letter) to respond (in seconds)
blankDur = 0            # time between response period and fixation dot reappearance (in seconds)
IBI = 5                 # time between end of block/probe and beginning of next block (in seconds)
targetLetter = 'c'      # the only digit to elicit no response
respKey = 'j'           # key to be used for responses
wanderKey = 'z'         # key to be used to indicate mind-wandering
triggerKey = 't'        # key from scanner that says scan is starting
targetFrac = 0.10       # fraction of trials that should be targets
targetProb = 1/(1/targetFrac - 1)  # probability of target on a trial that doesn't follow a target
                                   # (since targets are always followed by non-targets)
fullScreen = True      # run in full screen mode?
screenToShow = 0    # display on primary screen (0) or secondary (1)?
fixCrossSize = 10       # size of cross, in pixels
letterVolume = 0.5
rtDeadline = 1.000      # responses after this time will be considered too slow (in seconds)
rtTooSlowDur = 0.600    # duration of 'too slow!' message (in seconds)
#isRtThreshUsed = True   # determine response deadline according to a performance threshold?
#rtThreshFraction = 0.80 # recommend deadline (respDur) for next session as level at which this fraction of trials had RTs under the deadline.
nNontargetsAtEnd = 5    # make last few stimuli nontargets to allow mind-wandering before probes

# declare probe parameters
probeProb = 1 # probablilty that a given block will be followed by a probe
probe_strings = []
probe_options = []
probe_strings.append('Just now, what were you thinking about?')
probe_options.append(['What I had to do in the task just now (like getting the current trial right)',
    'Something else happening just now (like the scanner sounds)',
    'Something else about the task (like how well I was doing)',
    'Something else entirely (like what you had for breakfast)',
    'I was asleep.'])
#probe_strings.append('Where was your attention focused just before this?')
#probe_options.append(['Completely on the task','Mostly on the task','Not sure','Mostly on inward thoughts','Completely on inward thoughts'])
#probe_strings.append('How aware were you of where your attention was?')
#probe_options.append(['Very aware','Somewhat aware','Neutral','Somewhat unaware','Very unaware'])


# get list of possible non-target letters
#nontargets = list(set(['a','b','c','d','e','f','g','h','i','j'])-set(targetLetter)) # get all the letters a-j that aren't targetLetter.
nontargets = list(set(['b','c','d','e','f','g','j','k','l','m'])-set(targetLetter)) # a, h, and i are said kind of strangely by the bot.

# randomize list of block lengths
if randomizeBlocks:
    np.random.shuffle(blockLengths)


# ========================== #
# ===== SET UP LOGGING ===== #
# ========================== #
try:#try to get a previous parameters file
    expInfo = fromFile('lastAudSartParams.pickle')
    expInfo['session'] +=1 # automatically increment session number
except:#if not there then use a default set
    expInfo = {'subject':'1', 'session':1, 'target letter':targetLetter}
dateStr = time.strftime("%b_%d_%H%M", time.localtime())#add the current time

#present a dialogue to change params
dlg = gui.DlgFromDict(expInfo, title='Numerical SART task', fixed=['date'], order=['subject','session','target letter'])
if dlg.OK:
    toFile('lastAudSartParams.pickle', expInfo)#save params to file for next time
else:
    core.quit()#the user hit cancel so exit

# get volume from dialogue
targetLetter = expInfo['target letter']

#make a log file to save parameter/event  data
fileName = 'AudSart-%s-%d-%s'%(expInfo['subject'], expInfo['session'], dateStr) #'Sart-' + expInfo['subject'] + '-' + expInfo['session'] + '-' + dateStr
logging.LogFile((fileName+'.log'), level=logging.INFO)#, mode='w') # w=overwrite
logging.log(level=logging.INFO, msg='---START PARAMETERS---')
logging.log(level=logging.INFO, msg='subject: %s'%expInfo['subject'])
logging.log(level=logging.INFO, msg='session: %s'%expInfo['session'])
logging.log(level=logging.INFO, msg='date: %s'%dateStr)
logging.log(level=logging.INFO, msg='isPractice: %i'%isPractice)
logging.log(level=logging.INFO, msg='blockLengths: %s'%blockLengths)
logging.log(level=logging.INFO, msg='randomizeBlocks: %d'%randomizeBlocks)
logging.log(level=logging.INFO, msg='ITI_min: %f'%ITI_min)
logging.log(level=logging.INFO, msg='ITI_range: %f'%ITI_range)
logging.log(level=logging.INFO, msg='respDur: %d'%respDur)
logging.log(level=logging.INFO, msg='blankDur: %f'%blankDur)
logging.log(level=logging.INFO, msg='IBI: %f'%IBI)
logging.log(level=logging.INFO, msg='targetLetter: %s'%targetLetter)
logging.log(level=logging.INFO, msg='nontargets: %s'%nontargets)
logging.log(level=logging.INFO, msg='targetFrac: %f'%targetFrac)
logging.log(level=logging.INFO, msg='targetProb: %f'%targetProb)
logging.log(level=logging.INFO, msg='letterVolume: %f'%letterVolume)
logging.log(level=logging.INFO, msg='respKey: %s'%respKey)
logging.log(level=logging.INFO, msg='wanderKey: %s'%wanderKey)
logging.log(level=logging.INFO, msg='triggerKey: %s'%triggerKey)
logging.log(level=logging.INFO, msg='fullScreen: %s'%fullScreen)
logging.log(level=logging.INFO, msg='fixCrossSize: %s'%fixCrossSize)
logging.log(level=logging.INFO, msg='rtDeadline: %f'%rtDeadline)
logging.log(level=logging.INFO, msg='rtTooSlowDur: %f'%rtTooSlowDur)
#logging.log(level=logging.INFO, msg='isRtThreshUsed: %i'%isRtThreshUsed)
#logging.log(level=logging.INFO, msg='rtThreshFraction: %f'%rtThreshFraction)
logging.log(level=logging.INFO, msg='nNontargetsAtEnd: %d'%nNontargetsAtEnd)
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
# initialize letter sound
letterSound = sound.Sound() # initialize to blank
# make too-slow message
tooSlowStim = visual.TextStim(win, pos=[0,0], color='red', alignHoriz='center', name='tooSlow', text="Too Slow!")

# declare list of prompts
topPrompts = ["Keep your eyes on the cross at the center of the screen when it appears. You will then hear a series of letters. Using your right index finger, press %c whenever you hear a letter that is NOT %c."%(respKey.upper(),targetLetter.upper()), 
#    "Please respond as quickly as possible without sacrificing accuracy.",
    "If you answer too slowly, you'll see a message reminding you to speed up. Please respond as accurately as possible without being slower than this deadline.",
    "If at any time you notice that your mind has been wandering, press the '%c' key with your left index finger."%wanderKey.upper(),
    "Sometimes, a question may appear. When this happens, answer the question using the number keys."]
bottomPrompts = ["Press any key to continue.",
    "Press any key to continue.",
    "Press any key to continue.",
    "WHEN YOU'RE READY TO BEGIN, press any key."]

# ============================ #
# ======= SUBFUNCTIONS ======= #
# ============================ #

def RunTrial(isTarget,tStartTrial):
    
    # draw fixation dot
    fixation.draw()
    win.logOnFlip(level=logging.EXP, msg='Display Fixation')
    win.flip()
    
    # wait until it's time to start the new trial
    while globalClock.getTime()<tStartTrial:
        pass # do nothing
    
    # get trial time
    tTrial = globalClock.getTime()
    # reset clock
    trialClock.reset()
    
    # make sound
    if isTarget:
        letterSound = sound.Sound(value='Letters/say%c.wav'%targetLetter.upper(), volume=letterVolume, name='letter%c'%targetLetter.upper())
    else:
        nontargetLetter = np.random.choice(nontargets)
        letterSound = sound.Sound(value='Letters/say%c.wav'%nontargetLetter.upper(), volume=letterVolume, name='letter%c'%nontargetLetter.upper())
    letterSound.play()
    tStim = trialClock.getTime() # get time when stim was displayed
    event.clearEvents() # flush buffer
    
    #wait for responses to come in
    core.wait(respDur, respDur) #wait for specified ms (use a loop of x frames for more accurate timing)
    
    # get responses
    allKeys = event.getKeys(timeStamped=trialClock)
    # find RT
    RT = float('Inf')
    for thisKey in allKeys:
        if thisKey[0] == respKey:
            RT = thisKey[1]-tStim
            break
                
    if (not np.isinf(RT)) and (RT >= rtDeadline):
        tooSlowStim.draw()
        win.logOnFlip(level=logging.EXP, msg='Display TooSlow')
        win.flip()
        core.wait(rtTooSlowDur,rtTooSlowDur)
    
    
    # return trial time, response(s)
    return (tTrial,allKeys)


def RunProbes():
    
    # initialize response list
    allKeys = []
    # set up stimuli
    for iProbe in range(0,len(probe_strings)):
        respText = ""
        for iResp in range(0,len(probe_options[iProbe])):
            respText.append('%d) %s\n'%(iResp+1),probe_options[iProbe][iResp])
        message1.setText(probe_strings[iProbe])
        message2.setText(respText)
        message1.draw()
        message2.draw()
        win.logOnFlip(level=logging.EXP, msg='Display Probe%d'%(iProbe+1))
        win.flip()
        # reset clock
        trialClock.reset()
        # get response
        newKey = event.waitKeys(keyList=['1','2','3','4','5','q','escape'],timeStamped=trialClock)
        allKeys.append(newKey)
    
    # return results
    return (allKeys)
    

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
fixation.draw()
win.logOnFlip(level=logging.EXP, msg='Display Fixation')
win.flip()
core.wait(IBI, IBI)


# =========================== #
# ===== MAIN EXPERIMENT ===== #
# =========================== #


# set up performance variables
wasTarget = False # was the last trial a target?
isTarget_alltrials = np.zeros(nBlocks*nTrialsPerBlock)
isCorrect_alltrials = np.zeros(nBlocks*nTrialsPerBlock)
RT_alltrials = np.zeros(nBlocks*nTrialsPerBlock)

# set up other stuff
tNextTrial = 0 # to make first trial start immediately
logging.log(level=logging.EXP, msg='---START EXPERIMENT---')

for iBlock in range(0,nBlocks): # for each block of trials
    
    # log new block
    logging.log(level=logging.EXP, msg='Start Block %d'%iBlock)
    nTrialsPerBlock = blockLengths[iBlock]
    
    for iTrial in range(0,nTrialsPerBlock): # for each trial
        
        # determine trial type
        if wasTarget or iTrial>=(nTrialsPerBlock-nNontargetsAtEnd):
            isTarget = False # never have two targets in a row, and keep last few stims before probe as non-targets
        else:
            isTarget = (np.random.random() < targetProb)
        
        # Run Trial
        [tTrial, allKeys] = RunTrial(isTarget,tNextTrial)
        
        # determine next trial time
        ITI = ITI_min + np.random.random()*ITI_range
        tNextTrial = tTrial+ITI
        
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
            message1.setText("Whoops! That was incorrect. Respond by pressing '%c' when you hear any letter except %c."%(respKey.upper(),targetLetter.upper()))
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
        if blankDur > 0:
            win.logOnFlip(level=logging.EXP, msg='Display Blank')
            win.flip()
            core.wait(blankDur,blankDur)
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
