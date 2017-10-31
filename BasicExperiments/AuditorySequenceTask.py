#!/usr/bin/env python2
"""Display colored crosses to alert the subject of what they're supposed to do.
Play audio sequences for the experimenter to know what tactile stimulus sequence to give the subject."""

# AuditorySequenceTask.py
#
# Created 4/18/17 by DJ based on SingingTask_click.py.

from psychopy import core, gui, data, event, sound, logging #, visual # visual causes a bug in the guis, so I moved it down.
from psychopy.tools.filetools import fromFile, toFile
import random
import time, numpy as np
import AppKit, os # for monitor size detection, files
import PromptTools


# ====================== #
# ===== PARAMETERS ===== #
# ====================== #
# Save the parameters declared below?
saveParams = True;
newParamsFilename = 'AuditorySequenceTaskParams.pickle'

# Declare primary task parameters.
params = {
    'skipPrompts': False,    # at the beginning
    'tStartup': 0.0,       # time after beginning of scan before starting first pre-trial message
    'beatTime': 0.75,       # duration of beat (in sec)
    'sequences':[[4,3,2,1],[4,3,2,2],[1,4,2,3],[1,4,2,4]], # each [] is a sequence of numbers (1-4) indicating which sounds should be played. They should be in groups of 2 (if sequence[2] is played first, sequence[2] or [3] will be played next).
    'chanceOfRepeat': 0.5,   # odds of having the same sequence
    'trialTime': 3.0,       # duration of sequence (in sec)
    'delayTime': 6.0,        # duration of mid-trial delay (in sec)
    'respTime': 3.0,        # duration of post-trial response (in sec)
    'minITI': 6.0,          # minimum time between end of response period and beginning of next trial (in seconds)
    'maxITI': 9.0,          # maximum time between end of response period and beginning of next trial (in seconds)
    'nTrials': 3,           # number of trials in this run
    'randomizeOrder': True, # randomize order of trials in this run
    'respKeys': ['1','2'],  # keys corresponding to 'same' and 'different'
    'triggerKey': 't',      # key from scanner that says scan is starting
    'promptType': 'Default',# must correspond to keyword in PromptTools.py
    # declare click params
    'previewSound': 'numbers/next.wav',
    'goSound': 'numbers/go.wav',
    'sequenceSounds': ['numbers/one.wav','numbers/two.wav','numbers/three.wav','numbers/four.wav'],
    'soundVolume': 1,
# declare other stimulus parameters
    'fullScreen': True,       # run in full screen mode?
    'screenToShow': 0,        # display on primary screen (0) or secondary (1)?
    'fixCrossSize': 50,       # size of cross, in pixels
    'fixCrossPos': (0,0), # (x,y) pos of fixation cross displayed before each page (for drift correction)
    'usePhotodiode': False     # add sync square in corner of screen
    #'textBoxSize': [800,600] # [640,360]# [700, 500]   # width, height of text box (in pixels)
}

# save parameters
if saveParams:
    dlgResult = gui.fileSaveDlg(prompt='Save Params...',initFilePath = os.getcwd() + '/Params', initFileName = newParamsFilename,
        allowed="PICKLE files (.pickle)|.pickle|All files (.*)|")
    newParamsFilename = dlgResult
    if newParamsFilename is None: # keep going, but don't save
        saveParams = False
    else:
        toFile(newParamsFilename, params)# save it!


# ========================== #
# ===== SET UP LOGGING ===== #
# ========================== #
try:#try to get a previous parameters file
    expInfo = fromFile('lastSingInfo.pickle')
    expInfo['session'] +=1 # automatically increment session number
    expInfo['paramsFile'] = [expInfo['paramsFile'],'Load...']
except:#if not there then use a default set
    expInfo = {'subject':'1', 'session':1, 'paramsFile':['DEFAULT','Load...']}
# overwrite if you just saved a new parameter set
if saveParams:
    expInfo['paramsFile'] = [newParamsFilename,'Load...']
dateStr = time.strftime("%b_%d_%H%M", time.localtime()) # add the current time

#present a dialogue to change params
dlg = gui.DlgFromDict(expInfo, title='Auditory Sequence task', order=['subject','session','paramsFile'])
if not dlg.OK:
    core.quit()#the user hit cancel so exit

# find parameter file
if expInfo['paramsFile'] == 'Load...':
    dlgResult = gui.fileOpenDlg(prompt='Select parameters file',tryFilePath=os.getcwd(),
        allowed="PICKLE files (.pickle)|.pickle|All files (.*)|")
    expInfo['paramsFile'] = dlgResult[0]
# load parameter file
if expInfo['paramsFile'] not in ['DEFAULT', None]: # otherwise, just use defaults.
    # load params file
    params = fromFile(expInfo['paramsFile'])

# print params to Output
print 'params = {'
for key in sorted(params.keys()):
    print "   '%s': %s"%(key,params[key]) # print each value as-is (no quotes)
print '}'
    
# save experimental info
toFile('lastAudSeqInfo.pickle', expInfo)#save params to file for next time

#make a log file to save parameter/event  data
filename = 'Sequence-%s-%d-%s'%(expInfo['subject'], expInfo['session'], dateStr) #'Sart-' + expInfo['subject'] + '-' + expInfo['session'] + '-' + dateStr
logging.LogFile((filename+'.log'), level=logging.INFO)#, mode='w') # w=overwrite
logging.log(level=logging.INFO, msg='---START PARAMETERS---')
logging.log(level=logging.INFO, msg='filename: %s'%filename)
logging.log(level=logging.INFO, msg='subject: %s'%expInfo['subject'])
logging.log(level=logging.INFO, msg='session: %s'%expInfo['session'])
logging.log(level=logging.INFO, msg='date: %s'%dateStr)
for key in sorted(params.keys()): # in alphabetical order
    logging.log(level=logging.INFO, msg='%s: %s'%(key,params[key]))

logging.log(level=logging.INFO, msg='---END PARAMETERS---')

# ========================== #
# ===== SET UP STIMULI ===== #
# ========================== #
from psychopy import visual

# kluge for secondary monitor
if params['fullScreen'] and params['screenToShow']>0: 
    screens = AppKit.NSScreen.screens()
    screenRes = screens[params['screenToShow']].frame().size.width, screens[params['screenToShow']].frame().size.height
#    screenRes = [1920, 1200]
    params['fullScreen'] = False
else:
    screenRes = [800,600]

# Initialize deadline for displaying next frame
tNextFlip = [0.0] # put in a list to make it mutable? 

#create window and stimuli
globalClock = core.Clock()#to keep track of time
trialClock = core.Clock()#to keep track of time
win = visual.Window(screenRes, fullscr=params['fullScreen'], allowGUI=False, monitor='testMonitor', screen=params['screenToShow'], units='deg', name='win')
#fixation = visual.GratingStim(win, color='black', tex=None, mask='circle',size=0.2)
fCS = params['fixCrossSize'] # rename for brevity
fcX = params['fixCrossPos'][0] # rename for brevity
fcY = params['fixCrossPos'][1] # rename for brevity
fCS_vertices = ((-fCS/2 + fcX, fcY),(fCS/2 + fcX, fcY),(fcX, fcY),(fcX, fCS/2 + fcY),(fcX, -fCS/2 + fcY))
# make different-colored fixation crosses
fixation = visual.ShapeStim(win,lineColor='#000000',lineWidth=3.0,vertices=fCS_vertices,units='pix',closeShape=False);
fixRed = visual.ShapeStim(win,lineColor='#000000',lineWidth=3.0,vertices=fCS_vertices,units='pix',closeShape=False);
fixRed.lineColor = 'red'
fixBlue = visual.ShapeStim(win,lineColor='#000000',lineWidth=3.0,vertices=fCS_vertices,units='pix',closeShape=False);
fixBlue.lineColor = 'blue'
fixGreen = visual.ShapeStim(win,lineColor='#000000',lineWidth=3.0,vertices=fCS_vertices,units='pix',closeShape=False);
fixGreen.lineColor = 'green'
fixYellow = visual.ShapeStim(win,lineColor='#000000',lineWidth=3.0,vertices=fCS_vertices,units='pix',closeShape=False);
fixYellow.lineColor = 'yellow'
# make text messages
message1 = visual.TextStim(win, pos=[0, 0], wrapWidth=50, color='#000000', alignHoriz='center', name='topMsg', text="aaa", height=3)
message2 = visual.TextStim(win, pos=[0,-10], wrapWidth=50, color='#000000', alignHoriz='center', name='bottomMsg', text="bbb", height=3)
# initialize photodiode stimulus
squareSize = 0.4
diodeSquare = visual.Rect(win,pos=[squareSize/4-1,squareSize/4-1],lineColor='white',fillColor='white',size=[squareSize,squareSize],units='norm')

# Look up prompts
[topPrompts,bottomPrompts] = PromptTools.GetPrompts(os.path.basename(__file__),params['promptType'],params)
print('%d prompts loaded from %s'%(len(topPrompts),'PromptTools.py'))

# Declare sounds
previewSound = sound.Sound(value=params['previewSound'], name='previewSound')
previewSound.setVolume(params['soundVolume'])
goSound = sound.Sound(value=params['goSound'], name='goSound')
goSound.setVolume(params['soundVolume'])
sequenceSound = [None]*len(params['sequenceSounds'])
for i in range(0,len(params['sequenceSounds'])):
#    print params['sequenceSounds'][i]
    sequenceSound[i] = sound.Sound(value=params['sequenceSounds'][i], name='sound%d'%(i+1))
    sequenceSound[i].setVolume(params['soundVolume'])


# ============================ #
# ======= SUBFUNCTIONS ======= #
# ============================ #

# increment time of next window flip
def AddToFlipTime(tIncrement=1.0):
    tNextFlip[0] += tIncrement
#    print("%1.3f --> %1.3f"%(globalClock.getTime(),tNextFlip[0]))

def RunTrial(beatTime,trialTime,delayTime,respTime,ITI,sequence1,sequence2):
    
    # adjust pre-trial time
    nTrialBeats = len(sequence1)
    nPreTrialBeats = nTrialBeats + 2 # +2 to include 'next' and 'go' sounds
    timeToFirstSound = ITI - beatTime*nPreTrialBeats
    
    # flush response buffer
    event.clearEvents()
    
    # ===ITI=== #
    # Display pre-trial cross
    win.clearBuffer()
    fixation.draw()
    win.logOnFlip(level=logging.EXP, msg='Display Fixation')
    # wait until it's time
    while (globalClock.getTime()<tNextFlip[0]):
        core.wait(0.0001)
#        pass
    # flip display
    win.flip()
    AddToFlipTime(timeToFirstSound)
    
    # do pre-trial beats
    for iBeat in range(0, nPreTrialBeats):
        # determine which sound to play
        if iBeat==0:
            thisSound = previewSound
        elif iBeat==(nPreTrialBeats-1):
            thisSound = goSound
        else:
            thisSound = sequenceSound[sequence1[iBeat-1]-1]
        # wait until it's time
        while (globalClock.getTime()<tNextFlip[0]):
            core.wait(0.0001)
#            pass
        # play sound
        thisSound.play()
        # add to flip time
        AddToFlipTime(beatTime)
        # check for escape characters
        thisKey = event.getKeys()
        if thisKey!=None and len(thisKey)>0 and thisKey[0] in ['q','escape']:
            core.quit()
    
    # ===SEQUENCE=== #
    # Draw sequence cross
    fixGreen.draw()
    win.logOnFlip(level=logging.EXP, msg='Display fixGreen')
    
    # do trial beats
    for iBeat in range(0, nTrialBeats):
        # prepare next sound
        thisSound = sequenceSound[sequence1[iBeat]-1]
        # wait until it's time
        while (globalClock.getTime()<tNextFlip[0]):
            core.wait(0.0001)
#            pass
        # On first beat, flip display
        if iBeat==0:
            win.flip()
        # play sound
        thisSound.play()
        # add to flip time
        AddToFlipTime(beatTime)
        
        # check for escape characters
        thisKey = event.getKeys()
        if thisKey!=None and len(thisKey)>0 and thisKey[0] in ['q','escape']:
            core.quit()
    
    # ===DELAY=== #
    # calculate time to next sound
    timeToNextSound = delayTime - beatTime*nPreTrialBeats
    # Draw Delay cross
    fixBlue.draw()
    win.logOnFlip(level=logging.EXP, msg='Display fixBlue')
    # wait until it's time
    while (globalClock.getTime()<tNextFlip[0]):
        core.wait(0.0001)
#        pass
    # flip display
    win.flip()
    AddToFlipTime(timeToNextSound)
    
    # do pre-repeat beats
    for iBeat in range(0, nPreTrialBeats):
        # determine which sound to play
        if iBeat==0:
            thisSound = previewSound
        elif iBeat==(nPreTrialBeats-1):
            thisSound = goSound
        else:
            thisSound = sequenceSound[sequence2[iBeat-1]-1]
        # wait until it's time
        while (globalClock.getTime()<tNextFlip[0]):
            core.wait(0.0001)
#            pass
        # play sound
        thisSound.play()
        # add to flip time
        AddToFlipTime(beatTime)
        # check for escape characters
        thisKey = event.getKeys()
        if thisKey!=None and len(thisKey)>0 and thisKey[0] in ['q','escape']:
            core.quit()
    
    # ===REPEAT=== #
    # Draw repeat cross
    fixRed.draw()
    win.logOnFlip(level=logging.EXP, msg='Display fixRed')
    
    # play trial sounds
    for iBeat in range(0, nTrialBeats):
        # prepare next sound
        thisSound = sequenceSound[sequence2[iBeat]-1]
        # wait until it's time
        while (globalClock.getTime()<tNextFlip[0]):
            core.wait(0.0001)
#            pass
        # On first beat, flip display
        if iBeat==0:
            win.flip()
        # play sound
        thisSound.play()
        # add to flip time
        AddToFlipTime(beatTime)
        
        # check for escape characters
        thisKey = event.getKeys()
        if thisKey!=None and len(thisKey)>0 and thisKey[0] in ['q','escape']:
            core.quit()
    
    # ===RESPONSE=== #
    # Draw response cross
    fixYellow.draw()
    win.logOnFlip(level=logging.EXP, msg='Display fixYellow')
    # wait until it's time
    while (globalClock.getTime()<tNextFlip[0]):
        core.wait(0.0001)
#        pass
    # flip display
    win.flip()
    AddToFlipTime(respTime)


# =========================== #
# ======= RUN PROMPTS ======= #
# =========================== #

# display prompts
if not params['skipPrompts']:
    PromptTools.RunPrompts(topPrompts,bottomPrompts,win,message1,message2)

# wait for scanner
message1.setText("Waiting for scanner to start...")
message2.setText("(Press '%c' to override.)"%params['triggerKey'].upper())
message1.draw()
message2.draw()
win.logOnFlip(level=logging.EXP, msg='Display WaitingForScanner')
win.flip()
event.waitKeys(keyList=params['triggerKey'])
tStartSession = globalClock.getTime()
AddToFlipTime(tStartSession+params['tStartup'])

# wait before first stimulus
fixation.draw()
win.logOnFlip(level=logging.EXP, msg='Display Fixation')
win.flip()


# =========================== #
# ===== MAIN EXPERIMENT ===== #
# =========================== #


# set up other stuff
logging.log(level=logging.EXP, msg='---START EXPERIMENT---')

# Run trials
for iTrial in range(0,params['nTrials']): # for each block of pages
    
    # log new block
    logging.log(level=logging.EXP, msg='Trial %d'%iTrial)
    
    # pick first sequence
    iSeq = random.randint(0,len(params['sequences']))
    sequence1 = list(params['sequences'][iSeq])
    # pick second sequence
    isRepeat = (random.random() < params['chanceOfRepeat'])
    print('isRepeat = %d'%(isRepeat))
    sequence2 = list(sequence1) # use list to make a copy
    if not isRepeat: # second sequence should be the matching one (0<-->1, 2<-->3)
        if (iSeq%2)==1:
            sequence2 = list(params['sequences'][iSeq-1])
        else:
            sequence2 = list(params['sequences'][iSeq+1])
#        while sequence2[-1]==sequence1[-1]:
#            sequence2[-1] = random.randint(1,4)
    logging.log(level=logging.EXP, msg='sequence 1: %s'%(sequence1))
    logging.log(level=logging.EXP, msg='sequence 2: %s'%(sequence2))
    
    # determine the ITI
    ITI = random.random()*(params['maxITI']-params['minITI']) + params['minITI']
    logging.log(level=logging.EXP, msg='ITI: %s'%(ITI))
    
    # Run the trial
    RunTrial(params['beatTime'],params['trialTime'],params['delayTime'],params['respTime'],ITI,sequence1,sequence2)
    print('9')

# handle end of run
message1.setText("That's the end of this run!")
message2.setText("Please stay still until the scanner noise stops.")
win.logOnFlip(level=logging.EXP, msg='Display TheEnd')
message1.draw()
message2.draw()
# wait until it's time
while (globalClock.getTime()<tNextFlip[0]):
    core.wait(0.0001)
#        pass
# change the screen
win.flip()
# wait until a button is pressed to exit
thisKey = event.waitKeys(keyList=['q','escape'])

# exit experiment
core.quit()
