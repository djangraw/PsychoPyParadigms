#!/usr/bin/env python2
"""Display text at speeds that vary linearly over time."""

# VisualSpeedReadingTask_d1.py
#
# Created 6/4/18 by DJ based on AuditorySpeedReadingTask_d1.py.
# Updated 12/31/18 by DJ - modified to allow each block's speeds to be specified separately.

from psychopy import core, gui, data, event, sound, logging #, visual # visual causes a bug in the guis, so I moved it down.
from psychopy.tools.filetools import fromFile, toFile
import random
import time, numpy as np
import AppKit, os # for monitor size detection, files
import PromptTools
import numpy as np # for frame time calculations

# ====================== #
# ===== PARAMETERS ===== #
# ====================== #
# Save the parameters declared below?
saveParams = True;
newParamsFilename = 'VisualSpeedReadingTaskParams.psydat'

# Declare primary task parameters.
params = {
    # declare timing parameters
    'skipPrompts': False,    # at the beginning
    'promptType': 'Default', # type of prompts (see PromptTools.py)
    'promptHeight': 2,
    'tStartup': 3.0,       # time after beginning of scan before starting first trial
    'tCoolDown': 3.0,      # time after end of last trial before end-of-session message
    'minITI': 5.0,
    'maxITI': 5.0,
    # declare text parameters
    'textFiles': ['text/EastOfTheSun.txt','text/ReluctantDragon.txt','text/BremenTownMusicians.txt'],
    'wordsPerFrame': 1,
    'textHeight': 3,
    'minFPM': [120,600,120],       # frames per minute at start of block
    'maxFPM': [120,600,2000],       # frames per minute at end of block
    'nFrames': [20, 100,400], # [2004]*2, # number of frames (words) for each block
    # declare other stimulus parameters
    'triggerKey': 't',
    'fullScreen': True,       # run in full screen mode?
    'screenToShow': 0,        # display on primary screen (0) or secondary (1)?
    'fixCrossSize': 50,       # size of cross, in pixels
    'fixCrossPos': (0,0), # (x,y) pos of fixation cross displayed before each page (for drift correction)
    'usePhotodiode': False     # add sync square in corner of screen
}

# save parameters
if saveParams:
    dlgResult = gui.fileSaveDlg(prompt='Save Params...',initFilePath = os.getcwd() + '/Params', initFileName = newParamsFilename,
        allowed="PICKLE files (.psydat)|.psydat|All files (.*)|")
    newParamsFilename = dlgResult
    if newParamsFilename is None: # keep going, but don't save
        saveParams = False
    else:
        toFile(newParamsFilename, params)# save it!


# ========================== #
# ===== SET UP LOGGING ===== #
# ========================== #
try:#try to get a previous parameters file
    expInfo = fromFile('lastVisSpeedInfo.psydat')
    expInfo['session'] +=1 # automatically increment session number
    expInfo['paramsFile'] = [expInfo['paramsFile'],'Load...']
except:#if not there then use a default set
    expInfo = {'subject':'1', 'session':1, 'paramsFile':['DEFAULT','Load...']}
# overwrite if you just saved a new parameter set
if saveParams:
    expInfo['paramsFile'] = [newParamsFilename,'Load...']
dateStr = time.strftime("%b_%d_%H%M", time.localtime()) # add the current time

#present a dialogue to change params
dlg = gui.DlgFromDict(expInfo, title='Visual Speed-Reading task', order=['subject','session','paramsFile'])
if not dlg.OK:
    core.quit()#the user hit cancel so exit

# find parameter file
if expInfo['paramsFile'] == 'Load...':
    dlgResult = gui.fileOpenDlg(prompt='Select parameters file',tryFilePath=os.getcwd(),
        allowed="PICKLE files (.psydat)|.psydat|All files (.*)|")
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
toFile('lastVisSpeedInfo.psydat', expInfo)#save params to file for next time

#make a log file to save parameter/event  data
filename = 'VisSpeed-%s-%d-%s'%(expInfo['subject'], expInfo['session'], dateStr) #'Sart-' + expInfo['subject'] + '-' + expInfo['session'] + '-' + dateStr
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
fixation = visual.ShapeStim(win,lineColor='black',lineWidth=3.0,vertices=fCS_vertices,units='pix',closeShape=False);
fixRed = visual.ShapeStim(win,lineColor='black',lineWidth=3.0,vertices=fCS_vertices,units='pix',closeShape=False);
fixRed.lineColor = 'red'

# make text messages
message1 = visual.TextStim(win, pos=[0, 0], wrapWidth=50, color='black', alignHoriz='center', name='topMsg', text="aaa", height=params['promptHeight'])
message2 = visual.TextStim(win, pos=[0,-10], wrapWidth=50, color='black', alignHoriz='center', name='bottomMsg', text="bbb", height=params['promptHeight'])
mainText = visual.TextStim(win, pos=[0,0], wrapWidth=50, color='black', alignHoriz='center', name='bottomMsg', text="bbb", height=params['textHeight'])
# initialize photodiode stimulus
squareSize = 0.4
diodeSquare = visual.Rect(win,pos=[squareSize/4-1,squareSize/4-1],lineColor='white',fillColor='white',size=[squareSize,squareSize],units='norm')

# Look up prompts
[topPrompts,bottomPrompts] = PromptTools.GetPrompts(os.path.basename(__file__),params['promptType'],params)
print('%d prompts loaded from %s'%(len(topPrompts),'PromptTools.py'))

# Extract words
nTrials = len(params['textFiles'])
allFrames = [None]*nTrials
allIFI = [None]*nTrials
for i in range(0,nTrials):
    # read in text
    fid = open(params['textFiles'][i],'r')
    wholeText = fid.read()
    fid.close()
    # separate out into word list
    allWords = wholeText.split()
    # group words together
    allFrames[i] = []
    for j in range(params['nFrames'][i]):
        iWords = range(j*(params['wordsPerFrame']), (j+1)*params['wordsPerFrame'])
        allFrames[i].append(" ".join(allWords[i] for i in iWords))
    print('cropped block %d to %d words.'%(i,len(allFrames[i])))
    # calculate inter-frame intervals
    wpm = np.linspace(params['minFPM'][i],params['maxFPM'][i],params['nFrames'][i])
    allIFI[i] = 60.0/wpm # inter-frame interval in seconds

# ============================ #
# ======= SUBFUNCTIONS ======= #
# ============================ #

# increment time of next window flip
def AddToFlipTime(tIncrement=1.0):
    tNextFlip[0] += tIncrement
#    print("%1.3f --> %1.3f"%(globalClock.getTime(),tNextFlip[0]))

def RunTrial(frames,tIFIs,tISI):
    
    # ===TEXT=== #
    for i in range(len(frames)):
        # update text
        mainText.setText(frames[i])
        mainText.draw()
        win.logOnFlip(level=logging.EXP, msg='Display frame-%03d'%i)
        
        # wait until it's time
        while (globalClock.getTime()<tNextFlip[0]):
            # check for escape characters
            thisKey = event.getKeys()
            if thisKey!=None and len(thisKey)>0 and thisKey[0] in ['q','escape']:
                core.quit()
#            core.wait(0.0001)
        
        # now display
        win.flip()
        # add to flip time
        AddToFlipTime(tIFIs[i])
    
    # ===ISI=== #
    # set up ISI
    fixation.draw()
    win.logOnFlip(level=logging.EXP, msg='Display fixation')
    
    # wait for ISI
    while (globalClock.getTime()<tNextFlip[0]):
        # check for escape characters
        thisKey = event.getKeys()
        if thisKey!=None and len(thisKey)>0 and thisKey[0] in ['q','escape']:
            core.quit()
#        core.wait(0.0001)
#        pass
    
    # flip display and stop sound
    win.flip()
    AddToFlipTime(tISI)
    
    return

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
for iTrial in range(nTrials): # for each block of pages
    
    # log new block
    logging.log(level=logging.EXP, msg='Start trial %d'%iTrial)
    
    
    # determine the ITI
    if iTrial==(nTrials-1):
        ITI = params['tCoolDown']
    else:
        ITI = random.random()*(params['maxITI']-params['minITI']) + params['minITI']
        logging.log(level=logging.EXP, msg='ITI: %s'%(ITI))
    
    # Run the trial
    RunTrial(allFrames[iTrial],allIFI[iTrial],ITI)
    

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
