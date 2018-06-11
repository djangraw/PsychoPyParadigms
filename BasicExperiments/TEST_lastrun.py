#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This experiment was created using PsychoPy2 Experiment Builder (v1.90.1),
    on Mon Jun 11 10:48:56 2018
If you publish work using this script please cite the PsychoPy publications:
    Peirce, JW (2007) PsychoPy - Psychophysics software in Python.
        Journal of Neuroscience Methods, 162(1-2), 8-13.
    Peirce, JW (2009) Generating stimuli for neuroscience using PsychoPy.
        Frontiers in Neuroinformatics, 2:10. doi: 10.3389/neuro.11.010.2008
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

# Ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__)).decode(sys.getfilesystemencoding())
os.chdir(_thisDir)

# Store info about the experiment session
expName = 'TEST'  # from the Builder filename that created this script
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
    originPath=u'/Users/jangrawdc/Documents/Python/PsychoPyParadigms/BasicExperiments/TEST.psyexp',
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

# Initialize components for Routine "Trigger"
TriggerClock = core.Clock()
TriggerText = visual.TextStim(win=win, name='TriggerText',
    text='Waiting for trigger...\n\n(Experimenter: press t to override.)',
    font='Arial',
    pos=(0, 0), height=0.1, wrapWidth=None, ori=0, 
    color='white', colorSpace='rgb', opacity=1,
    depth=0.0);

# Initialize components for Routine "fixation"
fixationClock = core.Clock()
fixCross1 = visual.TextStim(win=win, name='fixCross1',
    text=u'+',
    font=u'Arial',
    pos=(0, 0), height=0.5, wrapWidth=None, ori=0, 
    color=u'white', colorSpace='rgb', opacity=1,
    depth=0.0);

# Initialize components for Routine "Movie"
MovieClock = core.Clock()
movie = visual.MovieStim3(
    win=win, name='movie',
    noAudio = False,
    filename='/Users/jangrawdc/Documents/Python/PsychoPyParadigms/BasicExperiments/Movies/Paperman.mp4',
    ori=0, pos=(0, 0), opacity=1,
    depth=0.0,
    )
fixCross = visual.TextStim(win=win, name='fixCross',
    text=u'+',
    font=u'Arial',
    pos=(0, 0), height=0.5, wrapWidth=None, ori=0, 
    color=u'white', colorSpace='rgb', opacity=1,
    depth=-1.0);

# Initialize components for Routine "fixation"
fixationClock = core.Clock()
fixCross1 = visual.TextStim(win=win, name='fixCross1',
    text=u'+',
    font=u'Arial',
    pos=(0, 0), height=0.5, wrapWidth=None, ori=0, 
    color=u'white', colorSpace='rgb', opacity=1,
    depth=0.0);

# Initialize components for Routine "CoolDown"
CoolDownClock = core.Clock()
CoolDownText = visual.TextStim(win=win, name='CoolDownText',
    text='Please stay still until\nthe scanner noise stops.',
    font='Arial',
    pos=(0, 0), height=0.1, wrapWidth=None, ori=0, 
    color='white', colorSpace='rgb', opacity=1,
    depth=0.0);

# Create some handy timers
globalClock = core.Clock()  # to track the time since experiment started
routineTimer = core.CountdownTimer()  # to track time remaining of each (non-slip) routine 

# ------Prepare to start Routine "Trigger"-------
t = 0
TriggerClock.reset()  # clock
frameN = -1
continueRoutine = True
# update component parameters for each repeat
TriggerKey = event.BuilderKeyResponse()
# keep track of which components have finished
TriggerComponents = [TriggerText, TriggerKey]
for thisComponent in TriggerComponents:
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED

# -------Start Routine "Trigger"-------
while continueRoutine:
    # get current time
    t = TriggerClock.getTime()
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame
    
    # *TriggerText* updates
    if t >= 0.0 and TriggerText.status == NOT_STARTED:
        # keep track of start time/frame for later
        TriggerText.tStart = t
        TriggerText.frameNStart = frameN  # exact frame index
        TriggerText.setAutoDraw(True)
    
    # *TriggerKey* updates
    if t >= 0.0 and TriggerKey.status == NOT_STARTED:
        # keep track of start time/frame for later
        TriggerKey.tStart = t
        TriggerKey.frameNStart = frameN  # exact frame index
        TriggerKey.status = STARTED
        # keyboard checking is just starting
        win.callOnFlip(TriggerKey.clock.reset)  # t=0 on next screen flip
        event.clearEvents(eventType='keyboard')
    if TriggerKey.status == STARTED:
        theseKeys = event.getKeys(keyList=['t'])
        
        # check for quit:
        if "escape" in theseKeys:
            endExpNow = True
        if len(theseKeys) > 0:  # at least one key was pressed
            TriggerKey.keys = theseKeys[-1]  # just the last key pressed
            TriggerKey.rt = TriggerKey.clock.getTime()
            # a response ends the routine
            continueRoutine = False
    
    # check if all components have finished
    if not continueRoutine:  # a component has requested a forced-end of Routine
        break
    continueRoutine = False  # will revert to True if at least one component still running
    for thisComponent in TriggerComponents:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished
    
    # check for quit (the Esc key)
    if endExpNow or event.getKeys(keyList=["escape"]):
        core.quit()
    
    # refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()

# -------Ending Routine "Trigger"-------
for thisComponent in TriggerComponents:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)
# check responses
if TriggerKey.keys in ['', [], None]:  # No response was made
    TriggerKey.keys=None
thisExp.addData('TriggerKey.keys',TriggerKey.keys)
if TriggerKey.keys != None:  # we had a response
    thisExp.addData('TriggerKey.rt', TriggerKey.rt)
thisExp.nextEntry()
# the Routine "Trigger" was not non-slip safe, so reset the non-slip timer
routineTimer.reset()

# ------Prepare to start Routine "fixation"-------
t = 0
fixationClock.reset()  # clock
frameN = -1
continueRoutine = True
routineTimer.add(6.000000)
# update component parameters for each repeat
# keep track of which components have finished
fixationComponents = [fixCross1]
for thisComponent in fixationComponents:
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED

# -------Start Routine "fixation"-------
while continueRoutine and routineTimer.getTime() > 0:
    # get current time
    t = fixationClock.getTime()
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame
    
    # *fixCross1* updates
    if t >= 0.0 and fixCross1.status == NOT_STARTED:
        # keep track of start time/frame for later
        fixCross1.tStart = t
        fixCross1.frameNStart = frameN  # exact frame index
        fixCross1.setAutoDraw(True)
    frameRemains = 0.0 + 6.0- win.monitorFramePeriod * 0.75  # most of one frame period left
    if fixCross1.status == STARTED and t >= frameRemains:
        fixCross1.setAutoDraw(False)
    
    # check if all components have finished
    if not continueRoutine:  # a component has requested a forced-end of Routine
        break
    continueRoutine = False  # will revert to True if at least one component still running
    for thisComponent in fixationComponents:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished
    
    # check for quit (the Esc key)
    if endExpNow or event.getKeys(keyList=["escape"]):
        core.quit()
    
    # refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()

# -------Ending Routine "fixation"-------
for thisComponent in fixationComponents:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)

# set up handler to look after randomisation of conditions etc
Movies = data.TrialHandler(nReps=5, method='sequential', 
    extraInfo=expInfo, originPath=-1,
    trialList=[None],
    seed=None, name='Movies')
thisExp.addLoop(Movies)  # add the loop to the experiment
thisMovie = Movies.trialList[0]  # so we can initialise stimuli with some values
# abbreviate parameter names if possible (e.g. rgb = thisMovie.rgb)
if thisMovie != None:
    for paramName in thisMovie:
        exec('{} = thisMovie[paramName]'.format(paramName))

for thisMovie in Movies:
    currentLoop = Movies
    # abbreviate parameter names if possible (e.g. rgb = thisMovie.rgb)
    if thisMovie != None:
        for paramName in thisMovie:
            exec('{} = thisMovie[paramName]'.format(paramName))
    
    # ------Prepare to start Routine "Movie"-------
    t = 0
    MovieClock.reset()  # clock
    frameN = -1
    continueRoutine = True
    routineTimer.add(15.000000)
    # update component parameters for each repeat
    # keep track of which components have finished
    MovieComponents = [movie, fixCross]
    for thisComponent in MovieComponents:
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    
    # -------Start Routine "Movie"-------
    while continueRoutine and routineTimer.getTime() > 0:
        # get current time
        t = MovieClock.getTime()
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *movie* updates
        if t >= 0.0 and movie.status == NOT_STARTED:
            # keep track of start time/frame for later
            movie.tStart = t
            movie.frameNStart = frameN  # exact frame index
            movie.setAutoDraw(True)
        frameRemains = 0.0 + 10.0- win.monitorFramePeriod * 0.75  # most of one frame period left
        if movie.status == STARTED and t >= frameRemains:
            movie.setAutoDraw(False)
        
        # *fixCross* updates
        if t >= 10.0 and fixCross.status == NOT_STARTED:
            # keep track of start time/frame for later
            fixCross.tStart = t
            fixCross.frameNStart = frameN  # exact frame index
            fixCross.setAutoDraw(True)
        frameRemains = 10.0 + 5.0- win.monitorFramePeriod * 0.75  # most of one frame period left
        if fixCross.status == STARTED and t >= frameRemains:
            fixCross.setAutoDraw(False)
        
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in MovieComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # check for quit (the Esc key)
        if endExpNow or event.getKeys(keyList=["escape"]):
            core.quit()
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    # -------Ending Routine "Movie"-------
    for thisComponent in MovieComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    thisExp.nextEntry()
    
# completed 5 repeats of 'Movies'


# ------Prepare to start Routine "fixation"-------
t = 0
fixationClock.reset()  # clock
frameN = -1
continueRoutine = True
routineTimer.add(6.000000)
# update component parameters for each repeat
# keep track of which components have finished
fixationComponents = [fixCross1]
for thisComponent in fixationComponents:
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED

# -------Start Routine "fixation"-------
while continueRoutine and routineTimer.getTime() > 0:
    # get current time
    t = fixationClock.getTime()
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame
    
    # *fixCross1* updates
    if t >= 0.0 and fixCross1.status == NOT_STARTED:
        # keep track of start time/frame for later
        fixCross1.tStart = t
        fixCross1.frameNStart = frameN  # exact frame index
        fixCross1.setAutoDraw(True)
    frameRemains = 0.0 + 6.0- win.monitorFramePeriod * 0.75  # most of one frame period left
    if fixCross1.status == STARTED and t >= frameRemains:
        fixCross1.setAutoDraw(False)
    
    # check if all components have finished
    if not continueRoutine:  # a component has requested a forced-end of Routine
        break
    continueRoutine = False  # will revert to True if at least one component still running
    for thisComponent in fixationComponents:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished
    
    # check for quit (the Esc key)
    if endExpNow or event.getKeys(keyList=["escape"]):
        core.quit()
    
    # refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()

# -------Ending Routine "fixation"-------
for thisComponent in fixationComponents:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)

# ------Prepare to start Routine "CoolDown"-------
t = 0
CoolDownClock.reset()  # clock
frameN = -1
continueRoutine = True
# update component parameters for each repeat
EndKey = event.BuilderKeyResponse()
# keep track of which components have finished
CoolDownComponents = [CoolDownText, EndKey]
for thisComponent in CoolDownComponents:
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED

# -------Start Routine "CoolDown"-------
while continueRoutine:
    # get current time
    t = CoolDownClock.getTime()
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame
    
    # *CoolDownText* updates
    if t >= 0.0 and CoolDownText.status == NOT_STARTED:
        # keep track of start time/frame for later
        CoolDownText.tStart = t
        CoolDownText.frameNStart = frameN  # exact frame index
        CoolDownText.setAutoDraw(True)
    
    # *EndKey* updates
    if t >= 0.0 and EndKey.status == NOT_STARTED:
        # keep track of start time/frame for later
        EndKey.tStart = t
        EndKey.frameNStart = frameN  # exact frame index
        EndKey.status = STARTED
        # keyboard checking is just starting
        win.callOnFlip(EndKey.clock.reset)  # t=0 on next screen flip
        event.clearEvents(eventType='keyboard')
    if EndKey.status == STARTED:
        theseKeys = event.getKeys(keyList=['q', 'escape'])
        
        # check for quit:
        if "escape" in theseKeys:
            endExpNow = True
        if len(theseKeys) > 0:  # at least one key was pressed
            EndKey.keys = theseKeys[-1]  # just the last key pressed
            EndKey.rt = EndKey.clock.getTime()
            # a response ends the routine
            continueRoutine = False
    
    # check if all components have finished
    if not continueRoutine:  # a component has requested a forced-end of Routine
        break
    continueRoutine = False  # will revert to True if at least one component still running
    for thisComponent in CoolDownComponents:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished
    
    # check for quit (the Esc key)
    if endExpNow or event.getKeys(keyList=["escape"]):
        core.quit()
    
    # refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()

# -------Ending Routine "CoolDown"-------
for thisComponent in CoolDownComponents:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)
# check responses
if EndKey.keys in ['', [], None]:  # No response was made
    EndKey.keys=None
thisExp.addData('EndKey.keys',EndKey.keys)
if EndKey.keys != None:  # we had a response
    thisExp.addData('EndKey.rt', EndKey.rt)
thisExp.nextEntry()
# the Routine "CoolDown" was not non-slip safe, so reset the non-slip timer
routineTimer.reset()
# these shouldn't be strictly necessary (should auto-save)
thisExp.saveAsWideText(filename+'.csv')
thisExp.saveAsPickle(filename)
logging.flush()
# make sure everything is closed down
thisExp.abort()  # or data files will save again on exit
win.close()
core.quit()
