#!/usr/bin/env python2
"""Display images from a specified folder and present them to the subject."""
# ExtinctioRecallAndVasTask.py
# Created 8/21/18 by DJ.
# Updated 8/29/18 by DJ - added parallel port triggers, opening prompt, baseline period 
# Updated 9/5/18 by DJ - commented out AppKit usage for PC compatibility, imported parallel package

# Import packages
from psychopy import visual, core, gui, data, event, logging # sound 
from psychopy import parallel # for parallel port event triggers
from psychopy.tools.filetools import fromFile, toFile # saving and loading parameter files
import time as ts, numpy as np # for timing and array operations
import os, glob # for file manipulation
#import AppKit # for monitor size detection (Mac only)
import BasicPromptTools # for loading/presenting prompts and questions
import random # for randomization of trials
import RatingScales # for VAS sliding scale

# ====================== #
# ===== PARAMETERS ===== #
# ====================== #
# Save the parameters declared below?
saveParams = True;
newParamsFilename = 'ExtinctionRecallParams.psydat'

# Declare primary task parameters.
params = {
# Declare experiment flow parameters
    'nTrialsPerBlock': 1,# 5,            # number of trials in a block
    'nBlocksPerGroup': 2,
    'nGroupsPerRun': 2,# 4,
    'nRunsPerSession': 2, 
# Declare timing parameters
    'tStartup': 3.,         # 16., #time displaying instructions while waiting for scanner to reach steady-state
    'tBaseline': 4.,        # 60., # pause time before starting first stimulus
    'tPreBlockPrompt': 2.,  # duration of prompt before each block
    'tStim': 1.,            # time when stimulus is presented (in seconds)
    'questionDur': 3.,      # duration of the VAS (in seconds)
    'tIsiMin': 1.,          # min time between when one stimulus disappears and the next appears (in seconds)
    'tIsiMax': 2.,          # max time between when one stimulus disappears and the next appears (in seconds)
# Declare stimulus and response parameters
    'preppedKey': 'y',         # key from experimenter that says scanner is ready
    'triggerKey': '5',        # key from scanner that says scan is starting
    'imageDir': 'Faces/',    # directory containing image stimluli
    'imageNames': ['R0_B100.bmp','R20_B80.bmp','R50_B50.bmp','R80_B20.bmp','R100_B0.bmp'],   # images will be selected randomly (without replacement) from this list of files in imageDir.
                  # Corresponding Port codes will be 1-len(imageNames) for versions 2 & 4, len(imageNames)-1 for versions 1 & 3 (to match increasig CSplus level). 
# declare prompt files
    'skipPrompts': False,     # go right to the scanner-wait page
    'promptFile': 'Prompts/ExtinctionRecallPrompts.txt', # Name of text file containing prompts 
# declare VAS info
    'questionFile': 'Questions/ExtinctionRecallVasQuestions.txt', # Name of text file containing Q&As
    'questionDownKey': '1',
    'questionUpKey':'2',
    'questionSelectKey':'3',
    'questionSelectAdvances': False,
# parallel port parameters
    'sendPortEvents': False, # send event markers to biopac computer via parallel port
    'portAddress': 0xD050, # 0x0378, # address of parallel port
    'codeBaseline': 9, # parallel port code for baseline period (make sure it's greater than len(imageNames)!)
# declare display parameters
    'fullScreen': True,       # run in full screen mode?
    'screenToShow': 0,        # display on primary screen (0) or secondary (1)?
    'fixCrossSize': 50,       # size of cross, in pixels
    'fixCrossPos': [0,0],     # (x,y) pos of fixation cross displayed before each stimulus (for gaze drift correction)
    'screenColor':(0,0,0),    # in rgb space: (r,g,b) all between -1 and 1
    'textColor': (-1,-1,-1),  # black
    'vasScreenColor': (0,0,0),  # gray
    'vasTextColor': (-1,-1,-1), # black
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
    expInfo['version'] = ['1','2','3','4']
    expInfo['paramsFile'] = [expInfo['paramsFile'],'Load...']
except: # if not there then use a default set
    expInfo = {
        'subject':'1', 
        'session': 1, 
        'version': ['1','2','3','4'], # group determining which stim is CS+
        'skipPrompts':False, 
        'sendPortEvents': True,
        'paramsFile':['DEFAULT','Load...']}
# overwrite params struct if you just saved a new parameter set
if saveParams:
    expInfo['paramsFile'] = [newParamsFilename,'Load...']

#present a dialogue to change select params
dlg = gui.DlgFromDict(expInfo, title=scriptName, order=['subject','session','version','skipPrompts','sendPortEvents','paramsFile'])
if not dlg.OK:
    core.quit() # the user hit cancel, so exit

# find parameter file
if expInfo['paramsFile'] == 'Load...':
    dlgResult = gui.fileOpenDlg(prompt='Select parameters file',tryFilePath=os.getcwd(),
        allowed="PSYDAT files (.psydat)|.psydat|All files (.*)|")
    expInfo['paramsFile'] = dlgResult[0]
# load parameter file
if expInfo['paramsFile'] not in ['DEFAULT', None]: # otherwise, just use defaults.
    # load params file
    params = fromFile(expInfo['paramsFile'])


# transfer experimental flow items from expInfo (gui input) to params (logged parameters)
for flowItem in ['skipPrompts','sendPortEvents']:
    params[flowItem] = expInfo[flowItem]


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
logging.log(level=logging.INFO, msg='version: %s'%expInfo['version'])
logging.log(level=logging.INFO, msg='date: %s'%dateStr)
# log everything in the params struct
for key in sorted(params.keys()): # in alphabetical order
    logging.log(level=logging.INFO, msg='%s: %s'%(key,params[key])) # log each parameter

logging.log(level=logging.INFO, msg='---END PARAMETERS---')


# ========================== #
# ===== GET SCREEN RES ===== #
# ========================== #

## kluge for secondary monitor
#if params['fullScreen']: 
#    screens = AppKit.NSScreen.screens()
#    screenRes = (int(screens[params['screenToShow']].frame().size.width), int(screens[params['screenToShow']].frame().size.height))
##    screenRes = [1920, 1200]
#    if params['screenToShow']>0:
#        params['fullScreen'] = False
#else:
#    screenRes = [800,600]

screenRes = (1280, 760) 
print "screenRes = [%d,%d]"%screenRes


# ========================== #
# == SET UP PARALLEL PORT == #
# ========================== #

if params['sendPortEvents']:
    port = parallel.ParallelPort(address=params['portAddress'])
    port.setData(0) # initialize to all zeros
else:
    print "Parallel port not used."
    

# ========================== #
# ===== SET UP STIMULI ===== #
# ========================== #

# Initialize deadline for displaying next frame
tNextFlip = [0.0] # put in a list to make it mutable (weird quirk of python variables) 

#create clocks and window
globalClock = core.Clock()#to keep track of time
trialClock = core.Clock()#to keep track of time
win = visual.Window(screenRes, fullscr=params['fullScreen'], allowGUI=False, monitor='testMonitor', screen=params['screenToShow'], units='deg', name='win',color=params['screenColor'])
# create fixation cross
fCS = params['fixCrossSize'] # size (for brevity)
fCP = params['fixCrossPos'] # position (for brevity)
lineWidth = int(params['fixCrossSize']/3)
fixation = visual.ShapeStim(win,lineColor=params['textColor'],lineWidth=lineWidth,vertices=((fCP[0]-fCS/2,fCP[1]),(fCP[0]+fCS/2,fCP[1]),(fCP[0],fCP[1]),(fCP[0],fCP[1]+fCS/2),(fCP[0],fCP[1]-fCS/2)),units='pix',closeShape=False,name='fixCross');
# create text stimuli
message1 = visual.TextStim(win, pos=[0,+.5], wrapWidth=1.5, color=params['textColor'], alignHoriz='center', name='topMsg', text="aaa",units='norm')
message2 = visual.TextStim(win, pos=[0,-.5], wrapWidth=1.5, color=params['textColor'], alignHoriz='center', name='bottomMsg', text="bbb",units='norm')

# get stimulus files
allImages = [params['imageDir'] + name for name in params['imageNames']] # assemble filenames: <imageDir>/<imageNames>.
# create corresponding names & codes
if expInfo['version'] in [2,4]:
    allCodes = range(1,len(allImages)+1)
    allNames = ['CSplus0','CSplus20','CSplus50','CSplus80','CSplus100']
else: # if it's version 1 or 3, reverse order
    allCodes = range(len(allImages),0,-1)
    allNames = ['CSplus100','CSplus80','CSplus50','CSplus20','CSplus0']
    
print('%d images loaded from %s'%(len(allImages),params['imageDir']))
# make sure there are enough images
if len(allImages)<params['nTrialsPerBlock']:
    raise ValueError("# images found in '%s' (%d) is less than # trials (%d)!"%(params['imageDir'],len(allImages),params['nTrials']))

# initialize main image stimulus
imageName = allImages[0] # initialize with first image
stimImage = visual.ImageStim(win, pos=[0.,0.4], name='ImageStimulus',image=imageName, units='norm')

# read prompts, questions and answers from text files
[topPrompts,bottomPrompts] = BasicPromptTools.ParsePromptFile(params['promptFile'])
print('%d prompts loaded from %s'%(len(topPrompts),params['promptFile']))
[questions,options,answers] = BasicPromptTools.ParseQuestionFile(params['questionFile'])
print('%d questions loaded from %s'%(len(questions),params['questionFile']))

# declare order of blocks for later randomization
blockOrder = range(params['nBlocksPerGroup'])


# ============================ #
# ======= SUBFUNCTIONS ======= #
# ============================ #

# increment time of next window flip
def AddToFlipTime(tIncrement=1.0):
    tNextFlip[0] += tIncrement

# flip window as soon as possible
def SetFlipTimeToNow():
    tNextFlip[0] = globalClock.getTime()

# Send parallel port event
def SetPortData(data):
    if params['sendPortEvents']:
        logging.log(level=logging.EXP,msg='set port %s to %d'%(format(params['portAddress'],'#04x'),data))
        port.setData(data)
    else:
        print('Port event: %d'%data)


# Wait for scanner, then display a fixation cross
def WaitForScanner():
    # wait for experimenter
    message1.setText("Experimenter, is the scanner prepared?")
    message2.setText("(Press '%c' when it is.)"%params['preppedKey'].upper())
    message1.draw()
    message2.draw()
    win.logOnFlip(level=logging.EXP, msg='Display WaitingForPrep')
    win.flip()
    event.waitKeys(keyList=params['preppedKey'])
    
    # wait for scanner
    message1.setText("Waiting for scanner to start...")
    message2.setText("(Press '%c' to override.)"%params['triggerKey'].upper())
    message1.draw()
    message2.draw()
    win.logOnFlip(level=logging.EXP, msg='Display WaitingForScanner')
    win.flip()
    event.waitKeys(keyList=params['triggerKey'])
    # Update next stim time
    SetFlipTimeToNow()


# Display the prompt before a block
def ShowPreBlockPrompt(question,iPrompt):
    # update messages and draw them
    message1.setText("In this block, when you see a face, answer:")
    message2.setText(question)
    message1.draw()
    message2.draw()
    # set up logging
    win.logOnFlip(level=logging.EXP, msg='Display PreBlockPrompt%d'%iPrompt)
    # wait until it's time
    while (globalClock.getTime()<tNextFlip[0]):
        pass
    # update display 
    win.flip()
    # Update next stim time
    AddToFlipTime(params['tPreBlockPrompt'])
    

# Display an image
def ShowImage(imageFile, stimDur=float('Inf'),imageName='image'):
    # display info to experimenter
    print('Showing Stimulus %s'%imageName) 
    
    # Draw image
    stimImage.setImage(imageFile)
    stimImage.draw()
    # Wait until it's time to display
    while (globalClock.getTime()<tNextFlip[0]):
        pass
    # log & flip window to display image
    win.logOnFlip(level=logging.EXP, msg='Display %s %s'%(imageFile,imageName))
    win.flip()
    # Update next stim time
    AddToFlipTime(stimDur) # add to tNextFlip[0]
    

# Run a set of visual analog scale (VAS) questions
def RunVas(questions,options):
    # Set screen color
    win.color = params['vasScreenColor']
    
    # wait until it's time
    while (globalClock.getTime()<tNextFlip[0]):
        pass
    
    # Show questions and options
    [rating,decisionTime,choiceHistory] = RatingScales.ShowVAS(questions,options,win, questionDur=params['questionDur'], \
        upKey=params['questionUpKey'],downKey=params['questionDownKey'],selectKey=params['questionSelectKey'],\
        isEndedByKeypress=params['questionSelectAdvances'],textColor=params['vasTextColor'],name='Vas',pos=(0.,-.4))
    
    # Update next stim time
    if params['questionSelectAdvances']:
        SetFlipTimeToNow() # no duration specified, so timing creep isn't an issue
    else:
        AddToFlipTime(params['questionDur']*len(questions)) # add question duration * # of questions
    
    # Set screen color back
    win.color = params['screenColor']
    win.flip() # flip so the color change 'takes' right away
    
    # Return VAS ratings
#    return (rating, decisionTime)


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

# log experiment start and set up
logging.log(level=logging.EXP, msg='---START EXPERIMENT---')

# =========================== #
# ========= RUN LOOP ======== #
# =========================== #

# RUN A RUN (SCAN)
for iRun in range(params['nRunsPerSession']):
    # wait for scanner
    WaitForScanner() # includes SetFlipTimeToNow
    # Log state of experiment
    logging.log(level=logging.EXP,msg='===== START RUN %d/%d ====='%(iRun+1,params['nRunsPerSession']))
    
    # Display instructions while waiting to reach steady state
    win.logOnFlip(level=logging.EXP, msg='Display RestInstructions')
    message1.text = 'For the next minute or so, stare at the cross and relax.'
    message1.draw()
    win.flip()
    AddToFlipTime(params['tStartup'])
    
    
    # display fixation before first stimulus
    fixation.draw()
    win.callOnFlip(SetPortData,data=params['codeBaseline'])
    win.logOnFlip(level=logging.EXP, msg='Display Fixation')
    # wait until it's time to show screen
    while (globalClock.getTime()<tNextFlip[0]):
        pass
    # show screen and update next flip time
    win.flip()
    AddToFlipTime(params['tBaseline'])
    
    
    # RUN GROUP OF BLOCKS
    for iGroup in range(params['nGroupsPerRun']):
        # Log state of experiment
        logging.log(level=logging.EXP,msg='==== START GROUP %d/%d ===='%(iGroup+1,params['nGroupsPerRun']))
        # randomize order of blocks
        random.shuffle(blockOrder)
        
        # RUN BLOCK
        for iBlock in range(params['nBlocksPerGroup']):
            # Log state of experiment
            logging.log(level=logging.EXP,msg='=== START BLOCK %d/%d ==='%(iBlock+1,params['nBlocksPerGroup']))
            
            # randomize order of images and codes the same way
            ziplist = list(zip(allImages, allCodes, allNames))
            random.shuffle(ziplist)
            allImages, allCodes, allNames = zip(*ziplist)
            
            # Display pre-block prompt
            ShowPreBlockPrompt(questions[blockOrder[iBlock]].upper(), blockOrder[iBlock])
            
            # RUN TRIAL
            for iTrial in range(params['nTrialsPerBlock']):
                # display image
                win.callOnFlip(SetPortData,data=allCodes[iTrial])
                ShowImage(imageFile=allImages[iTrial],stimDur=params['tStim'],imageName=allNames[iTrial])
                
                # Add image to VAS
                stimImage.autoDraw = True
                # Display VAS
                RunVas([questions[blockOrder[iBlock]]],[options[blockOrder[iBlock]]])
                # Remove image
                stimImage.autoDraw = False
                
                # get randomized ISI
                tIsi = random.uniform(params['tIsiMin'],params['tIsiMax'])
                # Display Fixation Cross (ISI)
                if iTrial < (params['nTrialsPerBlock']-1):
                    # Display the fixation cross
                    fixation.draw() # draw it
                    win.logOnFlip(level=logging.EXP, msg='Display Fixation')
                    # VAS keeps control to the end, so no need to wait for flip time
                    win.flip()
                    AddToFlipTime(tIsi)

# Log end of experiment
logging.log(level=logging.EXP, msg='--- END EXPERIMENT ---')

# exit experiment
CoolDown()
