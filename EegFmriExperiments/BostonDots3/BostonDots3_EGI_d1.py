#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This experiment was created using PsychoPy2 Experiment Builder (v1.90.1),
    on Tue May 15 12:05:58 2018
If you publish work using this script please cite the PsychoPy publications:
    Peirce, JW (2007) PsychoPy - Psychophysics software in Python.
        Journal of Neuroscience Methods, 162(1-2), 8-13.
    Peirce, JW (2009) Generating stimuli for neuroscience using PsychoPy.
        Frontiers in Neuroinformatics, 2:10. doi: 10.3389/neuro.11.010.2008
        
Updated 5/15/18 by DJ - adapted BostonDots3.py to add EGI calls.
"""

from __future__ import absolute_import, division
from psychopy import locale_setup, sound, gui, visual, core, data, event, logging, clock
from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,
                                STOPPED, FINISHED, PRESSED, RELEASED, FOREVER)
import numpy as np  # whole numpy lib is available, prepend 'np.'
from numpy import (sin, cos, tan, log, log10, pi, average,
                   sqrt, std, deg2rad, rad2deg, linspace, asarray)
from numpy.random import random, randint, normal, shuffle
import os  # handy system and path functions
import sys  # to get file system encoding
import egi.simple as egi #Net Station

# === EEG === #
# === Set up
isEegConnected = True #False #
tcpipAddress = '10.10.10.42'
tcpipPort = 55513

# === Initialize
if isEegConnected == False:
    # # This will import the debugging version of the PyNetStation module,
    # #  which will not actually attempt a connection but will check to make sure
    # #  your code is properly functioning.
    print('Starting FAKE EGI session for debugging...')
    import egi.fake as egi  # FOR TESTING WITHOUT CONNECTION TO NETSTATION COMPUTER
else:
    print('Starting EGI session...')
    # # This will import the single-threaded version of the PyNetStation module
    import egi.simple as egi # FOR RUNNING CONNECTED TO NETSTATION COMPUTER -- USE THIS IN A REAL EXPERIMENT

# === Timing Obj
# # Create a proper timing object to reference. To retrieve the time you want later,
# #  call this method using ms_localtime(), it returns the time in a millisecond format
# #  appropriate for the NetStation TCP/IP protocol.
# # This is only necessary if you are in need of direct contact with the clock object that NetStation is utilizing,
# #  which you don't actually need since it's working behind the scenes in the egi module.
# ms_localtime = egi.ms_localtime

# === Netstation Obj
# # Create the NetStation event-sending object. After this you can call
# #  the methods via the object instance, in this case 'ns'.
ns = egi.Netstation()

# === Establish Cxn
# # The next line is for connecting the actual, single-threaded module version to the computer.
if isEegConnected:
    ns.connect(tcpipAddress, tcpipPort)  # sample address and port -- change according to your network settings

# === Link Expt to Session
# # This sends some initialization info to NetStation for recording events.
ns.BeginSession()
# # This synchronizes the clocks of the stim computer and the NetStation computer.
ns.sync()

# === END EEG === #


# Ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__)).decode(sys.getfilesystemencoding())
os.chdir(_thisDir)

# Store info about the experiment session
expName = 'BostonDots3'  # from the Builder filename that created this script
expInfo = {'session': '001', 'participant': ''}
dlg = gui.DlgFromDict(dictionary=expInfo, title=expName)
if dlg.OK == False:
    core.quit()  # user pressed cancel
expInfo['date'] = data.getDateStr()  # add a simple timestamp
expInfo['expName'] = expName

# Data file name stem = absolute path + name; later add .psyexp, .csv, .log, etc
filename = _thisDir + os.sep + u'data/%s_%s_%s' % (expInfo['participant'], expName, expInfo['date'])

# An ExperimentHandler isn't essential but helps with data saving
thisExp = data.ExperimentHandler(name=expName, version='',
    extraInfo=expInfo, runtimeInfo=None,
    originPath=None,
    savePickle=True, saveWideText=True,
    dataFileName=filename)
# save a log file for detail verbose info
logFile = logging.LogFile(filename+'.log', level=logging.EXP)
logging.console.setLevel(logging.WARNING)  # this outputs to the screen, not a file

endExpNow = False  # flag for 'escape' or other condition => quit the exp

# Start Code - component code to be run before the window creation

# Setup the Window
win = visual.Window(
    size=(1024, 768), fullscr=True, screen=0,
    allowGUI=False, allowStencil=False,
    monitor='testMonitor', color=[0,0,0], colorSpace='rgb',
    blendMode='avg', useFBO=True)
# store frame rate of monitor if we can measure it
expInfo['frameRate'] = win.getActualFrameRate()
if expInfo['frameRate'] != None:
    frameDur = 1.0 / round(expInfo['frameRate'])
else:
    frameDur = 1.0 / 60.0  # could not measure, so guess

# Initialize components for Routine "welcome"
welcomeClock = core.Clock()
text = visual.TextStim(win=win, name='text',
    text='Welcome to the Boston Dots Task!\n\nWaiting for Scanner...',
    font='Arial',
    pos=(0, 0), height=0.1, wrapWidth=None, ori=0, 
    color='white', colorSpace='rgb', opacity=1,
    depth=0.0);

# Initialize components for Routine "instr1_solid"
instr1_solidClock = core.Clock()
text_2 = visual.TextStim(win=win, name='text_2',
    text='We are about to begin!\n\nIn this block, press the same\nside of the solid circle!\n\nWe will give you two examples.',
    font='Arial',
    pos=(0, 0), height=0.1, wrapWidth=None, ori=0, 
    color='white', colorSpace='rgb', opacity=1,
    depth=0.0);
ex1a = visual.ImageStim(
    win=win, name='ex1a',
    image='grey_left.bmp', mask=None,
    ori=0, pos=(0, 0), size=(0.5, 0.5),
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-1.0)
ex1_fix = visual.ImageStim(
    win=win, name='ex1_fix',
    image='fix.bmp', mask=None,
    ori=0, pos=(0, 0), size=(0.5, 0.5),
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-3.0)
ex1b = visual.ImageStim(
    win=win, name='ex1b',
    image='grey_right.bmp', mask=None,
    ori=0, pos=(0, 0), size=(0.5, 0.5),
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-4.0)
text_3 = visual.TextStim(win=win, name='text_3',
    text='Now we will begin the task.\n\nIn 3 seconds.',
    font='Arial',
    pos=(0, 0), height=0.1, wrapWidth=None, ori=0, 
    color='white', colorSpace='rgb', opacity=1,
    depth=-6.0);

# Initialize components for Routine "trial"
trialClock = core.Clock()
dotimage = visual.ImageStim(
    win=win, name='dotimage',
    image='sin', mask=None,
    ori=0, pos=(0, 0), size=(0.5, 0.5),
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=0.0)
fiximage = visual.ImageStim(
    win=win, name='fiximage',
    image='fix.bmp', mask=None,
    ori=0, pos=(0, 0), size=(0.5, 0.5),
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-2.0)

# Initialize components for Routine "instr2_striped"
instr2_stripedClock = core.Clock()
instr2_text1 = visual.TextStim(win=win, name='instr2_text1',
    text='You have completed one block!\n\nIn this next block, press the opposite\nside of the striped circle!\n\nWe will give you two examples.',
    font='Arial',
    pos=(0, 0), height=0.1, wrapWidth=None, ori=0, 
    color='white', colorSpace='rgb', opacity=1,
    depth=0.0);
ex_2_1 = visual.ImageStim(
    win=win, name='ex_2_1',
    image='str_left.bmp', mask=None,
    ori=0, pos=(0, 0), size=(0.5, 0.5),
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-1.0)
ex2_fix = visual.ImageStim(
    win=win, name='ex2_fix',
    image='fix.bmp', mask=None,
    ori=0, pos=(0, 0), size=(0.5, 0.5),
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-3.0)
ex_2_2 = visual.ImageStim(
    win=win, name='ex_2_2',
    image='str_right.bmp', mask=None,
    ori=0, pos=(0, 0), size=(0.5, 0.5),
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-4.0)
text_4 = visual.TextStim(win=win, name='text_4',
    text='Now we will return to the task.\n\nIn 3 seconds.',
    font='Arial',
    pos=(0, 0), height=0.1, wrapWidth=None, ori=0, 
    color='white', colorSpace='rgb', opacity=1,
    depth=-6.0);

# Initialize components for Routine "trial"
trialClock = core.Clock()
dotimage = visual.ImageStim(
    win=win, name='dotimage',
    image='sin', mask=None,
    ori=0, pos=(0, 0), size=(0.5, 0.5),
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=0.0)
fiximage = visual.ImageStim(
    win=win, name='fiximage',
    image='fix.bmp', mask=None,
    ori=0, pos=(0, 0), size=(0.5, 0.5),
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-2.0)

# Initialize components for Routine "instr3_mixed"
instr3_mixedClock = core.Clock()
text_5 = visual.TextStim(win=win, name='text_5',
    text='You have completed two blocks!\n\nIn this next block, we will mix\nthe two conditions!  \n\nWe will begin in 3 seconds',
    font='Arial',
    pos=(0, 0), height=0.1, wrapWidth=None, ori=0, 
    color='white', colorSpace='rgb', opacity=1,
    depth=0.0);

# Initialize components for Routine "trial"
trialClock = core.Clock()
dotimage = visual.ImageStim(
    win=win, name='dotimage',
    image='sin', mask=None,
    ori=0, pos=(0, 0), size=(0.5, 0.5),
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=0.0)
fiximage = visual.ImageStim(
    win=win, name='fiximage',
    image='fix.bmp', mask=None,
    ori=0, pos=(0, 0), size=(0.5, 0.5),
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-2.0)

# Initialize components for Routine "goodbye"
goodbyeClock = core.Clock()
text_6 = visual.TextStim(win=win, name='text_6',
    text="You've completed the task!",
    font='Arial',
    pos=(0, 0), height=0.1, wrapWidth=None, ori=0, 
    color='white', colorSpace='rgb', opacity=1,
    depth=0.0);

# Create some handy timers
globalClock = core.Clock()  # to track the time since experiment started
routineTimer = core.CountdownTimer()  # to track time remaining of each (non-slip) routine 


# === EEG === #
# # This starts the recording in NetStation acquisition. Equivalent to pressing the Record button.
# # If at some point you pause the experiment using the "StopRecording()" method,
# #  just call this method again to restart the recording.
ns.StartRecording()

# === END EEG === #



# ------Prepare to start Routine "welcome"-------
t = 0
welcomeClock.reset()  # clock
frameN = -1
continueRoutine = True
# update component parameters for each repeat
startResp1 = event.BuilderKeyResponse()
# keep track of which components have finished
welcomeComponents = [text, startResp1]
for thisComponent in welcomeComponents:
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED


# === EEG === #
# # This re-aligns the clocks between the stim computer and the NetStation computer.
# # Best to put at the start of each trial for maximal timing accuracy.
ns.sync()
# Send Message to EEG
win.callOnFlip(ns.send_event, key='WELC', timestamp=None, label="Welcome", description="Welcome Participant", pad=False)

# === END EEG === #


# -------Start Routine "welcome"-------
while continueRoutine:
    # get current time
    t = welcomeClock.getTime()
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame
    
    # *text* updates
    if t >= 0.0 and text.status == NOT_STARTED:
        # keep track of start time/frame for later
        text.tStart = t
        text.frameNStart = frameN  # exact frame index
        text.setAutoDraw(True)
    
    # *startResp1* updates
    if t >= 0.0 and startResp1.status == NOT_STARTED:
        # keep track of start time/frame for later
        startResp1.tStart = t
        startResp1.frameNStart = frameN  # exact frame index
        startResp1.status = STARTED
        # keyboard checking is just starting
        win.callOnFlip(startResp1.clock.reset)  # t=0 on next screen flip
        event.clearEvents(eventType='keyboard')
    if startResp1.status == STARTED:
        theseKeys = event.getKeys(keyList=['t'])
        
        # check for quit:
        if "escape" in theseKeys:
            endExpNow = True
        if len(theseKeys) > 0:  # at least one key was pressed
            startResp1.keys = theseKeys[-1]  # just the last key pressed
            startResp1.rt = startResp1.clock.getTime()
            # a response ends the routine
            continueRoutine = False
    
    # check if all components have finished
    if not continueRoutine:  # a component has requested a forced-end of Routine
        break
    continueRoutine = False  # will revert to True if at least one component still running
    for thisComponent in welcomeComponents:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished
    
    # check for quit (the Esc key)
    if endExpNow or event.getKeys(keyList=["escape"]):
        core.quit()
    
    # refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()

# -------Ending Routine "welcome"-------
for thisComponent in welcomeComponents:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)
# check responses
if startResp1.keys in ['', [], None]:  # No response was made
    startResp1.keys=None
thisExp.addData('startResp1.keys',startResp1.keys)
if startResp1.keys != None:  # we had a response
    thisExp.addData('startResp1.rt', startResp1.rt)
thisExp.nextEntry()
# the Routine "welcome" was not non-slip safe, so reset the non-slip timer
routineTimer.reset()

# ------Prepare to start Routine "instr1_solid"-------
t = 0
instr1_solidClock.reset()  # clock
frameN = -1
continueRoutine = True
routineTimer.add(12.500000)
# update component parameters for each repeat
key_resp_3 = event.BuilderKeyResponse()
key_resp_4 = event.BuilderKeyResponse()
# keep track of which components have finished
instr1_solidComponents = [text_2, ex1a, key_resp_3, ex1_fix, ex1b, key_resp_4, text_3]
for thisComponent in instr1_solidComponents:
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED

# === EEG === #
# # This re-aligns the clocks between the stim computer and the NetStation computer.
# # Best to put at the start of each trial for maximal timing accuracy.
ns.sync()
# Send Message to EEG
win.callOnFlip(ns.send_event, key='INS1', timestamp=None, label="Instructions1", description="Instructions #1 (solid)", pad=False)

# === END EEG === #

# -------Start Routine "instr1_solid"-------
while continueRoutine and routineTimer.getTime() > 0:
    # get current time
    t = instr1_solidClock.getTime()
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame
    
    # *text_2* updates
    if t >= 0.0 and text_2.status == NOT_STARTED:
        # keep track of start time/frame for later
        text_2.tStart = t
        text_2.frameNStart = frameN  # exact frame index
        text_2.setAutoDraw(True)
    frameRemains = 0.0 + 4.0- win.monitorFramePeriod * 0.75  # most of one frame period left
    if text_2.status == STARTED and t >= frameRemains:
        text_2.setAutoDraw(False)
    
    # *ex1a* updates
    if t >= 4.0 and ex1a.status == NOT_STARTED:
        # keep track of start time/frame for later
        ex1a.tStart = t
        ex1a.frameNStart = frameN  # exact frame index
        ex1a.setAutoDraw(True)
    frameRemains = 4.0 + 2.0- win.monitorFramePeriod * 0.75  # most of one frame period left
    if ex1a.status == STARTED and t >= frameRemains:
        ex1a.setAutoDraw(False)
    
    # *key_resp_3* updates
    if t >= 4.0 and key_resp_3.status == NOT_STARTED:
        # keep track of start time/frame for later
        key_resp_3.tStart = t
        key_resp_3.frameNStart = frameN  # exact frame index
        key_resp_3.status = STARTED
        # keyboard checking is just starting
        win.callOnFlip(key_resp_3.clock.reset)  # t=0 on next screen flip
        event.clearEvents(eventType='keyboard')
    frameRemains = 4.0 + 2- win.monitorFramePeriod * 0.75  # most of one frame period left
    if key_resp_3.status == STARTED and t >= frameRemains:
        key_resp_3.status = STOPPED
    if key_resp_3.status == STARTED:
        theseKeys = event.getKeys(keyList=['g', 'b', '1', '2'])
        
        # check for quit:
        if "escape" in theseKeys:
            endExpNow = True
        if len(theseKeys) > 0:  # at least one key was pressed
            key_resp_3.keys = theseKeys[-1]  # just the last key pressed
            key_resp_3.rt = key_resp_3.clock.getTime()
            # was this 'correct'?
            if (key_resp_3.keys == str("'g'")) or (key_resp_3.keys == "'g'"):
                key_resp_3.corr = 1
            else:
                key_resp_3.corr = 0
    
    # *ex1_fix* updates
    if t >= 6.0 and ex1_fix.status == NOT_STARTED:
        # keep track of start time/frame for later
        ex1_fix.tStart = t
        ex1_fix.frameNStart = frameN  # exact frame index
        ex1_fix.setAutoDraw(True)
    frameRemains = 6.0 + 1.0- win.monitorFramePeriod * 0.75  # most of one frame period left
    if ex1_fix.status == STARTED and t >= frameRemains:
        ex1_fix.setAutoDraw(False)
    
    # *ex1b* updates
    if t >= 7.0 and ex1b.status == NOT_STARTED:
        # keep track of start time/frame for later
        ex1b.tStart = t
        ex1b.frameNStart = frameN  # exact frame index
        ex1b.setAutoDraw(True)
    frameRemains = 7.0 + 2.0- win.monitorFramePeriod * 0.75  # most of one frame period left
    if ex1b.status == STARTED and t >= frameRemains:
        ex1b.setAutoDraw(False)
    
    # *key_resp_4* updates
    if t >= 7.0 and key_resp_4.status == NOT_STARTED:
        # keep track of start time/frame for later
        key_resp_4.tStart = t
        key_resp_4.frameNStart = frameN  # exact frame index
        key_resp_4.status = STARTED
        # keyboard checking is just starting
        win.callOnFlip(key_resp_4.clock.reset)  # t=0 on next screen flip
        event.clearEvents(eventType='keyboard')
    frameRemains = 7.0 + 2- win.monitorFramePeriod * 0.75  # most of one frame period left
    if key_resp_4.status == STARTED and t >= frameRemains:
        key_resp_4.status = STOPPED
    if key_resp_4.status == STARTED:
        theseKeys = event.getKeys(keyList=['b', 'g', '1', '2'])
        
        # check for quit:
        if "escape" in theseKeys:
            endExpNow = True
        if len(theseKeys) > 0:  # at least one key was pressed
            key_resp_4.keys = theseKeys[-1]  # just the last key pressed
            key_resp_4.rt = key_resp_4.clock.getTime()
            # was this 'correct'?
            if (key_resp_4.keys == str("'b'")) or (key_resp_4.keys == "'b'"):
                key_resp_4.corr = 1
            else:
                key_resp_4.corr = 0
    
    # *text_3* updates
    if t >= 9.5 and text_3.status == NOT_STARTED:
        # keep track of start time/frame for later
        text_3.tStart = t
        text_3.frameNStart = frameN  # exact frame index
        text_3.setAutoDraw(True)
    frameRemains = 9.5 + 3.0- win.monitorFramePeriod * 0.75  # most of one frame period left
    if text_3.status == STARTED and t >= frameRemains:
        text_3.setAutoDraw(False)
    
    # check if all components have finished
    if not continueRoutine:  # a component has requested a forced-end of Routine
        break
    continueRoutine = False  # will revert to True if at least one component still running
    for thisComponent in instr1_solidComponents:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished
    
    # check for quit (the Esc key)
    if endExpNow or event.getKeys(keyList=["escape"]):
        core.quit()
    
    # refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()

# -------Ending Routine "instr1_solid"-------
for thisComponent in instr1_solidComponents:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)
# check responses
if key_resp_3.keys in ['', [], None]:  # No response was made
    key_resp_3.keys=None
    # was no response the correct answer?!
    if str("'g'").lower() == 'none':
       key_resp_3.corr = 1  # correct non-response
    else:
       key_resp_3.corr = 0  # failed to respond (incorrectly)
# store data for thisExp (ExperimentHandler)
thisExp.addData('key_resp_3.keys',key_resp_3.keys)
thisExp.addData('key_resp_3.corr', key_resp_3.corr)
if key_resp_3.keys != None:  # we had a response
    thisExp.addData('key_resp_3.rt', key_resp_3.rt)
thisExp.nextEntry()
# check responses
if key_resp_4.keys in ['', [], None]:  # No response was made
    key_resp_4.keys=None
    # was no response the correct answer?!
    if str("'b'").lower() == 'none':
       key_resp_4.corr = 1  # correct non-response
    else:
       key_resp_4.corr = 0  # failed to respond (incorrectly)
# store data for thisExp (ExperimentHandler)
thisExp.addData('key_resp_4.keys',key_resp_4.keys)
thisExp.addData('key_resp_4.corr', key_resp_4.corr)
if key_resp_4.keys != None:  # we had a response
    thisExp.addData('key_resp_4.rt', key_resp_4.rt)
thisExp.nextEntry()

# set up handler to look after randomisation of conditions etc
trials = data.TrialHandler(nReps=2, method='sequential', 
    extraInfo=expInfo, originPath=-1,
    trialList=data.importConditions('block1_solid.xlsx'),
    seed=None, name='trials')
thisExp.addLoop(trials)  # add the loop to the experiment
thisTrial = trials.trialList[0]  # so we can initialise stimuli with some values
# abbreviate parameter names if possible (e.g. rgb = thisTrial.rgb)
if thisTrial != None:
    for paramName in thisTrial:
        exec('{} = thisTrial[paramName]'.format(paramName))

for thisTrial in trials:
    currentLoop = trials
    # abbreviate parameter names if possible (e.g. rgb = thisTrial.rgb)
    if thisTrial != None:
        for paramName in thisTrial:
            exec('{} = thisTrial[paramName]'.format(paramName))
    
    # ------Prepare to start Routine "trial"-------
    t = 0
    trialClock.reset()  # clock
    frameN = -1
    continueRoutine = True
    routineTimer.add(2.500000)
    # update component parameters for each repeat
    dotimage.setImage(image)
    key_resp_2 = event.BuilderKeyResponse()
    # keep track of which components have finished
    trialComponents = [dotimage, key_resp_2, fiximage]
    for thisComponent in trialComponents:
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    
    # -------Start Routine "trial"-------
    while continueRoutine and routineTimer.getTime() > 0:
        # get current time
        t = trialClock.getTime()
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *dotimage* updates
        if t >= 1 and dotimage.status == NOT_STARTED:
            # keep track of start time/frame for later
            dotimage.tStart = t
            dotimage.frameNStart = frameN  # exact frame index
            dotimage.setAutoDraw(True)
            
            # === EEG === #
            # # This re-aligns the clocks between the stim computer and the NetStation computer.
            # # Best to put at the start of each trial for maximal timing accuracy.
            ns.sync()
            # Send Message to EEG
            nstag = str(nstag)
            win.callOnFlip(ns.send_event, key=nstag, timestamp=None, label="Trial_%s"%nstag, description="Start trial (type %s)"%nstag, pad=False)
            # === END EEG === #

            
        frameRemains = 1 + 1.5- win.monitorFramePeriod * 0.75  # most of one frame period left
        if dotimage.status == STARTED and t >= frameRemains:
            dotimage.setAutoDraw(False)
        
        # *key_resp_2* updates
        if t >= 1 and key_resp_2.status == NOT_STARTED:
            # keep track of start time/frame for later
            key_resp_2.tStart = t
            key_resp_2.frameNStart = frameN  # exact frame index
            key_resp_2.status = STARTED
            # keyboard checking is just starting
            win.callOnFlip(key_resp_2.clock.reset)  # t=0 on next screen flip
            event.clearEvents(eventType='keyboard')
        frameRemains = 1 + 1.5- win.monitorFramePeriod * 0.75  # most of one frame period left
        if key_resp_2.status == STARTED and t >= frameRemains:
            key_resp_2.status = STOPPED
        if key_resp_2.status == STARTED:
            theseKeys = event.getKeys(keyList=['g', 'b', '1', '2'])
            
            # check for quit:
            if "escape" in theseKeys:
                endExpNow = True
            if len(theseKeys) > 0:  # at least one key was pressed
                key_resp_2.keys = theseKeys[-1]  # just the last key pressed
                key_resp_2.rt = key_resp_2.clock.getTime()
                # was this 'correct'?
                if (key_resp_2.keys == str(corrAns)) or (key_resp_2.keys == corrAns):
                    key_resp_2.corr = 1
                else:
                    key_resp_2.corr = 0
        
        # *fiximage* updates
        if t >= .50 and fiximage.status == NOT_STARTED:
            # keep track of start time/frame for later
            fiximage.tStart = t
            fiximage.frameNStart = frameN  # exact frame index
            fiximage.setAutoDraw(True)
        frameRemains = .50 + .5- win.monitorFramePeriod * 0.75  # most of one frame period left
        if fiximage.status == STARTED and t >= frameRemains:
            fiximage.setAutoDraw(False)
        
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in trialComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # check for quit (the Esc key)
        if endExpNow or event.getKeys(keyList=["escape"]):
            core.quit()
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    # -------Ending Routine "trial"-------
    for thisComponent in trialComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    # check responses
    if key_resp_2.keys in ['', [], None]:  # No response was made
        key_resp_2.keys=None
        # was no response the correct answer?!
        if str(corrAns).lower() == 'none':
           key_resp_2.corr = 1  # correct non-response
        else:
           key_resp_2.corr = 0  # failed to respond (incorrectly)
    # store data for trials (TrialHandler)
    trials.addData('key_resp_2.keys',key_resp_2.keys)
    trials.addData('key_resp_2.corr', key_resp_2.corr)
    if key_resp_2.keys != None:  # we had a response
        trials.addData('key_resp_2.rt', key_resp_2.rt)
    thisExp.nextEntry()
    
# completed 2 repeats of 'trials'


# ------Prepare to start Routine "instr2_striped"-------
t = 0
instr2_stripedClock.reset()  # clock
frameN = -1
continueRoutine = True
routineTimer.add(12.500000)
# update component parameters for each repeat
ex_2_1_keyb = event.BuilderKeyResponse()
ex_2_2_keyb = event.BuilderKeyResponse()
# keep track of which components have finished
instr2_stripedComponents = [instr2_text1, ex_2_1, ex_2_1_keyb, ex2_fix, ex_2_2, ex_2_2_keyb, text_4]
for thisComponent in instr2_stripedComponents:
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED

# === EEG === #
# # This re-aligns the clocks between the stim computer and the NetStation computer.
# # Best to put at the start of each trial for maximal timing accuracy.
ns.sync()
# Send Message to EEG
win.callOnFlip(ns.send_event, key='INS2', timestamp=None, label="Instructions2", description="Instructions #2 (striped)", pad=False)

# === END EEG === #

# -------Start Routine "instr2_striped"-------
while continueRoutine and routineTimer.getTime() > 0:
    # get current time
    t = instr2_stripedClock.getTime()
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame
    
    # *instr2_text1* updates
    if t >= 0.0 and instr2_text1.status == NOT_STARTED:
        # keep track of start time/frame for later
        instr2_text1.tStart = t
        instr2_text1.frameNStart = frameN  # exact frame index
        instr2_text1.setAutoDraw(True)
    frameRemains = 0.0 + 4- win.monitorFramePeriod * 0.75  # most of one frame period left
    if instr2_text1.status == STARTED and t >= frameRemains:
        instr2_text1.setAutoDraw(False)
    
    # *ex_2_1* updates
    if t >= 4.0 and ex_2_1.status == NOT_STARTED:
        # keep track of start time/frame for later
        ex_2_1.tStart = t
        ex_2_1.frameNStart = frameN  # exact frame index
        ex_2_1.setAutoDraw(True)
    frameRemains = 4.0 + 2.0- win.monitorFramePeriod * 0.75  # most of one frame period left
    if ex_2_1.status == STARTED and t >= frameRemains:
        ex_2_1.setAutoDraw(False)
    
    # *ex_2_1_keyb* updates
    if t >= 4.0 and ex_2_1_keyb.status == NOT_STARTED:
        # keep track of start time/frame for later
        ex_2_1_keyb.tStart = t
        ex_2_1_keyb.frameNStart = frameN  # exact frame index
        ex_2_1_keyb.status = STARTED
        # keyboard checking is just starting
        win.callOnFlip(ex_2_1_keyb.clock.reset)  # t=0 on next screen flip
        event.clearEvents(eventType='keyboard')
    frameRemains = 4.0 + 2- win.monitorFramePeriod * 0.75  # most of one frame period left
    if ex_2_1_keyb.status == STARTED and t >= frameRemains:
        ex_2_1_keyb.status = STOPPED
    if ex_2_1_keyb.status == STARTED:
        theseKeys = event.getKeys(keyList=['g', 'b', '1', '2'])
        
        # check for quit:
        if "escape" in theseKeys:
            endExpNow = True
        if len(theseKeys) > 0:  # at least one key was pressed
            ex_2_1_keyb.keys = theseKeys[-1]  # just the last key pressed
            ex_2_1_keyb.rt = ex_2_1_keyb.clock.getTime()
            # was this 'correct'?
            if (ex_2_1_keyb.keys == str("'b'")) or (ex_2_1_keyb.keys == "'b'"):
                ex_2_1_keyb.corr = 1
            else:
                ex_2_1_keyb.corr = 0
    
    # *ex2_fix* updates
    if t >= 6.0 and ex2_fix.status == NOT_STARTED:
        # keep track of start time/frame for later
        ex2_fix.tStart = t
        ex2_fix.frameNStart = frameN  # exact frame index
        ex2_fix.setAutoDraw(True)
    frameRemains = 6.0 + 1.0- win.monitorFramePeriod * 0.75  # most of one frame period left
    if ex2_fix.status == STARTED and t >= frameRemains:
        ex2_fix.setAutoDraw(False)
    
    # *ex_2_2* updates
    if t >= 7.0 and ex_2_2.status == NOT_STARTED:
        # keep track of start time/frame for later
        ex_2_2.tStart = t
        ex_2_2.frameNStart = frameN  # exact frame index
        ex_2_2.setAutoDraw(True)
    frameRemains = 7.0 + 2.0- win.monitorFramePeriod * 0.75  # most of one frame period left
    if ex_2_2.status == STARTED and t >= frameRemains:
        ex_2_2.setAutoDraw(False)
    
    # *ex_2_2_keyb* updates
    if t >= 7.0 and ex_2_2_keyb.status == NOT_STARTED:
        # keep track of start time/frame for later
        ex_2_2_keyb.tStart = t
        ex_2_2_keyb.frameNStart = frameN  # exact frame index
        ex_2_2_keyb.status = STARTED
        # keyboard checking is just starting
        win.callOnFlip(ex_2_2_keyb.clock.reset)  # t=0 on next screen flip
        event.clearEvents(eventType='keyboard')
    frameRemains = 7.0 + 2- win.monitorFramePeriod * 0.75  # most of one frame period left
    if ex_2_2_keyb.status == STARTED and t >= frameRemains:
        ex_2_2_keyb.status = STOPPED
    if ex_2_2_keyb.status == STARTED:
        theseKeys = event.getKeys(keyList=['b', 'g', '1', '2'])
        
        # check for quit:
        if "escape" in theseKeys:
            endExpNow = True
        if len(theseKeys) > 0:  # at least one key was pressed
            ex_2_2_keyb.keys = theseKeys[-1]  # just the last key pressed
            ex_2_2_keyb.rt = ex_2_2_keyb.clock.getTime()
            # was this 'correct'?
            if (ex_2_2_keyb.keys == str("'g'")) or (ex_2_2_keyb.keys == "'g'"):
                ex_2_2_keyb.corr = 1
            else:
                ex_2_2_keyb.corr = 0
    
    # *text_4* updates
    if t >= 9.5 and text_4.status == NOT_STARTED:
        # keep track of start time/frame for later
        text_4.tStart = t
        text_4.frameNStart = frameN  # exact frame index
        text_4.setAutoDraw(True)
    frameRemains = 9.5 + 3.0- win.monitorFramePeriod * 0.75  # most of one frame period left
    if text_4.status == STARTED and t >= frameRemains:
        text_4.setAutoDraw(False)
    
    # check if all components have finished
    if not continueRoutine:  # a component has requested a forced-end of Routine
        break
    continueRoutine = False  # will revert to True if at least one component still running
    for thisComponent in instr2_stripedComponents:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished
    
    # check for quit (the Esc key)
    if endExpNow or event.getKeys(keyList=["escape"]):
        core.quit()
    
    # refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()

# -------Ending Routine "instr2_striped"-------
for thisComponent in instr2_stripedComponents:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)
# check responses
if ex_2_1_keyb.keys in ['', [], None]:  # No response was made
    ex_2_1_keyb.keys=None
    # was no response the correct answer?!
    if str("'b'").lower() == 'none':
       ex_2_1_keyb.corr = 1  # correct non-response
    else:
       ex_2_1_keyb.corr = 0  # failed to respond (incorrectly)
# store data for thisExp (ExperimentHandler)
thisExp.addData('ex_2_1_keyb.keys',ex_2_1_keyb.keys)
thisExp.addData('ex_2_1_keyb.corr', ex_2_1_keyb.corr)
if ex_2_1_keyb.keys != None:  # we had a response
    thisExp.addData('ex_2_1_keyb.rt', ex_2_1_keyb.rt)
thisExp.nextEntry()
# check responses
if ex_2_2_keyb.keys in ['', [], None]:  # No response was made
    ex_2_2_keyb.keys=None
    # was no response the correct answer?!
    if str("'g'").lower() == 'none':
       ex_2_2_keyb.corr = 1  # correct non-response
    else:
       ex_2_2_keyb.corr = 0  # failed to respond (incorrectly)
# store data for thisExp (ExperimentHandler)
thisExp.addData('ex_2_2_keyb.keys',ex_2_2_keyb.keys)
thisExp.addData('ex_2_2_keyb.corr', ex_2_2_keyb.corr)
if ex_2_2_keyb.keys != None:  # we had a response
    thisExp.addData('ex_2_2_keyb.rt', ex_2_2_keyb.rt)
thisExp.nextEntry()

# set up handler to look after randomisation of conditions etc
trials_2 = data.TrialHandler(nReps=2, method='sequential', 
    extraInfo=expInfo, originPath=-1,
    trialList=data.importConditions('block2_stripe.xlsx'),
    seed=None, name='trials_2')
thisExp.addLoop(trials_2)  # add the loop to the experiment
thisTrial_2 = trials_2.trialList[0]  # so we can initialise stimuli with some values
# abbreviate parameter names if possible (e.g. rgb = thisTrial_2.rgb)
if thisTrial_2 != None:
    for paramName in thisTrial_2:
        exec('{} = thisTrial_2[paramName]'.format(paramName))

for thisTrial_2 in trials_2:
    currentLoop = trials_2
    # abbreviate parameter names if possible (e.g. rgb = thisTrial_2.rgb)
    if thisTrial_2 != None:
        for paramName in thisTrial_2:
            exec('{} = thisTrial_2[paramName]'.format(paramName))
    
    # ------Prepare to start Routine "trial"-------
    t = 0
    trialClock.reset()  # clock
    frameN = -1
    continueRoutine = True
    routineTimer.add(2.500000)
    # update component parameters for each repeat
    dotimage.setImage(image)
    key_resp_2 = event.BuilderKeyResponse()
    # keep track of which components have finished
    trialComponents = [dotimage, key_resp_2, fiximage]
    for thisComponent in trialComponents:
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    
    # -------Start Routine "trial"-------
    while continueRoutine and routineTimer.getTime() > 0:
        # get current time
        t = trialClock.getTime()
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *dotimage* updates
        if t >= 1 and dotimage.status == NOT_STARTED:
            # keep track of start time/frame for later
            dotimage.tStart = t
            dotimage.frameNStart = frameN  # exact frame index
            dotimage.setAutoDraw(True)
            
            # === EEG === #
            # # This re-aligns the clocks between the stim computer and the NetStation computer.
            # # Best to put at the start of each trial for maximal timing accuracy.
            ns.sync()
            # Send Message to EEG
            nstag = str(nstag)
            win.callOnFlip(ns.send_event, key=nstag, timestamp=None, label="Trial_%s"%nstag, description="Start trial (type %s)"%nstag, pad=False)
            # === END EEG === #
            
        frameRemains = 1 + 1.5- win.monitorFramePeriod * 0.75  # most of one frame period left
        if dotimage.status == STARTED and t >= frameRemains:
            dotimage.setAutoDraw(False)
        
        # *key_resp_2* updates
        if t >= 1 and key_resp_2.status == NOT_STARTED:
            # keep track of start time/frame for later
            key_resp_2.tStart = t
            key_resp_2.frameNStart = frameN  # exact frame index
            key_resp_2.status = STARTED
            # keyboard checking is just starting
            win.callOnFlip(key_resp_2.clock.reset)  # t=0 on next screen flip
            event.clearEvents(eventType='keyboard')
        frameRemains = 1 + 1.5- win.monitorFramePeriod * 0.75  # most of one frame period left
        if key_resp_2.status == STARTED and t >= frameRemains:
            key_resp_2.status = STOPPED
        if key_resp_2.status == STARTED:
            theseKeys = event.getKeys(keyList=['g', 'b', '1', '2'])
            
            # check for quit:
            if "escape" in theseKeys:
                endExpNow = True
            if len(theseKeys) > 0:  # at least one key was pressed
                key_resp_2.keys = theseKeys[-1]  # just the last key pressed
                key_resp_2.rt = key_resp_2.clock.getTime()
                # was this 'correct'?
                if (key_resp_2.keys == str(corrAns)) or (key_resp_2.keys == corrAns):
                    key_resp_2.corr = 1
                else:
                    key_resp_2.corr = 0
        
        # *fiximage* updates
        if t >= .50 and fiximage.status == NOT_STARTED:
            # keep track of start time/frame for later
            fiximage.tStart = t
            fiximage.frameNStart = frameN  # exact frame index
            fiximage.setAutoDraw(True)
        frameRemains = .50 + .5- win.monitorFramePeriod * 0.75  # most of one frame period left
        if fiximage.status == STARTED and t >= frameRemains:
            fiximage.setAutoDraw(False)
        
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in trialComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # check for quit (the Esc key)
        if endExpNow or event.getKeys(keyList=["escape"]):
            core.quit()
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    # -------Ending Routine "trial"-------
    for thisComponent in trialComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    # check responses
    if key_resp_2.keys in ['', [], None]:  # No response was made
        key_resp_2.keys=None
        # was no response the correct answer?!
        if str(corrAns).lower() == 'none':
           key_resp_2.corr = 1  # correct non-response
        else:
           key_resp_2.corr = 0  # failed to respond (incorrectly)
    # store data for trials_2 (TrialHandler)
    trials_2.addData('key_resp_2.keys',key_resp_2.keys)
    trials_2.addData('key_resp_2.corr', key_resp_2.corr)
    if key_resp_2.keys != None:  # we had a response
        trials_2.addData('key_resp_2.rt', key_resp_2.rt)
    thisExp.nextEntry()
    
# completed 2 repeats of 'trials_2'


# ------Prepare to start Routine "instr3_mixed"-------
t = 0
instr3_mixedClock.reset()  # clock
frameN = -1
continueRoutine = True
routineTimer.add(3.000000)
# update component parameters for each repeat
# keep track of which components have finished
instr3_mixedComponents = [text_5]
for thisComponent in instr3_mixedComponents:
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED

# === EEG === #
# # This re-aligns the clocks between the stim computer and the NetStation computer.
# # Best to put at the start of each trial for maximal timing accuracy.
ns.sync()
# Send Message to EEG
win.callOnFlip(ns.send_event, key='INS3', timestamp=None, label="Instructions3", description="Instructions #3 (mixed)", pad=False)

# === END EEG === #


# -------Start Routine "instr3_mixed"-------
while continueRoutine and routineTimer.getTime() > 0:
    # get current time
    t = instr3_mixedClock.getTime()
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame
    
    # *text_5* updates
    if t >= 0.0 and text_5.status == NOT_STARTED:
        # keep track of start time/frame for later
        text_5.tStart = t
        text_5.frameNStart = frameN  # exact frame index
        text_5.setAutoDraw(True)
    frameRemains = 0.0 + 3.0- win.monitorFramePeriod * 0.75  # most of one frame period left
    if text_5.status == STARTED and t >= frameRemains:
        text_5.setAutoDraw(False)
    
    # check if all components have finished
    if not continueRoutine:  # a component has requested a forced-end of Routine
        break
    continueRoutine = False  # will revert to True if at least one component still running
    for thisComponent in instr3_mixedComponents:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished
    
    # check for quit (the Esc key)
    if endExpNow or event.getKeys(keyList=["escape"]):
        core.quit()
    
    # refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()

# -------Ending Routine "instr3_mixed"-------
for thisComponent in instr3_mixedComponents:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)

# set up handler to look after randomisation of conditions etc
trials_3 = data.TrialHandler(nReps=1, method='sequential', 
    extraInfo=expInfo, originPath=-1,
    trialList=data.importConditions('block3_mixed.xlsx'),
    seed=None, name='trials_3')
thisExp.addLoop(trials_3)  # add the loop to the experiment
thisTrial_3 = trials_3.trialList[0]  # so we can initialise stimuli with some values
# abbreviate parameter names if possible (e.g. rgb = thisTrial_3.rgb)
if thisTrial_3 != None:
    for paramName in thisTrial_3:
        exec('{} = thisTrial_3[paramName]'.format(paramName))

for thisTrial_3 in trials_3:
    currentLoop = trials_3
    # abbreviate parameter names if possible (e.g. rgb = thisTrial_3.rgb)
    if thisTrial_3 != None:
        for paramName in thisTrial_3:
            exec('{} = thisTrial_3[paramName]'.format(paramName))
    
    # ------Prepare to start Routine "trial"-------
    t = 0
    trialClock.reset()  # clock
    frameN = -1
    continueRoutine = True
    routineTimer.add(2.500000)
    # update component parameters for each repeat
    dotimage.setImage(image)
    key_resp_2 = event.BuilderKeyResponse()
    # keep track of which components have finished
    trialComponents = [dotimage, key_resp_2, fiximage]
    for thisComponent in trialComponents:
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    
    # -------Start Routine "trial"-------
    while continueRoutine and routineTimer.getTime() > 0:
        # get current time
        t = trialClock.getTime()
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *dotimage* updates
        if t >= 1 and dotimage.status == NOT_STARTED:
            # keep track of start time/frame for later
            dotimage.tStart = t
            dotimage.frameNStart = frameN  # exact frame index
            dotimage.setAutoDraw(True)
            
            # === EEG === #
            # # This re-aligns the clocks between the stim computer and the NetStation computer.
            # # Best to put at the start of each trial for maximal timing accuracy.
            ns.sync()
            # Send Message to EEG
            nstag = str(nstag)
            win.callOnFlip(ns.send_event, key=nstag, timestamp=None, label="Trial_%s"%nstag, description="Start trial (type %s)"%nstag, pad=False)
            # === END EEG === #
            
        frameRemains = 1 + 1.5- win.monitorFramePeriod * 0.75  # most of one frame period left
        if dotimage.status == STARTED and t >= frameRemains:
            dotimage.setAutoDraw(False)
        
        # *key_resp_2* updates
        if t >= 1 and key_resp_2.status == NOT_STARTED:
            # keep track of start time/frame for later
            key_resp_2.tStart = t
            key_resp_2.frameNStart = frameN  # exact frame index
            key_resp_2.status = STARTED
            # keyboard checking is just starting
            win.callOnFlip(key_resp_2.clock.reset)  # t=0 on next screen flip
            event.clearEvents(eventType='keyboard')
        frameRemains = 1 + 1.5- win.monitorFramePeriod * 0.75  # most of one frame period left
        if key_resp_2.status == STARTED and t >= frameRemains:
            key_resp_2.status = STOPPED
        if key_resp_2.status == STARTED:
            theseKeys = event.getKeys(keyList=['g', 'b', '1', '2'])
            
            # check for quit:
            if "escape" in theseKeys:
                endExpNow = True
            if len(theseKeys) > 0:  # at least one key was pressed
                key_resp_2.keys = theseKeys[-1]  # just the last key pressed
                key_resp_2.rt = key_resp_2.clock.getTime()
                # was this 'correct'?
                if (key_resp_2.keys == str(corrAns)) or (key_resp_2.keys == corrAns):
                    key_resp_2.corr = 1
                else:
                    key_resp_2.corr = 0
        
        # *fiximage* updates
        if t >= .50 and fiximage.status == NOT_STARTED:
            # keep track of start time/frame for later
            fiximage.tStart = t
            fiximage.frameNStart = frameN  # exact frame index
            fiximage.setAutoDraw(True)
        frameRemains = .50 + .5- win.monitorFramePeriod * 0.75  # most of one frame period left
        if fiximage.status == STARTED and t >= frameRemains:
            fiximage.setAutoDraw(False)
        
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in trialComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # check for quit (the Esc key)
        if endExpNow or event.getKeys(keyList=["escape"]):
            core.quit()
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    # -------Ending Routine "trial"-------
    for thisComponent in trialComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    # check responses
    if key_resp_2.keys in ['', [], None]:  # No response was made
        key_resp_2.keys=None
        # was no response the correct answer?!
        if str(corrAns).lower() == 'none':
           key_resp_2.corr = 1  # correct non-response
        else:
           key_resp_2.corr = 0  # failed to respond (incorrectly)
    # store data for trials_3 (TrialHandler)
    trials_3.addData('key_resp_2.keys',key_resp_2.keys)
    trials_3.addData('key_resp_2.corr', key_resp_2.corr)
    if key_resp_2.keys != None:  # we had a response
        trials_3.addData('key_resp_2.rt', key_resp_2.rt)
    thisExp.nextEntry()
    
# completed 1 repeats of 'trials_3'


# ------Prepare to start Routine "goodbye"-------
t = 0
goodbyeClock.reset()  # clock
frameN = -1
continueRoutine = True
routineTimer.add(4.000000)
# update component parameters for each repeat
# keep track of which components have finished
goodbyeComponents = [text_6]
for thisComponent in goodbyeComponents:
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED

# -------Start Routine "goodbye"-------
while continueRoutine and routineTimer.getTime() > 0:
    # get current time
    t = goodbyeClock.getTime()
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame
    
    # *text_6* updates
    if t >= 0.0 and text_6.status == NOT_STARTED:
        # keep track of start time/frame for later
        text_6.tStart = t
        text_6.frameNStart = frameN  # exact frame index
        text_6.setAutoDraw(True)
    frameRemains = 0.0 + 4.0- win.monitorFramePeriod * 0.75  # most of one frame period left
    if text_6.status == STARTED and t >= frameRemains:
        text_6.setAutoDraw(False)
    
    # check if all components have finished
    if not continueRoutine:  # a component has requested a forced-end of Routine
        break
    continueRoutine = False  # will revert to True if at least one component still running
    for thisComponent in goodbyeComponents:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished
    
    # check for quit (the Esc key)
    if endExpNow or event.getKeys(keyList=["escape"]):
        core.quit()
    
    # refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()

# === EEG === #
# # This re-aligns the clocks between the stim computer and the NetStation computer.
# # Best to put at the start of each trial for maximal timing accuracy.
ns.sync()
# Send Message to EEG
win.callOnFlip(ns.send_event, key='DONE', timestamp=None, label="ExperimentDone", description="End of Scan", pad=False)

print('Ending EGI session...')
# === End Session
# # This method is misleading, as it merely pauses the recording in NetStation. Equivalent to the pause button.
# # It is not actually stopping the recording session. That is done by the 'EndSession()' method.
ns.StopRecording()

# # I don't typically use this, as it is closes the current "Session" in NetStation.
# # I find it easier to just pause the recording using "StopRecording()" and then
# # get ending impedance measurements before manually closing NetStation.
ns.EndSession()

# # This line ends the connection via the ns object, and should then be destroying the object itself.
# # It is good practice to use so as not to waste memory or leave TCP/IP links open, which could lead to being
# # unable to reconnect without restarting the computer running the experiment.
if isEegConnected:
    ns.disconnect()

# === END EEG === #

# -------Ending Routine "goodbye"-------
for thisComponent in goodbyeComponents:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)
# these shouldn't be strictly necessary (should auto-save)
thisExp.saveAsWideText(filename+'.csv')
thisExp.saveAsPickle(filename)
logging.flush()
# make sure everything is closed down
thisExp.abort()  # or data files will save again on exit
win.close()
core.quit()
