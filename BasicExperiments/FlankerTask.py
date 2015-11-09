#!/usr/bin/env python2
"""Implement the Erikson Flanker Task
described in Eichele 2008 (doi: doi: 10.1073/pnas.0708965105)"""
# FlankerTask.py
# Created 1/22/15 by DJ based on NumericalSartTask.py
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
nTrialsPerBlock = 100    # how many trials between breaks?
blockLengths = [100]     # how many trials in each block? The length of this list will be the number of blocks.
randomizeBlocks = True   # scramble the blockLengths list, or perform blocks in order given?
ITI_min = 2.5#4.5           # fixation dot before arrows appear
ITI_range = 1#3.0         # ITI will be between ITI_min and ITI_min + ITI_range (in seconds)
flankerDur = 0.080      # time flanker arrows are onscreen before target (in seconds)
targetDur = 0.030       # time target arrow is onscreen (in seconds)
respDur = 1.4           # max time (after onset of target) to respond (in seconds)
blankDur = 0            # time between response period and fixation dot reappearance (in seconds)
IBI = 5                # time between end of block/probe and beginning of next block (in seconds)
respKeys = ['j', 'k']   # keys to be used for responses
wanderKey = 'z'         # key to be used to indicate mind-wandering
triggerKey = 't'        # key from scanner that says scan is starting
isFullScreen = True     # run in full screen mode?
screenToShow = 0        # display on primary screen (0) or secondary (1)?
fixCrossSize = 10       # size of cross, in pixels
arrowChars = [u"\u2190", u"\u2192"] # unicode for left and right arrows
rtDeadline = 1.000      # responses after this time will be considered too slow (in seconds)
rtTooSlowDur = 0.600    # duration of 'too slow!' message (in seconds)
#isRtThreshUsed = True   # determine response deadline according to a performance threshold?
#rtThreshFraction = 0.80 # recommend deadline (respDur) for next session as level at which this fraction of trials had RTs under the deadline.
nCoherentsAtEnd = 5    # make last few stimuli coherent to allow mind-wandering before probes


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

# enumerate constants
arrowNames = ['Left','Right']

# randomize list of block lengths
if randomizeBlocks:
    np.random.shuffle(blockLengths)

# ========================== #
# ===== SET UP LOGGING ===== #
# ========================== #
try:#try to get a previous parameters file
    expInfo = fromFile('lastFlankerParams.pickle')
    expInfo['session'] +=1 # automatically increment session number
except:#if not there then use a default set
    expInfo = {'subject':'1', 'session':1}
dateStr = time.strftime("%b_%d_%H%M", time.localtime())#add the current time

#present a dialogue to change params
dlg = gui.DlgFromDict(expInfo, title='Flanker task', fixed=['date'], order=['subject','session'])
if dlg.OK:
    toFile('lastFlankerParams.pickle', expInfo)#save params to file for next time
else:
    core.quit()#the user hit cancel so exit

#make a log file to save parameter/event  data
fileName = 'Flanker-%s-%d-%s'%(expInfo['subject'], expInfo['session'], dateStr) #'Sart-' + expInfo['subject'] + '-' + expInfo['session'] + '-' + dateStr
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
logging.log(level=logging.INFO, msg='flankerDur: %f'%flankerDur)
logging.log(level=logging.INFO, msg='targetDur: %f'%targetDur)
logging.log(level=logging.INFO, msg='respDur: %d'%respDur)
logging.log(level=logging.INFO, msg='blankDur: %f'%blankDur)
logging.log(level=logging.INFO, msg='IBI: %f'%IBI)
logging.log(level=logging.INFO, msg='respKeys: %s'%respKeys)
logging.log(level=logging.INFO, msg='wanderKey: %s'%wanderKey)
logging.log(level=logging.INFO, msg='triggerKey: %s'%triggerKey)
logging.log(level=logging.INFO, msg='isFullScreen: %i'%isFullScreen)
logging.log(level=logging.INFO, msg='fixCrossSize: %f'%fixCrossSize)
logging.log(level=logging.INFO, msg='rtDeadline: %f'%rtDeadline)
logging.log(level=logging.INFO, msg='rtTooSlowDur: %f'%rtTooSlowDur)
#logging.log(level=logging.INFO, msg='isRtThreshUsed: %i'%isRtThreshUsed)
#logging.log(level=logging.INFO, msg='rtThreshFraction: %f'%rtThreshFraction)
logging.log(level=logging.INFO, msg='nCoherentsAtEnd: %d'%nCoherentsAtEnd)
logging.log(level=logging.INFO, msg='probeProb: %f'%probeProb)
logging.log(level=logging.INFO, msg='---END PARAMETERS---')

# ========================== #
# ===== SET UP STIMULI ===== #
# ========================== #

# kluge for secondary monitor
if isFullScreen and screenToShow>0: 
    screens = AppKit.NSScreen.screens()
    screenRes = screens[screenToShow].frame().size.width, screens[screenToShow].frame().size.height
#    screenRes = [1920, 1200]
    isFullScreen = False
else:
    screenRes = [800,600]


#create window and stimuli
globalClock = core.Clock()#to keep track of time
trialClock = core.Clock()#to keep track of time
win = visual.Window(screenRes, fullscr=isFullScreen, allowGUI=False, monitor='testMonitor', screen=screenToShow, units='deg', name='win')
#fixation = visual.GratingStim(win, color='black', tex=None, mask='circle',size=0.2)
fixation = visual.ShapeStim(win,lineColor='#000000',lineWidth=3.0,vertices=((-fixCrossSize/2,0),(fixCrossSize/2,0),(0,0),(0,fixCrossSize/2),(0,-fixCrossSize/2)),units='pix',closeShape=False);
message1 = visual.TextStim(win, pos=[0,+3], color='#000000', alignHoriz='center', name='topMsg', text="aaa")
message2 = visual.TextStim(win, pos=[0,-3], color='#000000', alignHoriz='center', name='bottomMsg', text="bbb")
# make target arrow
target = visual.TextStim(win,pos=[0,0], color='#000000', alignHoriz='center', height=2, name='target', text = arrowChars[0])
flankers = []
flankerPos = [-4, -2, 2, 4]
for i in range(0,len(flankerPos)):
    flankers.append(visual.TextStim(win,pos=[0,flankerPos[i]], color='#000000', alignHoriz='center', height=2 , name='flanker%d'%(i+1), text = arrowChars[1]))
# make too-slow message
tooSlowStim = visual.TextStim(win, pos=[0,0], color='red', alignHoriz='center', name='tooSlow', text="Too Slow!")



# declare list of prompts
topPrompts = ["Keep your eyes on the cross at the center of the screen when it appears. You will then see a series of arrows."
    "Using your right hand, press %c whenever the middle arrow points LEFT and %c when it points RIGHT."%(respKeys[0].upper(),respKeys[1].upper()), 
#    "Please respond as quickly as possible without sacrificing accuracy.",
    "If you answer too slowly, you'll see a message reminding you to speed up. Please respond as accurately as possible without being slower than this deadline.",
    "If at any time you notice that your mind has been wandering, press the '%c' key with your left index finger."%wanderKey.upper(),
    "Sometimes, a question may appear. When this happens, answer the question using the number keys."]
bottomPrompts = ["Press any key to continue.",
    "Press any key to continue.",
    "Press any key to continue.",
    "Press any key to continue.",
    "WHEN YOU'RE READY TO BEGIN, press any key."]

# ============================ #
# ======= SUBFUNCTIONS ======= #
# ============================ #

def RunTrial(targetDir,flankerDir,tStartTrial):
    
    # display fixation cross
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
    
    # display flankers
    for flanker in flankers:
        flanker.text = arrowChars[flankerDir]
        flanker.draw()
    win.logOnFlip(level=logging.EXP, msg='Display %sFlankers'%arrowNames[flankerDir])
    win.flip()
    core.wait(flankerDur,flankerDur)
    
    # display flankers AND target arrow
    for flanker in flankers:
        flanker.draw()
    target.text = arrowChars[targetDir]
    target.draw()
    win.logOnFlip(level=logging.EXP, msg='Display %sTarget'%arrowNames[targetDir])
    win.flip()
    tStim = trialClock.getTime() # get time when stim was displayed
    event.clearEvents() # flush buffer
    core.wait(targetDur,targetDur)
    
    #draw blank screen
    win.logOnFlip(level=logging.EXP, msg='Display Blank')
    win.flip()
    core.wait(respDur-targetDur, respDur-targetDur) #wait for specified ms (use a loop of x frames for more accurate timing)
    
    # get responses
    allKeys = event.getKeys(timeStamped=trialClock)
    # find RT
    RT = float('Inf')
    for thisKey in allKeys:
        if thisKey[0] in respKeys:
            RT = thisKey[1]-tStim
            break
                
    if RT >= rtDeadline:
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
isCorrect_alltrials = np.zeros(nBlocks*nTrialsPerBlock, dtype=np.bool)
isCongruent_alltrials = np.zeros(nBlocks*nTrialsPerBlock, dtype=np.bool)
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
        flankerDir = (np.random.random() < 0.5)
        if iTrial>=(nTrialsPerBlock-nCoherentsAtEnd):
            targetDir = flankerDir # make last few stims before probe easy, coherent trials
        else:
            targetDir = (np.random.random() < 0.5)
        
        # Run Trial
        [tTrial, allKeys] = RunTrial(targetDir,flankerDir,tNextTrial)
        
        # determine next trial time
        ITI = ITI_min + np.random.random()*ITI_range
        tNextTrial = tTrial+ITI
        
        # check responses
        keyChar = 0
        RT = np.nan
        for thisKey in allKeys:
            # check for escape keypresses
            if thisKey[0] in ['q', 'escape']:
                core.quit()#abort experiment
            # check for responses
            elif thisKey[0] in respKeys:
                keyChar = thisKey[0] #record key
                RT = thisKey[1]*1000 #in ms
        if keyChar == respKeys[targetDir]:
            thisResp = True # correct
        else:
            thisResp = False # incorrect
        event.clearEvents('mouse')#only really needed for pygame windows
        
        # give feedback if this is practice
        if isPractice and thisResp==0:
            message1.setText("Whoops! That was incorrect. Press %c whenever the middle arrow points LEFT and %c when it points RIGHT."%(respKeys[0].upper(),respKeys[1].upper()))
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
        isCorrect_alltrials[iLog] = thisResp
        RT_alltrials[iLog] = RT
        isCongruent_alltrials[iLog] = (flankerDir == targetDir)
        
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
isC = isCongruent_alltrials!=0
isI = np.logical_not(isCongruent_alltrials)
print('---Performance:')
print('All: %d/%d = %.2f%% correct' %(np.nansum(isCorrect_alltrials), len(isCorrect_alltrials), 100*np.nanmean(isCorrect_alltrials)))
print('Congruent: %d/%d = %.2f%% correct' %(np.nansum(isCorrect_alltrials[isC]), np.nansum(isC), 100*np.nanmean(isCorrect_alltrials[isC])))
print('Incongruent: %d/%d = %.2f%% correct' %(np.nansum(isCorrect_alltrials[isI]), np.nansum(isI), 100*np.nanmean(isCorrect_alltrials[isI])))
print('---Reaction Time:')
print('All: mean = %.4f, std = %.4f' %(np.nanmean(RT_alltrials), np.nanstd(RT_alltrials)))
print('Congruent: mean = %.4f, std = %.4f' %(np.nanmean(RT_alltrials[isC]), np.nanstd(RT_alltrials[isC])))
print('Incongruent: mean = %.4f, std = %.4f' %(np.nanmean(RT_alltrials[isI]), np.nanstd(RT_alltrials[isI])))
# exit experiment
core.quit()
