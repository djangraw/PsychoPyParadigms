#!/usr/bin/env python2
"""Display a visual viglilance task where the dot at the center changes color periodically."""
# ColorVigilanceTask.py
# Created 1/3/16 by DJ based on VidLecTask_vigilance.py

from psychopy import core, gui, data, event, sound, logging#, visual # visual causes a bug in the guis, so I moved it down.
from psychopy.tools.filetools import fromFile, toFile
import time, numpy as np
import AppKit, os # for monitor size detection, files
import PromptTools

# ====================== #
# ===== PARAMETERS ===== #
# ====================== #
# Save the parameters declared below?
saveParams = True;
newParamsFilename = 'VigTestParams.pickle'

# Declare primary task parameters.
params = {
    'nBlocks': 1,             # number of blocks per run
    'BlockTimeRange': [10, 15], # length of block will be between these times (in seconds)
    'IBI': 1,                 # time between end of block/probe and beginning of next block (in seconds)
    'triggerKey': 't',        # key from scanner that says scan is starting
# declare prompts
    'promptType': 'Default', # option in PromptTools.GetPrompts (options are ['Test','Backwards','Wander','Attend'])
# declare other stimulus parameters
    'fullScreen': True,       # run in full screen mode?
    'screenToShow': 0,        # display on primary screen (0) or secondary (1)?
    'fixCrossSize': 10,       # size of cross, in pixels
# declare vigilance params
    'ITI_min': 1.0,         # min time between targets (in seconds)
    'ITI_max': 3.0,        # max time between targets (in seconds)
    'respKey': 'j',         # key the subject should press to respond
    'dotRadius':10.0,
    'dotColor': 'black',
    'targetRadius':10.0,
    'targetColor': 'red',
    'targetDuration': 0.100
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
    expInfo = fromFile('lastColorVigInfo.pickle')
    expInfo['session'] +=1 # automatically increment session number
    expInfo['paramsFile'] = [expInfo['paramsFile'],'Load...']
except:#if not there then use a default set
    expInfo = {'subject':'1', 'session':1, 'paramsFile':['DEFAULT','Load...']}
# overwrite if you just saved a new parameter set
if saveParams:
    expInfo['paramsFile'] = [newParamsFilename,'Load...']
dateStr = time.strftime("%b_%d_%H%M", time.localtime()) # add the current time

#present a dialogue to change params
dlg = gui.DlgFromDict(expInfo, title='Color Vigilance task', order=['subject','session','paramsFile'])
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
toFile('lastColorVigInfo.pickle', expInfo)#save params to file for next time

#make a log file to save parameter/event  data
filename = 'ColorVig-%s-%d-%s'%(expInfo['subject'], expInfo['session'], dateStr) #'Sart-' + expInfo['subject'] + '-' + expInfo['session'] + '-' + dateStr
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


#create window and stimuli
globalClock = core.Clock()#to keep track of time
trialClock = core.Clock()#to keep track of time
win = visual.Window(screenRes, fullscr=params['fullScreen'], allowGUI=False, monitor='testMonitor', screen=params['screenToShow'], units='deg', name='win')
#fixation = visual.GratingStim(win, color='black', tex=None, mask='circle',size=0.2)
fCS = params['fixCrossSize'] # for brevity
fixation = visual.ShapeStim(win,lineColor='#000000',lineWidth=3.0,vertices=((-fCS/2,0),(fCS/2,0),(0,0),(0,fCS/2),(0,-fCS/2)),units='pix',closeShape=False);
message1 = visual.TextStim(win, pos=[0,+3], wrapWidth=30, color='#000000', alignHoriz='center', name='topMsg', text="aaa")
message2 = visual.TextStim(win, pos=[0,-3], wrapWidth=30, color='#000000', alignHoriz='center', name='bottomMsg', text="bbb")
# initialize dot stimulus
dot = visual.Circle(win, radius=params['dotRadius'],fillColor=params['dotColor'],lineColor=params['dotColor'],units='pix')
target = visual.Circle(win, radius=params['targetRadius'],fillColor=params['targetColor'],lineColor=params['targetColor'],units='pix')

# Look up prompts
[topPrompts,bottomPrompts] = PromptTools.GetPrompts(os.path.basename(__file__),params['promptType'],params)

# ============================ #
# ======= SUBFUNCTIONS ======= #
# ============================ #

def RunBlock(blockDuration):
    # set up vigilance stimuli
    dot.draw()
    nextOffTime = 0
    nextTargetTime = globalClock.getTime() + np.random.uniform(params['ITI_min'],params['ITI_max'])
    blockEndTime = globalClock.getTime() + blockDuration
    print(blockEndTime)
    isTarget = True
    frameTime = globalClock.getTime()
    # Change dot if it's time
    while frameTime<blockEndTime:
        frameTime = globalClock.getTime()
        if (isTarget):  
            if (frameTime > nextOffTime):
                dot.draw()
                isTarget = False
                nextOffTime = nextTargetTime + params['targetDuration']
                win.logOnFlip(level=logging.EXP, msg='Display Dot')
            else:
                target.draw()
        else: # target is off
            if (frameTime > nextTargetTime):
                target.draw()
                isTarget = True
                nextTargetTime = frameTime + np.random.uniform(params['ITI_min'],params['ITI_max'])
                win.logOnFlip(level=logging.EXP, msg='Display Target')
            else:
                dot.draw()
        # update window
        win.flip()
        # Check for action keys (stolen from MovieTest.py).....
        for key in event.getKeys():
            if key in ['escape', 'q']:
                win.close()
                core.quit()

# =========================== #
# ======= RUN PROMPTS ======= #
# =========================== #

# display prompts
PromptTools.RunPrompts(topPrompts,bottomPrompts,win,message1,message2)


# wait for scanner
message1.setText("Waiting for scanner to start...")
message2.setText("(Press '%c' to override.)"%params['triggerKey'].upper())
message1.draw()
message2.draw()
win.logOnFlip(level=logging.EXP, msg='Display WaitingForScanner')
win.flip()
event.waitKeys(keyList=params['triggerKey'])

# do brief wait before first stimulus
fixation.draw()
win.logOnFlip(level=logging.EXP, msg='Display Fixation')
win.flip()
core.wait(params['IBI'], params['IBI'])


# =========================== #
# ===== MAIN EXPERIMENT ===== #
# =========================== #

# set up other stuff
logging.log(level=logging.EXP, msg='---START EXPERIMENT---')
blockTimeRange = params['BlockTimeRange']
nBlocks = params['nBlocks']

for iBlock in range(0,nBlocks): # for each block of trials
    
    # log new block
    logging.log(level=logging.EXP, msg='Start Block %d'%iBlock)
    # run block
    tBlock = np.random.uniform(blockTimeRange[0],blockTimeRange[1])
    RunBlock(tBlock)
    # pause before next block
    core.wait(params['IBI'],params['IBI'])
    # tell the subject if it's break time.
    if iBlock < (nBlocks-1): # show break prompt
        allKeys = PromptTools.RunPrompts('Take a break!','Press any key to move to the next block.',win,message1,message2)
        # check for escape keypresses
        for thisKey in allKeys:
            if thisKey[0] in ['q', 'escape']: # check for quit keys
                core.quit()#abort experiment
        # display fixation
        fixation.draw()
        win.logOnFlip(level=logging.EXP, msg='Display Fixation')
        win.flip()
        core.wait(params['IBI'],params['IBI'])
    
# display cool-down message
message1.setText("That's the end! Please stay still until the scan is complete.")
message2.setText("(Press 'q' or 'escape' to override.)")
win.logOnFlip(level=logging.EXP, msg='Display TheEnd')
message1.draw()
message2.draw()
win.flip()
thisKey = event.waitKeys(['q','escape'])

# exit experiment
core.quit()
