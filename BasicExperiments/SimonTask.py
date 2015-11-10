#!/usr/bin/env python2
"""Implement a version of SIMON (working memory task) 
described in Morrison 2014 (doi: 10.3389/fnhum.2013.00897)"""
# SimonTask.py
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
skipInstructions = True # go right to the Wait-for-scanner screen
tSessionMax = 600       # max time at which a new block will be allowed to start (in seconds)
nBlocks = 1000          # how many sequences (blocks) will there be?
nTrialsPerBlock = 1000  # max items (trials) in a sequence
ITI_min = 2             # min time between response end and next sequence start (in seconds)
ITI_range = 0           # actual ITI will be between ITI_min and ITI_min + ITI_range seconds.
stimDur = 0.400         # time each item is onscreen (in seconds)
pauseDur = 0.100        # time between items (in seconds)
shortDur = 0.200        # duration of short response beep when the subject presses a button
tRespPerItem = 0.5      # Response deadline will be tRespPerItem * nItemsInSequence (in seconds)
tRespRoundOff = 2       # Round each response deadline up to the next tRespRoundOff (in seconds)... use tRespPerItem for no rounding.
#respDur = 2.0           # max time allowed between response keys (in seconds)
tStartup = 10.0         # time between scanner start and first block (in seconds)
IBI = 16.0              # time between end of block/probe and beginning of next block (in seconds)
IBIRoundOff = 2.0       # increase the IBI so that the time from the last block to this one is a multiple of this.
respKeys = ['r','b','y','g']           # keys to be used for responses (clockwise starting at top) - DIAMOND RESPONSE BOX
wanderKey = 'z'         # key to be used to indicate mind-wandering
triggerKey = 't'        # key from scanner that says scan is starting
breakBetween = False    # Allow a self-timed break between blocks

fullScreen = True       # run in full screen mode?
screenToShow = 0        # display on primary screen (0) or secondary (1)?
fixCrossSize = 10       # size of cross, in pixels
stimColors = ['red','blue','yellow','green'] # color of arrows (clockwise starting at top) - DIAMOND RESPONSE BOX
stimPos = [ [0,2],[2,0],[0,-2],[-2,0]] # (x,y) position of each stimulus (clockwise starting at top)
beepNotes = ['E','A','E','Csh'] # tones to be played along with each stimulus (clockwise starting at top)
beepOctaves = [3,3,4,4]  # octave of the tones played along with each stimulus (clockwise starting at top)
buzzDur = 2             # duration of buzz when subject gets it wrong


# === TRAINING VERSION WITH SHORT PAUSES
#skipInstructions = True
#tSessionMax = 180 # 3 min
#tStartup = 3.0
#IBI = 3.0
#respKeys = ['up','right','down','left']
# === END TRAINING VERSION


# === FAST VERSION FOR PILOTING
#tSessionMax = 30 # 1/2 min
#ITI_min = 0.5
#stimDur = 0.200
#pauseDur = 0.050
#shortDur = 0.100
#tRespPerItem = 0.2
#tRespRoundOff = 1
#tStartup = 1.0
#IBI = 2
#IBIRoundOff = 1
#respKeys = ['up','right','down','left']
# === END FAST VERSION FOR PILOTING

# declare constants
RIGHT = 0
WRONG = 1
TOOSLOW = 2

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
    expInfo = fromFile('lastSimonParams.pickle')
    expInfo['session'] +=1 # automatically increment session number
except:#if not there then use a default set
    expInfo = {'subject':'1', 'session':1}
dateStr = time.strftime("%b_%d_%H%M", time.localtime())#add the current time

#present a dialogue to change params
dlg = gui.DlgFromDict(expInfo, title='Numerical SART task', fixed=['date'], order=['subject','session'])
if dlg.OK:
    toFile('lastSimonParams.pickle', expInfo)#save params to file for next time
else:
    core.quit()#the user hit cancel so exit

#make a log file to save parameter/event  data
fileName = 'Simon-%s-%d-%s'%(expInfo['subject'], expInfo['session'], dateStr) #'Sart-' + expInfo['subject'] + '-' + expInfo['session'] + '-' + dateStr
logging.LogFile((fileName+'.log'), level=logging.INFO)#, mode='w') # w=overwrite
logging.log(level=logging.INFO, msg='---START PARAMETERS---')
logging.log(level=logging.INFO, msg='fileName: %s'%fileName)
logging.log(level=logging.INFO, msg='subject: %s'%expInfo['subject'])
logging.log(level=logging.INFO, msg='session: %s'%expInfo['session'])
logging.log(level=logging.INFO, msg='date: %s'%dateStr)
logging.log(level=logging.INFO, msg='isPractice: %i'%isPractice)
logging.log(level=logging.INFO, msg='skipInstructions: %i'%skipInstructions)
logging.log(level=logging.INFO, msg='tSessionMax: %d'%tSessionMax)
logging.log(level=logging.INFO, msg='nBlocks: %d'%nBlocks)
logging.log(level=logging.INFO, msg='nTrialsPerBlock: %d'%nTrialsPerBlock)
logging.log(level=logging.INFO, msg='ITI_min: %1.3f'%ITI_min)
logging.log(level=logging.INFO, msg='ITI_range: %1.3f'%ITI_range)
logging.log(level=logging.INFO, msg='stimDur: %1.3f'%stimDur)
logging.log(level=logging.INFO, msg='pauseDur: %1.3f'%pauseDur)
logging.log(level=logging.INFO, msg='tRespPerItem: %1.3f'%tRespPerItem)
logging.log(level=logging.INFO, msg='tRespRoundOff: %1.3f'%tRespRoundOff)
logging.log(level=logging.INFO, msg='tStartup: %1.3f'%tStartup)
logging.log(level=logging.INFO, msg='IBI: %1.3f'%IBI)
logging.log(level=logging.INFO, msg='IBIRoundOff: %1.3f'%IBIRoundOff)
logging.log(level=logging.INFO, msg='respKeys: %s'%respKeys)
logging.log(level=logging.INFO, msg='wanderKey: %s'%wanderKey)
logging.log(level=logging.INFO, msg='triggerKey: %s'%triggerKey)
logging.log(level=logging.INFO, msg='fullScreen: %i'%fullScreen)
logging.log(level=logging.INFO, msg='fixCrossSize: %s'%fixCrossSize)
logging.log(level=logging.INFO, msg='stimColors: %s'%stimColors)
logging.log(level=logging.INFO, msg='beepNotes: %s'%beepNotes)
logging.log(level=logging.INFO, msg='beepOctaves: %s'%beepOctaves)
logging.log(level=logging.INFO, msg='probeProb: %1.3f'%probeProb)
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

# Initialize deadline for displaying next frame
tNextFlip = [0.0] # put in a list to make it mutable? 

#create window and stimuli
globalClock = core.Clock()#to keep track of time
trialClock = core.Clock()#to keep track of time
win = visual.Window(screenRes, fullscr=fullScreen, allowGUI=False, monitor='testMonitor', screen=screenToShow, units='deg', name='win')
#fixation = visual.GratingStim(win, color='black', tex=None, mask='circle',size=0.2)
fixation = visual.ShapeStim(win,lineColor='#000000',lineWidth=3.0,vertices=((-fixCrossSize/2,0),(fixCrossSize/2,0),(0,0),(0,fixCrossSize/2),(0,-fixCrossSize/2)),units='pix',closeShape=False);
message1 = visual.TextStim(win, pos=[0,+3], color='#000000', alignHoriz='center', name='topMsg', text="aaa")
message2 = visual.TextStim(win, pos=[0,-3], color='#000000', alignHoriz='center', name='bottomMsg', text="bbb")
# make target stims
stimOn = []
stimOff = []
beeps = []
beepsShort = []
for i in range(0,len(stimColors)):
    stimOn.append(visual.Polygon(win, edges=3, radius=1, pos=stimPos[i], fillColor=stimColors[i], ori=90*i, name='stimOn%d'%(i+1)));
    stimOff.append(visual.Polygon(win, edges=3, radius=1, pos=stimPos[i], fillColor=stimColors[i],contrast=0.2, ori=90*i, name='stimOff%d'%(i+1)));
    beeps.append(sound.Sound(value=beepNotes[i], octave=beepOctaves[i], secs=stimDur, name='beep%d'%(i+1)))
    beepsShort.append(sound.Sound(value=beepNotes[i], octave=beepOctaves[i], secs=shortDur, name='beepShort%d'%(i+1)))
buzz = sound.Sound(value='Fsh', octave=3 , secs=buzzDur, name='buzz')

# declare list of prompts
topPrompts = ["You will hear a series of beeps and see the corresponding arrows light up. When the fixation cross appears, repeat the sequence using the response pad.", 
    "Please respond as quickly as possible without sacrificing accuracy. You can take up to %1.1f seconds for every %d keys in the sequence."%(tRespRoundOff,np.round(tRespRoundOff/tRespPerItem)),
#    "Please respond as quickly as possible without sacrificing accuracy. You can take up to %1.1f seconds to press each key in the sequence."%tResp,
    #"If at any time you notice that your mind has been wandering, press the '%c' key with your left index finger."%wanderKey.upper(),
    #"Sometimes, a question may appear. When this happens, answer the question using the number keys.",
    "Try to stay as still as you can during the scan. The experiment will end automatically. Good luck!"]
bottomPrompts = ["Press any key to continue.",
    "Press any key to continue.",
    #"Press any key to continue.",
    #"Press any key to continue.",
    "WHEN YOU'RE READY TO BEGIN, press any key."]


# ============================ #
# ======= SUBFUNCTIONS ======= #
# ============================ #

# increment time of next window flip
def AddToFlipTime(tIncrement=1.0):
    #tLastFlip = tNextFlip
    tNextFlip[0] += tIncrement
#    print("%1.3f --> %1.3f"%(globalClock.getTime(),tNextFlip[0]))

def DisplayButtons(iOn,tIncrement=1.0,isFixOn=False):
    if isFixOn:
        msgText = 'Display Fix+Stim%s'%str(iOn)
    else:
        msgText = 'Display Stim%s'%str(iOn)
    # wait for the right time before drawing new frame!
    while (globalClock.getTime()<tNextFlip[0]):
        win.flip(clearBuffer=False)
    # draw fix cross
    win.clearBuffer()
    if isFixOn:
        fixation.draw()
    # draw arrows
    for iDraw in range(0,len(stimColors)):
        if iDraw in iOn:
            stimOn[iDraw].draw()
        else:
            stimOff[iDraw].draw()
    # set up flip
    win.logOnFlip(level=logging.EXP, msg=msgText)
    win.callOnFlip(AddToFlipTime,tIncrement);
    win.flip(clearBuffer=False)
    return

def RunTrial(sequence):
    
    # check for going over session time
    if globalClock.getTime()-tStartSession > tSessionMax:
        CoolDown() #exit experiment gracefully
    
    # get deadline for response
    respDur = tRespPerItem*(len(sequence))
    respDur = int(tRespRoundOff * np.ceil(float(respDur)/tRespRoundOff)) # round up to next tRespRoundOff multiple
#    print("length = %d, respDur = %1.1f"%(len(sequence), respDur))
    logging.log(level=logging.EXP, msg='Start Sequence %d'%len(sequence))
    # play sequence
    for iStim in sequence:
        DisplayButtons([iStim],stimDur)
        beeps[iStim].play()
        core.wait(stimDur,stimDur) # wait so sound plays properly
        DisplayButtons([],pauseDur)
#        core.wait(pauseDur,pauseDur)
    
    logging.log(level=logging.EXP, msg='End Sequence %d'%len(sequence))
    #draw fixation dot and wait for response
    event.clearEvents() # ignore any keypresses before now
#    win.logOnFlip(level=logging.EXP, msg='Display Fixation')
#    fixation.draw()
    DisplayButtons([],0,True)
#    tResp = trialClock.getTime() # IMPORTANT REFERENCE POINT
    tResp = tNextFlip[0] # IMPORTANT REFERENCE POINT
    iSeq = 0
    # Response loop
    while globalClock.getTime() < (tResp + respDur) and iSeq < len(sequence):
        iStim = sequence[iSeq]
        thisKey = event.getKeys(timeStamped=globalClock)
        if len(thisKey)>0 and thisKey[0][0] == respKeys[iStim]:
            #tResp = trialClock.getTime(); # reset the shot clock
#            fixation.draw()
            DisplayButtons([iStim],0,True) # DON'T INCREMENT CLOCK
            beepsShort[iStim].play()
            core.wait(shortDur,shortDur) # USE CORE.WAIT HERE SO CLOCK DOESN'T INCREMENT
#            fixation.draw()
            DisplayButtons([],0,True)
            iSeq += 1
        elif len(thisKey)>0 and thisKey[0][0] in ['q','escape']:
            core.quit()
        elif len(thisKey)>0:
            print('this: %s'%str(thisKey[0][0]))
            print('correct: %s'%str(respKeys[iStim]))
            buzz.play()
            core.wait(buzzDur,buzzDur) # USE CORE.WAIT HERE SO CLOCK DOESN'T INCREMENT
            return (WRONG)
            
    #get response
    if iSeq == len(sequence): # finished sequence
        DisplayButtons([],respDur,False) # increment next-frame clock
        return(RIGHT)
    else: # ran out of time
        buzz.play()
        core.wait(buzzDur,buzzDur) # USE CORE.WAIT HERE SO CLOCK DOESN'T INCREMENT
        DisplayButtons([],respDur,False) # increment next-frame clock
        return (TOOSLOW)

# exit experiment gracefully
def CoolDown():
    # display cool-down message
    win.clearBuffer()
    message1.setText("That's the end! Please stay still until the scan is complete.")
    message2.setText("(Press 'q' or 'escape' to override.)")
    win.logOnFlip(level=logging.EXP, msg='Display TheEnd')
    message1.draw()
#    message2.draw()
    win.flip()
    thisKey = event.waitKeys(['q','escape'])
    # exit experiment
    core.quit()

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
if not skipInstructions:
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
#message2.draw()
win.logOnFlip(level=logging.EXP, msg='Display WaitingForScanner')
win.flip()
event.waitKeys(keyList=triggerKey)
tStartSession = globalClock.getTime()
AddToFlipTime(tStartSession+tStartup)

# do brief wait before first stimulus
win.clearBuffer() # just in case
fixation.draw()
win.logOnFlip(level=logging.EXP, msg='Display Fixation')
win.flip()
#core.wait(tStartup,tStartup)


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
    tThisBlock = tNextFlip[0] # when will this block start?
    sequence = []
    for iTrial in range(0,nTrialsPerBlock): # for each trial
        
        sequence.append(np.random.choice(range(0,len(stimColors))))
        
        # Run Trial
        exitCode = RunTrial(sequence)
        
        # give feedback if this is practice
        if isPractice and exitCode != RIGHT: 
            if exitCode==WRONG:
                message1.setText("Whoops! That was incorrect. Respond by pressing the arrow keys corresponding to the sequence you just heard.")
            else:
                message1.setText("Whoops! Too slow. You have %1.1f seconds to press the next key in the sequence."%respDur)
            message2.setText("Press any key to continue.")
            message1.draw()
            message2.draw()
            win.logOnFlip(level=logging.EXP, msg='Display Feedback')
            win.flip()
            core.wait(0.25) # quick pause to make sure they see it
            event.waitKeys()
            break
        elif exitCode != RIGHT:
            break
        
        # do ITI
        ITI = ITI_min + np.random.random()*ITI_range
        if ITI > 0:
#            win.logOnFlip(level=logging.EXP, msg='Display Blank')
#            win.flip()
            AddToFlipTime(ITI) # increment flip time without changing display
#            core.wait(ITI,ITI)
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
     
    # Check for session end time
    print("Block end time = %1.1f"%(globalClock.getTime() - tStartSession))
    if ((globalClock.getTime() - tStartSession) > tSessionMax):
        break
    
    # skip IBI on last block
    if iBlock < (nBlocks-1):
        if breakBetween:
            # Display wait screen
            message1.setText("Take a break! When you're ready to begin a new block, press any key.")
            message1.draw()
            win.logOnFlip(level=logging.EXP, msg='Display BreakTime')
            win.flip()
            thisKey = event.waitKeys()
            if thisKey[0] in ['q', 'escape']:
                core.quit() #abort experiment
            # do IBI (blank screen)
        win.clearBuffer()
        win.logOnFlip(level=logging.EXP, msg='Display Blank')
        totalBlockTime = tNextFlip[0]+IBI-tThisBlock # anticipated time of next block minus time of this one
        IBIPatch = IBIRoundOff - (totalBlockTime % IBIRoundOff) # add a bit so we round up to a multiple of IBIRoundOff
        print("IBIPatch = %.3f"%IBIPatch)
        win.callOnFlip(AddToFlipTime,IBI+IBIPatch)
        win.flip()
        print("old: %.3f, new: %.3f, now: %.3f"%(tThisBlock,tNextFlip[0],globalClock.getTime()))
#        core.wait(IBI,IBI)
        

# display cool-down message and wait for keypress to quit
CoolDown()


