#!/usr/bin/env python2
"""
FaceGazeTask.py
Display images to the subject while collecting EyeLink eye tracking data.

* Created 10/30/18 by DJ based on ExtinctionRecallTask.py.
* Updated 11/8-9/18 by DJ - added new images, timing file reading code
* Updated 11/26/18 by DJ - comments and cleanup
* Updated 1/23/19 by DJ - added global escape key, modified print cmds and file reads to work in PschoPy3.
* Updated 1/24/19 by DJ - updated image files.
* Updated 1/25/19 by DJ - fixed over-logging during tracker setup
* Updated 2/5/19 by DJ - changed background color, fixCross pos, pre&post timing
* Updated 2/6/19 by DJ - made fix cross text instead of shapeStim (to make it thicker), fixed screenRes display in fullscreen mode
* Updated 3/18/18 by DJ - added ExperimentHandler to cleanly log trial data, param respKeys to specify which responses are allowed
"""

# Import packages
from psychopy import visual, core, gui, data, event, logging # sound
#from psychopy import parallel # for parallel port event triggers
from psychopy.tools.filetools import fromFile, toFile # saving and loading parameter files
import time as ts # for timing operations
import os # for file manipulation
import math # for rounding
#import AppKit # for monitor size detection (Mac only)
import BasicPromptTools # for loading/presenting prompts and questions
import random # for randomization of trials
import io # for reading files with specified newlines
# EyeLink packages
import pylink # for eye tracker interface
from EyeLinkCoreGraphicsPsychoPy import EyeLinkCoreGraphicsPsychoPy

# ====================== #
# ===== PARAMETERS ===== #
# ====================== #
# Save the parameters declared below?
saveParams = True;
newParamsFilename = 'FaceGazeParams.psydat'

# Declare primary task parameters.
params = {
# Declare EyeLink parameters
    'eyeSampleRate': 500,   # sampling rate of EyeLink (250, 500, 1000, or 2000)
    'eyeCalibType': 'HV9',  # EyeLink caibration type (H3, HV3, HV5, HV9, or HV13 (HV = horiztonal/vertical)),
# Declare experiment flow parameters
    'nTrialsPerRun': 45,    # number of trials in a block
    'nRunsPerSession': 2,   # number of runs in a session
# Declare timing parameters
    'tStartup': 9.2,        # time displaying fixation cross while waiting for scanner to reach steady-state
    'tCoolDown': 10.,       # time displaying fixation cross while waiting for scanner to stop
# Declare stimulus and response parameters
    'preppedKey': 'y',      # key from experimenter that says scanner is ready
    'triggerKey': '5',      # key from scanner that says scan is starting
    'respKeys': ['1','2','3','4','space'], # list of all keys the subject can press to respond (make sure this matches the prompts they see)
    'imageDir': 'Images/',  # directory containing image stimluli
    'imageNames': ['oAF01NEFL.png','oAF01NES.png','oAF05NEFR.png',
'oAF05NES.png','oAF09NEFL.png','oAF09NES.png',
'oAF20NEFR.png','oAF20NES.png','oAF32NEFL.png',
'oAF32NES.png','oAM08NEFR.png','oAM08NES.png',
'oAM21NEFL.png','oAM21NES.png','oAM23NEFR.png',
'oAM23NES.png','oAM28NEFL.png','oAM28NES.png',
'oAM31NEFR.png','oAM31NES.png','C1.png',
'C2.png','C3.png','C4.png',
'C5.png','C6.png','C7.png',
'C8.png','C9.png','C10.png'], # images will be selected randomly (without replacement) from this list of files in imageDir.
# declare prompt files
    'skipPrompts': False,     # go right to the scanner-wait page
    'promptFile': 'Prompts/PressSpacePrompts.txt', # Name of text file containing prompts
# declare timing files
    'timingFileDir': 'TimingFiles/',                             # where the AFNI timing text files sit
    'usedTimingFileList': 'TimingFiles/UsedTimingFiles.txt',     # subject number and timing file
    'unusedTimingFileList': 'TimingFiles/UnusedTimingFiles.txt', # timing files
# declare display parameters
    'fullScreen': True,         # run in full screen mode?
    'screenToShow': 0,          # display on primary screen (0) or secondary (1)?
    'screenRes': (0, 0),        # (1040,768),# display size in pixels (overridden by monitor resolution if fullScreen=True)
    'fixCrossSize': 0.3,        # size of "+" text displayed before each trial (in norm units, 1 = capital letters 1/2 screen height high)
    'fixCrossPos': (0,-0.5),    # (x,y) pos of fixation cross displayed before each stimulus (in norm units from center, for gaze drift correction)
    'screenColor':(0.7,0.7,0.7),# in rgb space: (r,g,b) all between -1 and 1
    'textColor': (-1,-1,-1),    # in rgb space: (r,g,b) all between -1 and 1
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
    if expInfo['run']==params['nRunsPerSession']:
        expInfo['subject'] = '' # empty
        expInfo['run'] = 1 # cycle back to 1
    else:
        expInfo['run'] +=1 # automatically increment session number
    expInfo['paramsFile'] = [expInfo['paramsFile'],'Load...']
except: # if not there then use a default set
    expInfo = {
        'subject':'1',
        'run': 1,
        'skipPrompts':False,
        'useEyeLink':False,
        'paramsFile':['DEFAULT','Load...']}
# overwrite params struct if you just saved a new parameter set
if saveParams:
    expInfo['paramsFile'] = [newParamsFilename,'Load...']

#present a dialogue to change select params
dlg = gui.DlgFromDict(expInfo, title=scriptName, order=['subject','run','skipPrompts','useEyeLink','paramsFile'])
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


# transfer experimental flow items from expInfo (gui input) to params (logged parameters)
for flowItem in ['skipPrompts']:
    params[flowItem] = expInfo[flowItem]


# print params to Output
print('params = {')
for key in sorted(params.keys()):
    print("   '%s': %s"%(key,params[key])) # print each value as-is (no quotes)
print('}')

# save experimental info
toFile('%s-lastExpInfo.psydat'%scriptName, expInfo)#save params to file for next time

# Start log file
dateStr = ts.strftime("%b_%d_%H%M", ts.localtime()) # add the current time
filename = 'Logs/%s-%s-%d-%s'%(scriptName,expInfo['subject'], expInfo['run'], dateStr) # log filename, no run param
outLog = logging.LogFile((filename+'.log'), level=logging.EXP)#, mode='w') # w=overwrite
logging.log(level=logging.INFO, msg='---START PARAMETERS---')
logging.log(level=logging.INFO, msg='filename: %s'%filename)
logging.log(level=logging.INFO, msg='subject: %s'%expInfo['subject'])
logging.log(level=logging.INFO, msg='run: %s'%expInfo['run'])
logging.log(level=logging.INFO, msg='date: %s'%dateStr)
logging.log(level=logging.INFO, msg='useEyeLink: %s'%expInfo['useEyeLink'])
# log everything in the params struct
for key in sorted(params.keys()): # in alphabetical order
    logging.log(level=logging.INFO, msg='%s: %s'%(key,params[key])) # log each parameter

logging.log(level=logging.INFO, msg='---END PARAMETERS---')

# Create an ExperimentHandler for simple trial data saving
thisExp = data.ExperimentHandler(name=scriptName, version='',
    extraInfo=expInfo, runtimeInfo=None,
    originPath= __file__,
    savePickle=False, saveWideText=True,
    dataFileName=filename)

# ========================== #
# ===== SET UP STIMULI ===== #
# ========================== #

# Initialize deadline for displaying next frame
tNextFlip = [0.0] # put in a list to make it mutable (weird quirk of python variables)

#create clocks and window
globalClock = core.Clock()#to keep track of time
trialClock = core.Clock()#to keep track of time
win = visual.Window(params['screenRes'], fullscr=params['fullScreen'], allowGUI=False, monitor='testMonitor', screen=params['screenToShow'], units='pix', name='win',color=params['screenColor'])

# update screen resolution
screenRes = (win.size[0]/2,win.size[1]/2)
scnWidth = screenRes[0]
scnHeight = screenRes[1]
print("Actual screenRes = [%d,%d]"%screenRes)

# create fixation cross
fixation = visual.TextStim(win, pos=params['fixCrossPos'], color=params['textColor'], alignHoriz='center', name='fixCross', text="+",height=params['fixCrossSize'],units='norm')

# create text stimuli
message1 = visual.TextStim(win, pos=[0,+.5], wrapWidth=1.5, color=params['textColor'], alignHoriz='center', name='topMsg', text="aaa",units='norm')
message2 = visual.TextStim(win, pos=[0,-.5], wrapWidth=1.5, color=params['textColor'], alignHoriz='center', name='bottomMsg', text="bbb",units='norm')
# read prompts from text file
[topPrompts,bottomPrompts] = BasicPromptTools.ParsePromptFile(params['promptFile'])
print('%d prompts loaded from %s'%(len(topPrompts),params['promptFile']))

# read in list of subjects/timing fiiles used
isSubjUsed = False
with io.open(params['usedTimingFileList']) as f:
    allLines = f.read().splitlines()

# check whether this subj has been used
for line in allLines:
    if line.startswith(expInfo['subject']):
        isSubjUsed = True
        timingFile = line.split()[-1]
        print('Subject %s found in %s! Reusing timing file %s.'%(expInfo['subject'],params['usedTimingFileList'],timingFile))
# if it hasn't been, find a timing file that hasn't been used
if not isSubjUsed:
    with io.open(params['unusedTimingFileList'], 'r') as fin:
        data = fin.read().splitlines()
    timingFile = data[0]
    print('Subject %s not yet used. Using timing file %s.'%(expInfo['subject'],timingFile))
    # add it to the used list
    print('Adding to %s.'%params['usedTimingFileList'])
    with io.open(params['usedTimingFileList'],'a') as f:
        f.write("%s %s\r\n"%(expInfo['subject'],timingFile))
    # remove it from the unused list
    print('Removing from %s.'%params['usedTimingFileList'])
    with io.open(params['unusedTimingFileList'], 'w') as fout:
        fout.write('\n'.join(data[1:]))

# read in stimulus timing file
# [conditions,stimDur,itis] = readTimingFile(timingFile)
conditions = []
stimDur = []
itis = []
with io.open(params['timingFileDir'] + timingFile,newline='\r\n') as f:
    allLines = f.read().splitlines()

for line in allLines:
    if line.startswith(' '):
        data = line.split()
        conditions = conditions + [int(data[0])]
        stimDur = stimDur + [float(data[3])]
        itis = itis + [float(data[4])]
print('%d conditions found in timing file. Parameters specified %d trials per run.'%(len(conditions),params['nTrialsPerRun']))

# get stimulus files
allNames = params['imageNames']; #copy image names for event marking
print('%d images specified in %s'%(len(allNames),params['imageDir']))
# make sure there are enough images. If not, duplicate them so that there are enough.
nTrials = params['nTrialsPerRun']*params['nRunsPerSession']
nRepetitions = math.ceil(float(nTrials)/len(allNames))
allNames = allNames * nRepetitions
print('Each image will be displayed %d times across %d runs.'%(nRepetitions,params['nRunsPerSession']))
# infer conditions from filenames
straightImages = [name for name in allNames if 'NES' in name] # straight-on view of face
sideImages = [name for name in allNames if 'NEF' in name] # side view of face
otherImages = [name for name in allNames if ('NES' not in name and 'NEF' not in name) ] # scrambled/control images
print('Found %d straight, %d side, and %d other images.'%(len(straightImages),len(sideImages),len(otherImages)))
# randomize image orders in ways that are distinct from each other but consistent for a subject/run combo
# i.e., use 3 different functions of (subject ID #) * (run #) as a seed
seed = int(expInfo['subject'])*expInfo['run']
random.Random(seed).shuffle(straightImages);
random.Random(seed^2).shuffle(sideImages);
random.Random(seed^3).shuffle(otherImages);
# assemble image list
iStraight = 0; iSide = 0; iOther = 0;
for i,cond in enumerate(conditions):
    if cond==0:
        allNames[i] = straightImages[iStraight]
        iStraight +=1;
    elif cond==1:
        allNames[i] = sideImages[iSide]
        iSide +=1;
    else:
        allNames[i] = otherImages[iOther]
        iOther +=1;

# initialize main image stimulus
imageFile = params['imageDir'] + allNames[0] # initialize with first image
stimImage = visual.ImageStim(win, pos=[0.,0.], name='ImageStimulus',image=imageFile, units='norm')
aspectRatio = stimImage.size[0]/stimImage.size[1]
stimImage.size = (2*aspectRatio,2) # stretch to height of screen, assume all images are same size


# ========================== #
# === SET UP EYE TRACKER === #
# ========================== #

# Establish connection to EyeLink tracker
if expInfo['useEyeLink']:
    tk = pylink.EyeLink('100.1.1.1')
else:
    print("EyeLink not used.")
    tk = pylink.EyeLink(None)


# Open an EDF data file EARLY
# Note that the file name cannot exceeds 8 characters
# please open eyelink data files early to record as much info as possible
dataFolder = os.getcwd() + '/edfData/'
if not os.path.exists(dataFolder): os.makedirs(dataFolder)
dataFileName = '%s_%d.EDF'%(expInfo['subject'],expInfo['run'])
tk.openDataFile(dataFileName)
# add personalized data file header (preamble text)
tk.sendCommand("add_file_preamble_text 'Face Gaze Psychopy Experiment'")

# call the custom calibration routine "EyeLinkCoreGraphicsPsychopy.py", instead of the default
# routines that were implemented in SDL
genv = EyeLinkCoreGraphicsPsychoPy(tk, win)
pylink.openGraphicsEx(genv)

# STEP V: Set up the tracker
# we need to put the tracker in offline mode before we change its configrations
tk.setOfflineMode()

# sampling rate, 250, 500, 1000, or 2000; this command won't work for EyeLInk II/I
tk.sendCommand('sample_rate %d'%params['eyeSampleRate'])

# inform the tracker the resolution of the subject display
# [see Eyelink Installation Guide, Section 8.4: Customizing Your PHYSICAL.INI Settings ]
tk.sendCommand("screen_pixel_coords = 0 0 %d %d" % (scnWidth-1, scnHeight-1))

# save display resolution in EDF data file for Data Viewer integration purposes
# [see Data Viewer User Manual, Section 7: Protocol for EyeLink Data to Viewer Integration]
tk.sendMessage("DISPLAY_COORDS = 0 0 %d %d" % (scnWidth-1, scnHeight-1))

# specify the calibration type, H3, HV3, HV5, HV13 (HV = horiztonal/vertical),
tk.sendCommand("calibration_type = %s"%params['eyeCalibType']) # tk.setCalibrationType('HV9') also works, see the Pylink manual

# specify the proportion of subject display to calibrate/validate (OPTIONAL, useful for wide screen monitors)
#tk.sendCommand("calibration_area_proportion 0.85 0.83")
#tk.sendCommand("validation_area_proportion  0.85 0.83")

# Using a button from the EyeLink Host PC gamepad to accept calibration/dirft check target (optional)
# tk.sendCommand("button_function 5 'accept_target_fixation'")

# the model of the tracker, 1-EyeLink I, 2-EyeLink II, 3-Newer models (100/1000Plus/DUO)
eyelinkVer = tk.getTrackerVersion()

#turn off scenelink camera stuff (EyeLink II/I only)
if eyelinkVer == 2: tk.sendCommand("scene_camera_gazemap = NO")

# Set the tracker to parse Events using "GAZE" (or "HREF") data
tk.sendCommand("recording_parse_type = GAZE")

# Online parser configuration: 0-> standard/coginitve, 1-> sensitive/psychophysiological
# the Parser for EyeLink I is more conservative, see below
# [see Eyelink User Manual, Section 4.3: EyeLink Parser Configuration]
if eyelinkVer>=2: tk.sendCommand('select_parser_configuration 0')

# get Host tracking software version
hostVer = 0
if eyelinkVer == 3:
    tvstr  = tk.getTrackerVersionString()
    vindex = tvstr.find("EYELINK CL")
    hostVer = int(float(tvstr[(vindex + len("EYELINK CL")):].strip()))

# specify the EVENT and SAMPLE data that are stored in EDF or retrievable from the Link
# See Section 4 Data Files of the EyeLink user manual
tk.sendCommand("file_event_filter = LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON,INPUT")
tk.sendCommand("link_event_filter = LEFT,RIGHT,FIXATION,FIXUPDATE,SACCADE,BLINK,BUTTON,INPUT")
if hostVer>=4:
    tk.sendCommand("file_sample_data  = LEFT,RIGHT,GAZE,AREA,GAZERES,STATUS,HTARGET,INPUT")
    tk.sendCommand("link_sample_data  = LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS,HTARGET,INPUT")
else:
    tk.sendCommand("file_sample_data  = LEFT,RIGHT,GAZE,AREA,GAZERES,STATUS,INPUT")
    tk.sendCommand("link_sample_data  = LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS,INPUT")



# ============================ #
# ======= SUBFUNCTIONS ======= #
# ============================ #

# increment time of next window flip
def AddToFlipTime(tIncrement=1.0):
    tNextFlip[0] += tIncrement

# flip window as soon as possible
def SetFlipTimeToNow():
    tNextFlip[0] = globalClock.getTime()
    
# Wait until it's time to update the window, logging responses as we go
def WaitForFlipTime():
    firstResp = ("","")
    while (globalClock.getTime()<tNextFlip[0]):
        keyList = event.getKeys(params['respKeys']+['q','escape'],timeStamped=globalClock)
        # Check for escape characters
        for key in keyList:
            # record first response
            if len(firstResp[0])==0:
                firstResp = key;
            if key[0] in ['q','escape']:
                CoolDown()
    # Return result
    return firstResp

# Send EyeLink event
def SendEyeEvent(eventText):
    logging.log(level=logging.EXP,msg="sent event '%s' to tracker"%(eventText))
    tk.sendMessage(eventText)

# Wait for scanner, then display a fixation cross
def WaitForScanner():
    # wait for experimenter
    message1.setText("Experimenter, is the scanner prepared?")
    message2.setText("(Press '%c' when it is.)"%params['preppedKey'].upper())
    message1.draw()
    message2.draw()
    win.logOnFlip(level=logging.EXP, msg='Display WaitingForPrep')
    win.callOnFlip(SendEyeEvent,'Display WaitingForPrep')
    win.flip()
    event.waitKeys(keyList=params['preppedKey'])

    # wait for scanner
    message1.setText("Waiting for scanner to start...")
    message2.setText("(Press '%c' to override.)"%params['triggerKey'].upper())
    message1.draw()
    message2.draw()
    win.logOnFlip(level=logging.EXP, msg='Display WaitingForScanner')
    win.callOnFlip(SendEyeEvent,'Display WaitingForScanner')
    win.flip()
    event.waitKeys(keyList=params['triggerKey'])
    # Update next stim time
    SetFlipTimeToNow()


# Display an image
def RunTrial(imageFile, stimDur=float('Inf'),imageCond=0,tIti=0):

    # send the standard "TRIALID" message to mark the start of a trial
    # [see Data Viewer User Manual, Section 7: Protocol for EyeLink Data to Viewer Integration]
    SendEyeEvent('TRIALID')

    # Draw image
    stimImage.setImage(imageFile)
    stimImage.draw()
    # log info
    msgTxt = 'Display %s cond=%d'%(imageFile,imageCond)
    win.logOnFlip(level=logging.EXP, msg=msgTxt)
    win.callOnFlip(SendEyeEvent,msgTxt)
    # Wait until it's time to display
    WaitForFlipTime()
    # flip window to display image
    win.flip()
    # log stim onset time/info
    thisExp.addData('image.tOnset',globalClock.getTime())
    # Update next stim time
    AddToFlipTime(stimDur) # add to tNextFlip[0]

    if tIti>0:
        # Display the fixation cross
        fixation.draw() # draw it
        win.logOnFlip(level=logging.EXP, msg='Display Fixation')
        win.callOnFlip(SendEyeEvent,'Display Fixation')        
    
    # Wait until it's time to display fixatin/blankscreen (and record first response)
    firstResp = WaitForFlipTime()
    win.flip()
    # log offset time and response
    thisExp.addData('image.tOffset',globalClock.getTime())
    thisExp.addData('response.key',firstResp[0])
    thisExp.addData('response.time', firstResp[1])
    AddToFlipTime(tIti)

# Handle end of a run
def CoolDown():
    
    # Save behavioral data
    thisExp.nextEntry() # advance data file
    thisExp.saveAsWideText(filename + '.csv')
    
    # stop recording eye data
    pylink.endRealTimeMode()
    pylink.pumpDelay(100)
    error = tk.stopRecording()
    
    # Clear the screen
    win.flip()
    
    # display cool-down message
    message1.setText("That's the end! ")
    message2.setText("Press 'q' or 'escape' to end the run.")
    win.logOnFlip(level=logging.EXP, msg='Display TheEnd')
    message1.draw()
    message2.draw()
    win.flip()
    
    # Wait for keypress
    thisKey = event.waitKeys(keyList=['q','escape'])

    # --- EyeLink code --- #
    # close the EDF data file
    tk.setOfflineMode()
    tk.closeDataFile()
    pylink.pumpDelay(50)

    # Get the EDF data and say goodbye
    message1.text='Data transfering.....'
    message1.draw()
    win.flip()
    tk.receiveDataFile(dataFileName, dataFolder + dataFileName)

    #close the link to the tracker
    tk.close()

    # close the graphics
    pylink.closeGraphics()
    # --- End EyeLink code --- #

    # exit
    win.close()
    core.quit()


# === SET UP GLOBAL ESCAPE KEY === #
event.globalKeys.clear()
event.globalKeys.add(key='q', modifiers=['ctrl'],func=CoolDown)

# =========================== #
# ====== RUN EXPERIMENT ===== #
# =========================== #

# log experiment start and set up
logging.log(level=logging.EXP, msg='---START EXPERIMENT---')

# RUN EYELINK CALIBRATION
# Show display for tracker setup
message1.text = 'Tracker setup: press C to calibrate, V to validate.'
message2.text = 'Press ESCAPE to skip.'
message1.draw()
message2.draw() # draw it
win.logOnFlip(level=logging.EXP, msg='Display TrackerSetup')
win.callOnFlip(SendEyeEvent,'Display TrackerSetup')
win.flip()

# set up the camera and calibrate the eye tracker at the beginning of each run
outLog.setLevel(logging.DATA)
logging.console.setLevel(logging.DATA)
tk.doTrackerSetup()
# set logging level back
outLog.setLevel(logging.INFO)
logging.console.setLevel(logging.INFO)

# START EYELINK RECORDING
# start recording, parameters specify whether events and samples are
# stored in file, and available over the link
error = tk.startRecording(1,1,1,1)
pylink.pumpDelay(100) # wait for 100 ms to make sure data of interest is recorded

# display prompts
if not params['skipPrompts']:
    BasicPromptTools.RunPrompts(topPrompts,bottomPrompts,win,message1,message2)

# wait for scanner
WaitForScanner() # includes SetFlipTimeToNow
tStart = tNextFlip[0] # record run start time

# Show fixation cross immediately
fixation.draw() # draw it
win.logOnFlip(level=logging.EXP, msg='Display Fixation')
win.callOnFlip(SendEyeEvent,'Display Fixation')
win.flip()

# Log state of experiment
logging.log(level=logging.EXP,msg='===== START RUN %d/%d ====='%(expInfo['run'],params['nRunsPerSession']))
AddToFlipTime(params['tStartup'])

# randomize order of images and names the same way
# ziplist = list(zip(allImages, allNames))
# random.shuffle(ziplist)
# allImages, allNames = zip(*ziplist)

# RUN TRIAL
for iTrial in range(params['nTrialsPerRun']):
    # get image, stim duration, and ITI index
    iImg = (expInfo['run']-1) * params['nTrialsPerRun'] + iTrial
#    tStim = params['tStim'];
    if iTrial < (params['nTrialsPerRun']-1):
        tIti = itis[iImg]
        # tIti = random.uniform(params['tItiMin'],params['tItiMax'])
    else: # last trial: no ITI
        tIti = params['tCoolDown']
        # tIti = 0;
    # Log trial info
    if iTrial>0:
        thisExp.nextEntry() # advance data file
    thisExp.addData('trial',iTrial+1)
    thisExp.addData('image.file',allNames[iImg])
    thisExp.addData('image.condition',conditions[iImg])
    # Display image and fixation
    RunTrial(imageFile=params['imageDir'] + allNames[iImg],stimDur=stimDur[iImg],imageCond=conditions[iImg],tIti=tIti)

# Wait until it's time to display
while (globalClock.getTime()<tNextFlip[0]):
    pass
logging.log(level=logging.EXP,msg='===== END RUN %d/%d ====='%(expInfo['run'],params['nRunsPerSession']))


# Log end of experiment
logging.log(level=logging.EXP, msg='--- END EXPERIMENT ---')

# exit experiment
CoolDown()
