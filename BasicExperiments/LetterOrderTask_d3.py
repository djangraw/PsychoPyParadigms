#!/usr/bin/env python2
"""Display a string of letters to the subject, then ask them whether a certain letter 
is at a certain position in the sequence. On some trials, ask them to alphabetize the 
letters in their head."""
# LetterOrderTask_d1.py
# Created 10/05/17 by DJ based on SampleExperiment_d1.py
# Updated 10/24/17 by DJ - fixed basename, random doubles, logging, escape keys at end
# Updated 10/31/17 by DJ - switched to 5-button response, added catch trials
# Updated 11/2/17 by DJ - switched from specified nTrials to max session time, removed extraneous 'true trial' designation

from psychopy import core, gui, data, event, sound, logging 
# from psychopy import visual # visual causes a bug in the guis, so it's declared after all GUIs run.
from psychopy.tools.filetools import fromFile, toFile # saving and loading parameter files
import time as ts, numpy as np # for timing and array operations
import AppKit, os, glob # for monitor size detection, files
import BasicPromptTools # for loading/presenting prompts and questions
import random, string # for randomization of trials, letters

# ====================== #
# ===== PARAMETERS ===== #
# ====================== #
# Save the parameters declared below?
saveParams = True;
newParamsFilename = 'LetterOrderParams.pickle'

# Declare primary task parameters.
params = {
# Declare stimulus and response parameters
#    'nTrials': 12,            # number of trials in this session
    'sessionDur': 300.0,          # max duration of this session, including warm-up and cool-down (in seconds)
    'nLetters': 5,            # number of letters in the string
    'stringDur': 2.5,           # time string is on screen (sec)
    'pauseDur': 1.0,          # time between string and cue (sec)
    'cueDur': 1.0,              # time instructions (remember/alphabetize) are on screen (sec)
    'minDelayDur': 7.0,         # minimum duration of cue-resp delay (seconds)
    'maxDelayDur': 11.0,         # maximum duration of cue-resp delay (seconds)
    'testDur': 1.0,             # time when test stimulus is presented (in seconds)
    'minISI': 7.0,              # min time between when one stimulus disappears and the next appears (in seconds)
    'maxISI': 11.0,              # max time between when one stimulus disappears and the next appears (in seconds)
    'tStartup': 10.0,            # pause time before starting first stimulus
    'tCoolDown': 10.0,           # pause time after end of last stimulus before "the end" text
    'triggerKey': 't',        # key from scanner that says scan is starting
    'respKeys': ['1','2','3','4','5'],           # keys to be used for responses (mapped to positions 1,2,3,4,5)
    'cues':['REMEMBER','ALPHABETIZE'], # strings of instructions for each condition (remember, alphabetize)
    'letters': string.ascii_uppercase, # letters that could be in the string (all uppercase letters)
    'rememberProb': 0.5,      # probability of a given trial being a 'remember' trial
    'catchProb': 1.0/3,         # probability of a given trial being a 'catch' trial with no response requested (must have decimal to avoid rounding)
# declare prompt and question files
    'skipPrompts': False,     # go right to the scanner-wait page
    'promptDir': 'Prompts/',  # directory containing prompts and questions files
    'promptFile': 'LetterOrderPrompts_5button.txt', # Name of text file containing prompts 
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
scriptName = os.path.splitext(scriptName)[0] # remove extension
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
mainText = visual.TextStim(win, pos=[0,-0], wrapWidth=3.5, color='#000000', alignHoriz='center', name='mainText', text="bbb",units='norm')

# read prompts from text files
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

def RunTrial(iTrial):
    # Flush the key buffer and mouse movements
    event.clearEvents()

    # Decide Trial Params
    isRememberTrial = random.random()<params['rememberProb']
    isCatchTrial = random.random()<params['catchProb']
    delayDur = random.uniform(params['minDelayDur'], params['maxDelayDur'])
    ISI = random.uniform(params['minISI'], params['maxISI'])
    startLetters = random.sample(params['letters'], params['nLetters']) # get list of letters to present to subject
    startString = ''.join(startLetters) # turn them into a string
    testLoc = random.randint(0,params['nLetters']-1) # the letter to test the subject on
    if isCatchTrial:
        testLetter = '*' # indicates no response is required.
    else:
        if isRememberTrial:
            testLetter = startLetters[testLoc];
        else: # alphabetize!
            sortedLetters = sorted(startLetters)
            testLetter = sortedLetters[testLoc]
    testString = '%s?'%(testLetter) 
    
    # display info to experimenter
    print('trial: iTrial = %d, isRemember = %d, delayDur = %.1f, ISI = %.1f, startString = %s, testLetter = %s, testLoc = %d, isCatchTrial = %d'%(iTrial+1,isRememberTrial,delayDur,ISI,startString,testLetter,testLoc+1,isCatchTrial)) 
    logging.log(level=logging.EXP, msg='trial: iTrial = %d, isRemember = %d, delayDur = %.1f, ISI = %.1f, startString = %s, testLetter = %s, testLoc = %d, isCatchTrial = %d'%(iTrial+1,isRememberTrial,delayDur,ISI,startString,testLetter,testLoc+1,isCatchTrial)) 
    
    # Draw letters
    mainText.setText(startString)
    mainText.draw()
    win.logOnFlip(level=logging.EXP, msg='Display string (%s)'%startString)
    # Wait until it's time to display
    while (globalClock.getTime()<tNextFlip[0]):
        pass
    # log & flip window to display image
    win.flip()
    tStringStart = globalClock.getTime() # record time when window flipped
    # set up next win flip time after this one
    AddToFlipTime(params['stringDur']) # add to tNextFlip[0]
    
    # Draw fixation (PAUSE)
    fixation.draw()
    win.logOnFlip(level=logging.EXP, msg='Display fixation (pause)')
    # Wait until it's time to display
    while (globalClock.getTime()<tNextFlip[0]):
        pass
    # log & flip window to display image
    win.flip()
    # set up next win flip time after this one
    AddToFlipTime(params['pauseDur']) # add to tNextFlip[0]
    
    # Draw cue
    if isRememberTrial:
        mainText.setText(params['cues'][0])
        win.logOnFlip(level=logging.EXP, msg='Display cue (%s)'%params['cues'][0])
    else:
        mainText.setText(params['cues'][1])
        win.logOnFlip(level=logging.EXP, msg='Display cue (%s)'%params['cues'][1])
    mainText.draw()
    # Wait until it's time to display
    while (globalClock.getTime()<tNextFlip[0]):
        pass
    # log & flip window to display image
    win.flip()
    tStimStart = globalClock.getTime() # record time when window flipped
    # set up next win flip time after this one
    AddToFlipTime(params['cueDur']) # add to tNextFlip[0]
    
    # Draw fixation (DELAY)
    fixation.draw()
    win.logOnFlip(level=logging.EXP, msg='Display fixation (delay)')
    # Wait until it's time to display
    while (globalClock.getTime()<tNextFlip[0]):
        pass
    # log & flip window to display image
    win.flip()
    # set up next win flip time after this one
    AddToFlipTime(delayDur) # add to tNextFlip[0]
    
    # Draw letters (test
    mainText.setText(testString)
    mainText.draw()
    win.logOnFlip(level=logging.EXP, msg='Display test stim (%s)'%testString)
    # Wait until it's time to display
    while (globalClock.getTime()<tNextFlip[0]):
        pass
    # log & flip window to display image
    win.flip()
    # set up next win flip time after this one
    AddToFlipTime(params['testDur']) # add to tNextFlip[0]
    
    # Draw fixation for next frame (but don't display yet)
    fixation.draw() # draw it
    win.logOnFlip(level=logging.EXP, msg='Display fixation (ISI)')
    
    # Wait for 'testDur' seconds while recording relevant key presses 
    respKey = None
    while (globalClock.getTime()<tNextFlip[0]): # until it's time for the next frame
        # get new keys
        newKeys = event.getKeys(keyList=params['respKeys']+['q','escape'],timeStamped=globalClock)
        # check each keypress for escape or response keys
        if len(newKeys)>0:
            for thisKey in newKeys: 
                if thisKey[0] in ['q','escape']: # escape keys
                    CoolDown() # exit gracefully
                elif thisKey[0] in params['respKeys'] and respKey == None: # only take first keypress
                    respKey = thisKey # record keypress
                    print(respKey)
                    logging.log(level=logging.EXP, msg='pressed key %s'%respKey[0])
        
    # Display fixation cross (ISI)
    win.flip()
    AddToFlipTime(ISI) # -1 to give the next trial time to load up
    
    # Keep waiting while recording relevant key presses
    while (globalClock.getTime()<tNextFlip[0] -1 ): # Include -1 to give time for next trial to load
        # get new keys
        newKeys = event.getKeys(keyList=params['respKeys']+['q','escape'],timeStamped=globalClock)
        # check each keypress for escape or response keys
        if len(newKeys)>0:
            for thisKey in newKeys: 
                if thisKey[0] in ['q','escape']: # escape keys
                    CoolDown() # exit gracefully
                elif thisKey[0] in params['respKeys'] and respKey == None: # only take first keypress
                    respKey = thisKey # record keypress
                    print(respKey)
                    logging.log(level=logging.EXP, msg='pressed key %s'%respKey[0])
    
    return 

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
win.logOnFlip(level=logging.EXP, msg='Display fixation')
win.flip()




# =========================== #
# ===== MAIN EXPERIMENT ===== #
# =========================== #

# log experiment start and set up
logging.log(level=logging.EXP, msg='---START EXPERIMENT---')
maxPossibleTrialDur = params['stringDur'] + params['pauseDur'] + params['cueDur'] + params['maxDelayDur'] + params['testDur'] + params['tCoolDown']
tLastTrial = tStartSession + params['sessionDur'] - maxPossibleTrialDur
print maxPossibleTrialDur
print tLastTrial
iTrial = 0 # initialize trial number
# run trials
# for iTrial in range(0,params['nTrials']):
while (globalClock.getTime() < tLastTrial):
    # increment trial number
    iTrial = iTrial+1
    # display text
    RunTrial(iTrial)

# Set flip time to end of session
tNextFlip[0] = tStartSession + params['sessionDur']

# wait before 'the end' text
while (globalClock.getTime()<tNextFlip[0]):
    # check for escape keys
    newKeys = event.getKeys(keyList=['q','escape'],timeStamped=globalClock)
    # check each keypress for escape or response keys
    if len(newKeys)>0:
        for thisKey in newKeys: 
            if thisKey[0] in ['q','escape']: # escape keys
                CoolDown() # exit gracefully

# Log end of experiment
logging.log(level=logging.EXP, msg='--- END EXPERIMENT ---')

# exit experiment
CoolDown()