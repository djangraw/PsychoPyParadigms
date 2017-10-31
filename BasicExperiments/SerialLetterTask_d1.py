#!/usr/bin/env python2
"""Display letters regularly to the subject. Subj must respond to a target letter 
only if it's different from the previous target letter.
Based on (Garavan, 1999 PNAS) doi:10.1073/pnas.96.14.8301"""

# SerialLetterTask_d1.py
# Created 10/06/17 by DJ based on GoNoGoTask_d1.py

from psychopy import core, gui, data, event, sound, logging 
# from psychopy import visual # visual causes a bug in the guis, so it's declared after all GUIs run.
from psychopy.tools.filetools import fromFile, toFile # saving and loading parameter files
import time as ts, numpy as np # for timing and array operations
import AppKit, os, glob # for monitor size detection, files
import BasicPromptTools # for loading/presenting prompts and questions
import random, math # for randomization of trials, math

# ====================== #
# ===== PARAMETERS ===== #
# ====================== #
# Save the parameters declared below?
saveParams = True;
newParamsFilename = 'SerialLetterParams.pickle'

# Declare primary task parameters.
params = {
# Declare stimulus and response parameters
    'nTrials': 10,            # number of trials in this session
    'stimDur': 0.5,             # time when stimulus is presented (in seconds)
    'tStartup': 2,            # pause time before starting first stimulus
    'tCoolDown': 2,           # pause time after end of last stimulus before "the end" text
    'triggerKey': 't',        # key from scanner that says scan is starting
    'respKeys': ['r'],           # keys to be used for responses (mapped to 1,2,3,4)
    'nullLetters': ['A','B','C','D'], # null
    'GoLetters': ['X','Y'],          # shape signaling oncoming trial
    'minGoInterval', 30 # in letters
    'goStimProb': 0.8,        # probability of a given trial being a 'go' trial
    'lureProb': 0.8, # given a go stim, what's the probability that the next is the same letter (a lure)?
# declare prompt and question files
    'skipPrompts': False,     # go right to the scanner-wait page
    'promptDir': 'Prompts/',  # directory containing prompts and questions files
    'promptFile': 'GoNoGoPrompts.txt', # Name of text file containing prompts 
# declare display parameters
    'fullScreen': True,       # run in full screen mode?
    'screenToShow': 0,        # display on primary screen (0) or secondary (1)?
    'fixCrossSize': 50,       # size of cross, in pixels
    'fixCrossPos': [0,0],     # (x,y) pos of fixation cross displayed before each stimulus (for gaze drift correction)
    'screenColor':(128,128,128) # in rgb255 space: (r,g,b) all between 0 and 255
}

# save parameters
if saveParams:
    dlgResult = gui.fileSaveDlg(prompt='Save Params...',initFilePath = os.getcwd() + '/Params', initFileName = newParamsFilename,
        allowed="PICKLE files (.pickle)|.pickle|All files (.*)|")
    newParamsFilename = dlgResult
    if newParamsFilename is None: # keep going, but don't save
        saveParams = False
    else:
        toFile(newParamsFilename, params) # save it!

# ========================== #
# ===== SET UP LOGGING ===== #
# ========================== #
scriptName = os.path.basename(__file__)
try: # try to get a previous parameters file
    expInfo = fromFile('%s-lastExpInfo.pickle'%scriptName)
    expInfo['session'] +=1 # automatically increment session number
    expInfo['paramsFile'] = [expInfo['paramsFile'],'Load...']
except: # if not there then use a default set
    expInfo = {
        'subject':'1', 
        'session': 1, 
        'skipPrompts':False, 
        'paramsFile':['DEFAULT','Load...']}
# overwrite params struct if you just saved a new parameter set
if saveParams:
    expInfo['paramsFile'] = [newParamsFilename,'Load...']

#present a dialogue to change select params
dlg = gui.DlgFromDict(expInfo, title=scriptName, order=['subject','session','skipPrompts','paramsFile'])
if not dlg.OK:
    core.quit() # the user hit cancel, so exit

# find parameter file
if expInfo['paramsFile'] == 'Load...':
    dlgResult = gui.fileOpenDlg(prompt='Select parameters file',tryFilePath=os.getcwd(),
        allowed="PICKLE files (.pickle)|.pickle|All files (.*)|")
    expInfo['paramsFile'] = dlgResult[0]
# load parameter file
if expInfo['paramsFile'] not in ['DEFAULT', None]: # otherwise, just use defaults.
    # load params file
    params = fromFile(expInfo['paramsFile'])


# transfer skipPrompts from expInfo (gui input) to params (logged parameters)
params['skipPrompts'] = expInfo['skipPrompts']

# print params to Output
print 'params = {'
for key in sorted(params.keys()):
    print "   '%s': %s"%(key,params[key]) # print each value as-is (no quotes)
print '}'
    
# save experimental info
toFile('%s-lastExpInfo.pickle'%scriptName, expInfo)#save params to file for next time

#make a log file to save parameter/event  data
dateStr = ts.strftime("%b_%d_%H%M", ts.localtime()) # add the current time
filename = '%s-%s-%d-%s'%(scriptName,expInfo['subject'], expInfo['session'], dateStr) # log filename
logging.LogFile((filename+'.log'), level=logging.INFO)#, mode='w') # w=overwrite
logging.log(level=logging.INFO, msg='---START PARAMETERS---')
logging.log(level=logging.INFO, msg='filename: %s'%filename)
logging.log(level=logging.INFO, msg='subject: %s'%expInfo['subject'])
logging.log(level=logging.INFO, msg='session: %s'%expInfo['session'])
logging.log(level=logging.INFO, msg='date: %s'%dateStr)
# log everything in the params struct
for key in sorted(params.keys()): # in alphabetical order
    logging.log(level=logging.INFO, msg='%s: %s'%(key,params[key])) # log each parameter

logging.log(level=logging.INFO, msg='---END PARAMETERS---')


# ========================== #
# ===== GET SCREEN RES ===== #
# ========================== #

# kluge for secondary monitor
if params['fullScreen']: 
    screens = AppKit.NSScreen.screens()
    screenRes = (int(screens[params['screenToShow']].frame().size.width), int(screens[params['screenToShow']].frame().size.height))
#    screenRes = [1920, 1200]
    if params['screenToShow']>0:
        params['fullScreen'] = False
else:
    screenRes = [800,600]

print "screenRes = [%d,%d]"%screenRes


# ========================== #
# ===== SET UP STIMULI ===== #
# ========================== #
from psychopy import visual

# Initialize deadline for displaying next frame
tNextFlip = [0.0] # put in a list to make it mutable (weird quirk of python variables) 

#create clocks and window
globalClock = core.Clock()#to keep track of time
trialClock = core.Clock()#to keep track of time
win = visual.Window(screenRes, fullscr=params['fullScreen'], allowGUI=False, monitor='testMonitor', screen=params['screenToShow'], units='deg', name='win',color=params['screenColor'],colorSpace='rgb255')
# create fixation cross
fCS = params['fixCrossSize'] # size (for brevity)
fCP = params['fixCrossPos'] # position (for brevity)
fixation = visual.ShapeStim(win,lineColor='#000000',lineWidth=3.0,vertices=((fCP[0]-fCS/2,fCP[1]),(fCP[0]+fCS/2,fCP[1]),(fCP[0],fCP[1]),(fCP[0],fCP[1]+fCS/2),(fCP[0],fCP[1]-fCS/2)),units='pix',closeShape=False,name='fixCross');
# create text stimuli
message1 = visual.TextStim(win, pos=[0,+.5], wrapWidth=1.5, color='#000000', alignHoriz='center', name='topMsg', text="aaa",units='norm')
message2 = visual.TextStim(win, pos=[0,-.5], wrapWidth=1.5, color='#000000', alignHoriz='center', name='bottomMsg', text="bbb",units='norm')

# draw stimuli
mainText = visual.TextStim(win, pos=[0,0], wrapWidth=1.5, color='#000000', alignHoriz='center', name='mainText', text="ccc",units='norm')


# read questions and answers from text files
[topPrompts,bottomPrompts] = BasicPromptTools.ParsePromptFile(params['promptDir']+params['promptFile'])
print('%d prompts loaded from %s'%(len(topPrompts),params['promptFile']))

# ============================ #
# ======= SUBFUNCTIONS ======= #
# ============================ #

# increment time of next window flip
def AddToFlipTime(tIncrement=1.0):
    tNextFlip[0] += tIncrement

# flip window as soon as possible
def SetFlipTimeToNow():
    tNextFlip[0] = globalClock.getTime()

def RunTrial(iTrial,iLastGoTrial,lastGoLetter):
    
    # Decide Trial Params
    if iTrial-iLastGoTrial<params['minGoInterval']:
        isGoTrial=0
    else:
        isGoTrial = random.random()<params['goStimProb']
    
    if isGoTrial:
        isLureTrial = random.random()<params['lureProb']
        if isLureTrial:
            thisLetter = lastGoLetter
        else:
            otherGoLetters = list(set(params['goLetters'])-lastGoLetter)
            thisLetter = random.choice(otherGoLetters)
            lastGoLetter = thisLetter
            iLastGoTrial=iTrial
    else:
        thisLetter = random.choice(params['nullLetters'])
            
    # display info to experimenter
    print('Running Trial %d: isGo = %d, isLure = %.1f'%(iTrial,isGoTrial,cueDur)) 
    
    # Draw stim
    if isGoTrial:
        mainText.setText(params['goLetters']])
        win.logOnFlip(level=logging.EXP, msg='Display go stim (%s)'%params['goStim'])
    else:
        mainText.setText(params['goLetters']])
        win.logOnFlip(level=logging.EXP, msg='Display no-go stim (%s)'%params['noGoStim'])
    mainText.draw()
    # Wait until it's time to display
    while (globalClock.getTime()<tNextFlip[0]):
        pass
    # log & flip window to display image
    win.flip()
    tStimStart = globalClock.getTime() # record time when window flipped
    # set up next win flip time after this one
    AddToFlipTime(params['stimDur']) # add to tNextFlip[0]
        
    # Wait for relevant key press or 'stimDur' seconds
    newKeys = event.getKeys(keyList=params['respKeys']+['q','escape'],timeStamped=globalClock)
    # check each keypress for escape or response keys
    if len(newKeys)>0:
        for thisKey in newKeys: 
            if thisKey[0] in ['q','escape']: # escape keys
                CoolDown() # exit gracefully
    
    # Flush the key buffer and mouse movements
    event.clearEvents()
    
    return(iLastGoTrial,lastGoLetter)

# Handle end of a session
def CoolDown():
    
    # display cool-down message
    message1.setText("That's the end! ")
    message2.setText("Press 'q' or 'escape' to end the session.")
    win.logOnFlip(level=logging.EXP, msg='Display TheEnd')
    message1.draw()
    message2.draw()
    win.flip()
    thisKey = event.waitKeys(keyList=['q','escape'])
    
    # exit
    core.quit()


# =========================== #
# ======= RUN PROMPTS ======= #
# =========================== #

# display prompts
if not params['skipPrompts']:
    BasicPromptTools.RunPrompts(topPrompts,bottomPrompts,win,message1,message2)

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

# log experiment start and set up
logging.log(level=logging.EXP, msg='---START EXPERIMENT---')

# run trials
iLastGoTrial = 0
lastGoLetter = []
for iTrial in range(0,params['nTrials']):
    # display text
    [iLastGoTrial,lastGoLetter] = RunTrial(iTrial,iLastGoTrial,lastGoLetter)



# wait before 'the end' text
fixation.draw()
win.flip()
AddToFlipTime(params['tCoolDown'])
while (globalClock.getTime()<tNextFlip[0]):
        pass

# Log end of experiment
logging.log(level=logging.EXP, msg='--- END EXPERIMENT ---')

# exit experiment
CoolDown()