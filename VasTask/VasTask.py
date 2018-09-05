#!/usr/bin/env python2
"""Display VAS ratings of mood."""
# VasTask.py
# Created 8/20/18 by DJ.
# Updated 8/22/18 by DJ - added vasStepSize param to control slider speed
# Updated 9/5/18 by DJ - removed AppKit calls, updated GUI filters (|-->;;), removed parallel import

from psychopy import visual # visual must be called first to prevent a bug where a movie won't appear.
from psychopy import core, gui, data, event, logging # experiment
from psychopy.tools.filetools import fromFile, toFile # saving and loading parameter files
import time as ts, numpy as np # for timing and array operations
import os # for monitor size detection, files
# import AppKit # for monitor size detection (on Macs only)
import BasicPromptTools # for loading/presenting prompts and questions
import RatingScales # for VAS sliding scale

# ====================== #
# ===== PARAMETERS ===== #
# ====================== #
# Save the parameters declared below?
saveParams = True; # SET THIS TO TRUE IF YOU WANT TO CHANGE PARAMETERS!
newParamsFilename = 'VasParams.psydat'

# Declare primary task parameters.
params = {
# declare VAS question files
    'questionFile': 'Questions/ScaryMovieVasQuestions.txt', # Name of text file containing Q&As
    'questionDownKey': '1',
    'questionUpKey':'2',
    'questionSelectKey':'3',
    'questionSelectAdvances': True,
    'questionDur': 999.0,
    'vasStepSize': 0.5, # how far the slider moves with a keypress (increase to move faster)
# declare display parameters
    'fullScreen': True,       # run in full screen mode?
    'screenToShow': 0,        # display on primary screen (0) or secondary (1)?
    'screenColor':(0,0,0), # gray #(-0.46667, -0.10588, 0.53725), # a neutral blue
    'textColor':(1,1,1) # white
}

# save parameters
if saveParams:
    dlgResult = gui.fileSaveDlg(prompt='Save Params...',initFilePath = os.getcwd() + '/Params', initFileName = newParamsFilename,
        allowed="PSYDAT files (*.psydat);;All files (*.*)")
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
    expInfo = fromFile('%s-lastExpInfo.psydat'%scriptName)
    expInfo['session'] +=1 # automatically increment session number
    expInfo['paramsFile'] = [expInfo['paramsFile'],'Load...']
except: # if not there then use a default set
    expInfo = {
        'subject':'1', 
        'session': 1, 
        'paramsFile':['DEFAULT','Load...']}
# overwrite params struct if you just saved a new parameter set
if saveParams:
    expInfo['paramsFile'] = [newParamsFilename,'Load...']

#present a dialogue to change select params
dlg = gui.DlgFromDict(expInfo, title=scriptName, order=['subject','session','paramsFile'])
if not dlg.OK:
    core.quit() # the user hit cancel, so exit

# find parameter file
if expInfo['paramsFile'] == 'Load...':
    dlgResult = gui.fileOpenDlg(prompt='Select parameters file',tryFilePath=os.getcwd(),
        allowed="PSYDAT files (*.psydat);;All files (*.*)")
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
toFile('%s-lastExpInfo.psydat'%scriptName, expInfo)#save params to file for next time

#make a log file to save parameter/event  data
dateStr = ts.strftime("%b_%d_%H%M", ts.localtime()) # add the current time
filename = 'Logs/%s-%s-%d-%s'%(scriptName,expInfo['subject'], expInfo['session'], dateStr) # log filename
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
#if params['fullScreen']: 
#    screens = AppKit.NSScreen.screens()
#    screenRes = (int(screens[params['screenToShow']].frame().size.width), int(screens[params['screenToShow']].frame().size.height))
##    screenRes = [1920, 1200]
#    if params['screenToShow']>0:
#        params['fullScreen'] = False
#else:
#    screenRes = [800,600]
screenRes = (1280,760)
print "screenRes = [%d,%d]"%screenRes



# ========================== #
# ===== SET UP STIMULI ===== #
# ========================== #
#from psychopy import visual

# Initialize deadline for displaying next frame
tNextFlip = [0.0] # put in a list to make it mutable (weird quirk of python variables) 

#create clocks and window
globalClock = core.Clock()#to keep track of time
trialClock = core.Clock()#to keep track of time
win = visual.Window(screenRes, fullscr=params['fullScreen'], allowGUI=False, monitor='testMonitor', screen=params['screenToShow'], units='deg', name='win',color=params['screenColor'])
# create text stimuli
message1 = visual.TextStim(win, pos=[0,+.5], wrapWidth=1.5, color=params['textColor'], alignHoriz='center', name='topMsg', text="aaa",units='norm')
message2 = visual.TextStim(win, pos=[0,-.5], wrapWidth=1.5, color=params['textColor'], alignHoriz='center', name='bottomMsg', text="bbb",units='norm')

# load VAS Qs & options
[questions,options,answers] = BasicPromptTools.ParseQuestionFile(params['questionFile'])
print('%d questions loaded from %s'%(len(questions),params['questionFile']))

# ============================ #
# ======= SUBFUNCTIONS ======= #
# ============================ #

# increment time of next window flip
def AddToFlipTime(tIncrement=1.0):
    tNextFlip[0] += tIncrement

# flip window as soon as possible
def SetFlipTimeToNow():
    tNextFlip[0] = globalClock.getTime()

def RunVas(questions,options):
    
    # Show questions and options
    [rating,decisionTime,choiceHistory] = RatingScales.ShowVAS(questions,options,win, questionDur=params['questionDur'], \
        upKey=params['questionUpKey'],downKey=params['questionDownKey'],selectKey=params['questionSelectKey'],\
        isEndedByKeypress=params['questionSelectAdvances'],textColor=params['textColor'],name='Vas',stepSize=params['vasStepSize'])
    
    # Print results
    print('===VAS Responses:===')
    for iQ in range(len(rating)):
        print('Scale #%d: %.1f'%(iQ,rating[iQ]))


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


# ==== MAIN EXPERIMENT ===== #

# Display VAS
RunVas(questions,options)

# exit experiment
CoolDown()
