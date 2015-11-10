#!/usr/bin/env python2
"""Display multi-page text with a quiz at the end."""
# TappingWithTrTiming_d1.py
# Created 11/09/15 by DJ based on DistractionTask_practice_d3.py

from psychopy import core, gui, data, event, sound, logging 
# from psychopy import visual # visual causes a bug in the guis, so it's declared after all GUIs run.
from psychopy.tools.filetools import fromFile, toFile # saving and loading parameter files
import time as ts, numpy as np # for timing and array operations
import AppKit, os, glob # for monitor size detection, files
import BasicPromptTools # for loading/presenting prompts and questions
import random # for randomization of trials

# ====================== ##!/usr/bin/env python2
"""Display images from a specified folder and present them to the subject."""
# SampleExperiment_d1.py
# Created 11/09/15 by DJ based on DistractionTask_practice_d3.py
# Updated 11/10/15 by DJ - cleaned up comments

from psychopy import core, gui, data, event, sound, logging 
# from psychopy import visual # visual causes a bug in the guis, so it's declared after all GUIs run.
from psychopy.tools.filetools import fromFile, toFile # saving and loading parameter files
import time as ts, numpy as np # for timing and array operations
import AppKit, os, glob # for monitor size detection, files
import BasicPromptTools # for loading/presenting prompts and questions
import random # for randomization of trials

# ====================== #
# ===== PARAMETERS ===== #
# ====================== #
# Save the parameters declared below?
saveParams = True;
newParamsFilename = 'TappingParams.pickle'

# Declare primary task parameters.
params = {
# Declare stimulus and response parameters
    'nBlocks': 3,            # number of trials in this session
    'stimDur': [0.1, 0.1, 0.1],             # time when stimulus is presented (in seconds) for each block
    'ISI': [0.5, 1.0, 2.0],                 # time between when one stimulus disappears and the next appears (in seconds) for each block
    'blockDur_TRs': 3,            # duration of each tapping block (in TRs)
    'restDur_TRs': 3,             # duration of each rest block (in TRs)
    'tStartup_TRs': 0,            # pause time before starting first stimulus (in TRs)
    'triggerKey': 't',        # key from scanner that says scan is starting
    'dotSize': 100,              # size of dot in pixels
    'dotPos': [0,0],            # (x,y) position of dot in pixels
# declare prompt and question files
    'skipPrompts': False,     # go right to the scanner-wait page
    'promptDir': 'Text/',  # directory containing prompts and questions files
    'promptFile': 'TappingPrompts.txt', # Name of text file containing prompts 
# declare display parameters
    'fullScreen': True,       # run in full screen mode?
    'screenToShow': 1,        # display on primary screen (0) or secondary (1)?
    'fixCrossSize': 100,       # size of cross, in pixels
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

# initialize main dot stimulus
stimDot = visual.GratingStim(win, color='black', tex=None, mask='circle',pos=params['dotPos'],size=params['dotSize'],units='pix')

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

def CheckForTriggers():
    # get new keys
    newKeys = event.getKeys(keyList=[params['triggerKey'], 'q','escape'],timeStamped=globalClock)
    # check each keypress for escape or trigger keys
    nTriggers = 0
    if len(newKeys)>0:
        for thisKey in newKeys: 
            if thisKey[0] in ['q','escape']: # escape keys
                CoolDown() # exit gracefully
            elif thisKey[0] == params['triggerKey']:
                nTriggers = nTriggers + 1
                
    return nTriggers

def FlashDot(stimDur, ISI, blockDur_TRs):
    # Wait for escape key press or 'blockDur_TRs' triggers
    nTriggers = 0
    SetFlipTimeToNow()
    tBlockStart = globalClock.getTime() # record time when window flipped
    while (nTriggers < blockDur_TRs): # until it's time for the next frame
        # ---tapping dot
        # prepare stim
        stimDot.draw()
        win.logOnFlip(level=logging.EXP, msg='Display dot')
        # Wait until it's time to display
        while (globalClock.getTime()<tNextFlip[0]):
            # Check for triggers and increment trigger count
            nNew = CheckForTriggers()
            nTriggers = nTriggers + nNew
            # check for final trigger
            if nTriggers >= blockDur_TRs:
                break
        # check for final trigger
        if nTriggers >= blockDur_TRs:
            break
        # log & flip window to display dot
        win.flip()
        AddToFlipTime(stimDur) # add to tNextFlip[0]
        
        # ---Fixation
        # prepare stim
        win.logOnFlip(level=logging.EXP, msg='Display fixation')
        # Wait until it's time to display
        while (globalClock.getTime()<tNextFlip[0]):
            # Check for triggers and increment trigger count
            nNew = CheckForTriggers()
            nTriggers = nTriggers + nNew
            # check for final trigger
            if nTriggers >= blockDur_TRs:
                break
        # check for final trigger
        if nTriggers >= blockDur_TRs:
            break
        # log & flip window to display image
        win.flip()
        AddToFlipTime(ISI) # add to tNextFlip[0]
        
    # Get block time
    tBlock = globalClock.getTime()-tBlockStart
    print('Block time: %.3f seconds'%(tBlock))
    
    
    return (tBlock)

# Pause until a given number of TRs is received.
def WaitForTrs(tWait_TRs):
    # do IBI
    nTriggers = 0
    while (nTriggers < tWait_TRs):
        # Check for triggers and increment trigger count
        nNew = CheckForTriggers()
        nTriggers = nTriggers + nNew
        if nTriggers >= tWait_TRs:
            break


# Handle end of a session
def CoolDown():
    
    # display cool-down message
    message1.setText("That's the end! ")
    message2.setText("Press 'q' or 'escape' to end the session.")
    win.logOnFlip(level=logging.EXP, msg='Display TheEnd')
    win.clearBuffer() # clear the screen
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
message1.setText("Please don't move...")
message2.setText("") #("(Press '%c' to override.)"%params['triggerKey'].upper())
message1.draw()
message2.draw()
win.logOnFlip(level=logging.EXP, msg='PleaseDontMove') #'Display WaitingForScanner')
win.flip()
event.waitKeys(keyList=params['triggerKey'])
tStartSession = globalClock.getTime()
AddToFlipTime(tStartSession)

# wait before first stimulus
fixation.draw()
win.logOnFlip(level=logging.EXP, msg='Display Fixation')
win.flip()
WaitForTrs(params['tStartup_TRs']) # wait for the given # of TRs


# =========================== #
# ===== MAIN EXPERIMENT ===== #
# =========================== #

# log experiment start and set up
logging.log(level=logging.EXP, msg='---START EXPERIMENT---')

# run main experiment loop
for iBlock in range(0,params['nBlocks']):
    
    # Run rest period
    print('Resting Block %d: duration=%.2f'%(iBlock, params['restDur_TRs']) )
    # Display fixation cross
    win.clearBuffer() # clear the screen
    fixation.draw() # draw the cross
    win.logOnFlip(level=logging.EXP, msg='Display Fixation')
    win.flip() # flip the window ASAP
    # do rest period
    WaitForTrs(params['restDur_TRs'])
        
    # display info to experimenter
    print('Tapping Block %d: stimDur=%.2f, ISI=%.2f'%(iBlock, params['stimDur'][iBlock], params['ISI'][iBlock]) )
    # display dot stim
    tBlock = FlashDot(stimDur=params['stimDur'][iBlock], ISI=params['ISI'][iBlock], blockDur_TRs=params['blockDur_TRs'])
    

# Log end of experiment
logging.log(level=logging.EXP, msg='--- END EXPERIMENT ---')

# ============================= #
# === CALCULATE PERFORMANCE === #
# ============================= #

# show user response times
#print('===Response times:===')
#print('Min RT = %.3f seconds'%(np.nanmin(rtVec)))
#print('Max RT = %.3f seconds'%(np.nanmax(rtVec)))
#print('Mean RT = %.3f seconds'%(np.nanmean(rtVec)))
#
# report the keys pressed
#print('===Keypresses:===')
#for iResp in range(0,len(params['respKeys'])):
#    print('Responded %s: %.1f%%'%(params['respKeys'][iResp],np.nanmean(iRespVec==iResp)*100))
#    
#print('Did not respond: %.1f%%'%(np.mean(np.isnan(iRespVec))*100))

# exit experiment
CoolDown()

