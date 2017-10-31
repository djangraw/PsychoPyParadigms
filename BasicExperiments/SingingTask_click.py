#!/usr/bin/env python2
"""Display multi-page text with interspersed thought probes.
Then ask the subject comprehension questions at the end."""
# SingingTask.py
#
# Created 3/17/17 by DJ based on ReadingTask.py.

from psychopy import core, gui, data, event, sound, logging #, visual # visual causes a bug in the guis, so I moved it down.
from psychopy.tools.filetools import fromFile, toFile
from random import shuffle
import time, numpy as np
import AppKit, os # for monitor size detection, files
import PromptTools


# ====================== #
# ===== PARAMETERS ===== #
# ====================== #
# Save the parameters declared below?
saveParams = True;
newParamsFilename = 'SingingTaskParams.pickle'

# Declare primary task parameters.
bpm = 36
tPerBeat = 60.0/bpm
params = {
    'skipPrompts': True,      # at the beginning
    'tStartup': 10.0,      # time after beginning of scan before starting first pre-trial message
    'tempo_bpm': bpm,#90,         # beats per minute (beat time = 60.0/tempo_bpm)
    'trialTime': tPerBeat*16,#20.0,#20,     # duration of song/exercise (in sec)... will be rounded down to nearest multiple of beat time
    'msgTime': tPerBeat*6,#6.0,           # duration of pre-trial message (in sec)... will be rounded down to nearest multiple of beat time
    'restTime': tPerBeat*10,#14.0,      # duration of post-trial rest (in sec)... ITI = msgTime+restTime
    'IBI': tPerBeat*10,#14.0,#17,           # time between end of block/probe and beginning of next block (in seconds)
    'nBlocks': 2,             # blocks for this run
    'trialTypes': ['Speak','Imagine','Sing'], #['Improvise'], #  currently used only for visual instructions
    'playPitch': [True, True, True], # [True], # Play pitch before each block?
    'randomizeOrder': True,     # randomize each block
    'advanceKey': 'space',    # key to skip block
    'triggerKey': 't',        # key from scanner that says scan is starting
    'promptType': 'CountImagineSing',#'Default',  # must correspond to keyword in PromptTools.py
    # declare click params
    'clickSound': 'music/High Seiko SQ50.wav',#'F',
    'clickVolume': 1,
    # declare pitch params
    'pitchNote': 'C',#'music/Major_Chords_Low/Grand Piano - Fazioli - major C.wav',#
    'pitchOctave': 4,
    'pitchBeatStart': 4,
    'pitchBeatDur': 1,
    'pitchVolume': 1,
# declare other stimulus parameters
    'fullScreen': True,       # run in full screen mode?
    'screenToShow': 0,        # display on primary screen (0) or secondary (1)?
    'fixCrossSize': 50,       # size of cross, in pixels
    'fixCrossPos': (0,0), # (x,y) pos of fixation cross displayed before each page (for drift correction)
    'usePhotodiode': False     # add sync square in corner of screen
    #'textBoxSize': [800,600] # [640,360]# [700, 500]   # width, height of text box (in pixels)
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
    expInfo = fromFile('lastSingInfo.pickle')
    expInfo['session'] +=1 # automatically increment session number
    expInfo['paramsFile'] = [expInfo['paramsFile'],'Load...']
except:#if not there then use a default set
    expInfo = {'subject':'1', 'session':1, 'paramsFile':['DEFAULT','Load...']}
# overwrite if you just saved a new parameter set
if saveParams:
    expInfo['paramsFile'] = [newParamsFilename,'Load...']
dateStr = time.strftime("%b_%d_%H%M", time.localtime()) # add the current time

#present a dialogue to change params
dlg = gui.DlgFromDict(expInfo, title='Singing task', order=['subject','session','paramsFile'])
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
toFile('lastSingingInfo.pickle', expInfo)#save params to file for next time

#make a log file to save parameter/event  data
filename = 'Singing-%s-%d-%s'%(expInfo['subject'], expInfo['session'], dateStr) #'Sart-' + expInfo['subject'] + '-' + expInfo['session'] + '-' + dateStr
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
fixation = visual.ShapeStim(win,lineColor='#000000',lineWidth=3.0,vertices=fCS_vertices,units='pix',closeShape=False);
message1 = visual.TextStim(win, pos=[0, 0], wrapWidth=50, color='#000000', alignHoriz='center', name='topMsg', text="aaa", height=3)
message2 = visual.TextStim(win, pos=[0,-10], wrapWidth=50, color='#000000', alignHoriz='center', name='bottomMsg', text="bbb", height=3)
# initialize photodiode stimulus
squareSize = 0.4
diodeSquare = visual.Rect(win,pos=[squareSize/4-1,squareSize/4-1],lineColor='white',fillColor='white',size=[squareSize,squareSize],units='norm')

# Look up prompts
[topPrompts,bottomPrompts] = PromptTools.GetPrompts(os.path.basename(__file__),params['promptType'],params)
print('%d prompts loaded from %s'%(len(topPrompts),'PromptTools.py'))

# Declare sounds
timePerBeat = 60.0/params['tempo_bpm']
pitchDur = timePerBeat*params['pitchBeatDur']
print('pitch dur = %f'%(pitchDur))
if len(params['pitchNote'])<4: # just a note name
    pitch = sound.Sound(value=params['pitchNote'], sampleRate=44100, secs=pitchDur, bits=8, octave=params['pitchOctave'],name='pitch')
else:
    pitch = sound.Sound(value=params['pitchNote'], start=0.0,stop=pitchDur, name='pitch')
pitch.setVolume(params['pitchVolume']) 
# play pitch
# pitch.play()
# Declare click track sound
if len(params['pitchNote'])<4: # just a note name
    click = sound.Sound(value=params['clickSound'], sampleRate=44100, secs=pitchDur, bits=8, octave=4,name='click')
else:
    click = sound.Sound(value=params['clickSound'], name='click')
click.setVolume(params['clickVolume']) 
# play pitch
click.play()

# ============================ #
# ======= SUBFUNCTIONS ======= #
# ============================ #

# increment time of next window flip
def AddToFlipTime(tIncrement=1.0):
    tNextFlip[0] += tIncrement
#    print("%1.3f --> %1.3f"%(globalClock.getTime(),tNextFlip[0]))

def RunTrial(preTrialTime, trialTime, restTime, condition, playPitch):
    # adjust pre-trial time
    timePerBeat = 60.0/params['tempo_bpm'];
    nPreTrialBeats = int(preTrialTime/timePerBeat)
    nTrialBeats = int(trialTime/timePerBeat)
    # Display pre-trial message
    win.clearBuffer()
    for iBeat in range(0, nPreTrialBeats):
        # set up frame
        message1.setText('%s in %d...'%(condition,nPreTrialBeats-iBeat))
        message1.draw()
        win.logOnFlip(level=logging.EXP, msg='Display %sIn%d'%(condition,nPreTrialBeats-iBeat))
        win.callOnFlip(AddToFlipTime,timePerBeat)
        # wait until it's time
        while (globalClock.getTime()<tNextFlip[0]):
            core.wait(0.001)
            # pass
        # FLIP DISPLAY!
        win.flip()
        if playPitch and (nPreTrialBeats-iBeat)==params['pitchBeatStart']:
            pitch.play()
        # check for escape characters
        thisKey = event.getKeys()
        if thisKey!=None and len(thisKey)>0 and thisKey[0] in ['q','escape']:
            core.quit()
    
    # Display trial message
    for iBeat in range(0, nTrialBeats):
        # message1.setText('%s (%d/%d)'%(condition,iBeat+1,nTrialBeats))
        message1.setText('%s'%(condition))
        message1.draw()
        # win.logOnFlip(level=logging.EXP, msg='Display %s(%d/%d)'%(condition,iBeat+1,nTrialBeats))
        win.logOnFlip(level=logging.EXP, msg='Display %s'%(condition))
        win.callOnFlip(AddToFlipTime,timePerBeat)
        # wait until it's time
        while (globalClock.getTime()<tNextFlip[0]):
            pass
        # FLIP DISPLAY!
        win.flip()
        click.play()
        # check for escape characters
        thisKey = event.getKeys()
        if thisKey!=None and len(thisKey)>0 and thisKey[0] in ['q','escape']:
            core.quit()
    
#    # Flush the key buffer and mouse movements
#    event.clearEvents()
#    # Wait for relevant key press or 'maxPageTime' seconds
#    thisKey = event.waitKeys(maxWait=trialTime-0.5,keyList=[params['advanceKey'],'q','escape'])
    # Process key press
#    if thisKey!=None and len(thisKey)>0 and thisKey[0] in ['q','escape']:
#        core.quit()
        #allow the screen to update immediately
#        tNextFlip[0]=globalClock.getTime()
    
    if restTime>0:
        # draw fixation cross
        fixation.draw()
        win.logOnFlip(level=logging.EXP, msg='Display Fixation')
        win.callOnFlip(AddToFlipTime,restTime)
        # wait until it's time
        while (globalClock.getTime()<tNextFlip[0]):
            pass
            # flash photodiode
        if params['usePhotodiode']:
            diodeSquare.draw()
            win.flip()
            # erase diode square and re-draw
            fixation.draw()
        # FLIP DISPLAY!
        win.flip()


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
for iBlock in range(0,params['nBlocks']): # for each block of pages
    
    # log new block
    logging.log(level=logging.EXP, msg='Start Block %d'%iBlock)
    
    # trial loop
    trialTypes = params['trialTypes']
    playPitch = params['playPitch']
    if params['randomizeOrder']:
        order = range(len(params['trialTypes']))
        shuffle(order)
        trialTypes = [params['trialTypes'][i] for i in order]
        playPitch = [params['playPitch'][i] for i in order]
        
    for iTrial in range(0,len(trialTypes)):
        # display text
        logging.log(level=logging.EXP, msg='Block %d, Trial %d'%(iBlock,iTrial))
        if iTrial < (len(trialTypes)-1):
            RunTrial(params['msgTime'],params['trialTime'],params['restTime'],trialTypes[iTrial],playPitch[iTrial])
        elif iBlock< (params['nBlocks']-1):
            RunTrial(params['msgTime'],params['trialTime'],params['IBI'],trialTypes[iTrial],playPitch[iTrial])
        else:
            RunTrial(params['msgTime'],params['trialTime'],0,trialTypes[iTrial],playPitch[iTrial])
            
    # handle end of block
    if iBlock == (params['nBlocks']-1):
        message1.setText("That's the end of this run!")
        message2.setText("Please stay still until the scanner noise stops.")
        win.logOnFlip(level=logging.EXP, msg='Display TheEnd')
        message1.draw()
        message2.draw()
        # wait until it's time
        while (globalClock.getTime()<tNextFlip[0]):
            pass
        # change the screen
        win.flip()
        # wait until a button is pressed to exit
        thisKey = event.waitKeys(keyList=['q','escape'])

    

# exit experiment
core.quit()
