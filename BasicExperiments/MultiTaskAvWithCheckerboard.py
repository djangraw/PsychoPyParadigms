#!/usr/bin/env python2
"""Display visual and auditory stimuli to the subject, requiring different responses from them based on pre-block cues.
Also present a large, task-irrelevant checkerboard stimulus at random times."""

# MultiTaskAvWithCheckerboard.py
#
# Created 4/18/17 by DJ based on AuditorySequenceTask.py.

from psychopy import core, gui, data, event, sound, logging #, visual # visual causes a bug in the guis, so I moved it down.
from psychopy.tools.filetools import fromFile, toFile
import random
import time, numpy as np
import AppKit, os # for monitor size detection, files
import PromptTools
import numpy, scipy.signal
from numpy import pi
import matplotlib.pyplot as plt


# ====================== #
# ===== PARAMETERS ===== #
# ====================== #
# Save the parameters declared below?
saveParams = True;
newParamsFilename = 'MultiTaskAvParams.pickle'

# Declare primary task parameters.
params = {
    # Start-of-run prompts
    'skipPrompts': False,       # at the beginning
    'promptType': 'Long',    # must correspond to keyword in PromptTools.py
    # inputs
    'triggerKey': 't',          # key from scanner that says scan is starting
    'respKeys': ['1','2'],      # keys corresponding to 'same' and 'different'
    # trial timing
    'visDur': 0.2,              # duration of visual stimulation (in seconds)
    'minVisITI': 3.0,           # minimum time between start of one visual trial and the next (in seconds)
    'maxVisITI': 5.0,           # maximum time between start of one visual trial and the next (in seconds)
    'minAudITI': 3.0,           # minimum time between start of one auditory trial and the next (in seconds)
    'maxAudITI': 5.0,           # maximum time between start of one auditory trial and the next (in seconds)
    'checkDur': 2.0,            # duration of checkerboard (in sec)
    'checkFreq': 10,            # frequency of checkerboard (in Hz)
    'minCheckITI': 5.0,         # minimum time between start of one checkerboard and the next (in seconds)
    'maxCheckITI': 10.0,         # maximum time between start of one checkerboard and the next (in seconds)
    # Run timing
    'tStartup': 0.0,            # time after beginning of scan before starting first trial
    'tCoolDown': 0.0,           # time at end of block where no trials are displayed
    'blockDur': 300.0,          # duration of each block (in seconds)
    'countDur': 20.0,           # duration of count period (in seconds)
    'IBI': 10.0,                  # time between blocks (in seconds)
    # stimulus params
    'visWords': ['1','2','3','4'], # text stimuli (to be selected randomly)
    'visHeight': 3,           # size of text stimuli
    'visColor': '#FF0000',      # hex color of stimulus text
    'audFolder': 'numbers/',    # folder where audio files are kept
    'audFiles': ['one.wav','two.wav','three.wav','four.wav'], # audio stimuli (to be selected randomly)
    'audVolume': 1,             # volume for audio stimuli
    'checkSize': 12,             # size of checkerboard (units?)
    # cue params
    'cues': ['Visual: Add','Audio: Add'], # ['Audio: Button','Audio: Add','Visual: Button','Visual: Add','Rest'], # 
    'cueDur': 2.0,              # duration of cue (in seconds)
    'randomizeCues': True,      # shuffle order of cues randomly (without replacement)
    # other stimulus parameters
    'fullScreen': True,         # run in full screen mode?
    'screenToShow': 0,          # display on primary screen (0) or secondary (1)?
    'fixCrossSize': 50,         # size of cross, in pixels
    'fixCrossPos': (0,0),       # (x,y) pos of fixation cross displayed before each page (for drift correction)
    'fixColor': '#FF0000'       # hex color of fixation cross
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
    expInfo = fromFile('lastMultiTaskAvInfo.pickle')
    expInfo['session'] +=1 # automatically increment session number
    expInfo['paramsFile'] = [expInfo['paramsFile'],'Load...']
except:#if not there then use a default set
    expInfo = {'subject':'1', 'session':1, 'paramsFile':['DEFAULT','Load...']}
# overwrite if you just saved a new parameter set
if saveParams:
    expInfo['paramsFile'] = [newParamsFilename,'Load...']
dateStr = time.strftime("%b_%d_%H%M", time.localtime()) # add the current time

#present a dialogue to change params
dlg = gui.DlgFromDict(expInfo, title='Multi-Task A/V', order=['subject','session','paramsFile'])
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
toFile('lastMultiTaskAvInfo.pickle', expInfo)#save params to file for next time

#make a log file to save parameter/event  data
filename = 'MultiTaskAv-%s-%d-%s'%(expInfo['subject'], expInfo['session'], dateStr) #'Sart-' + expInfo['subject'] + '-' + expInfo['session'] + '-' + dateStr
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
#tNextFlip = [0.0] # put in a list to make it mutable? 

#create window and stimuli
globalClock = core.Clock()#to keep track of time
win = visual.Window(screenRes, fullscr=params['fullScreen'], allowGUI=False, monitor='testMonitor', screen=params['screenToShow'], units='deg', name='win')
#fixation = visual.GratingStim(win, color='black', tex=None, mask='circle',size=0.2)
fCS = params['fixCrossSize'] # rename for brevity
fcX = params['fixCrossPos'][0] # rename for brevity
fcY = params['fixCrossPos'][1] # rename for brevity
fCS_vertices = ((-fCS/2 + fcX, fcY),(fCS/2 + fcX, fcY),(fcX, fcY),(fcX, fCS/2 + fcY),(fcX, -fCS/2 + fcY))
# make different-colored fixation crosses
fixation = visual.ShapeStim(win,lineColor=params['fixColor'],lineWidth=3.0,vertices=fCS_vertices,units='pix',closeShape=False);
# Make trial text
text = visual.TextStim(win, pos=[0, 0], wrapWidth=50, color=params['visColor'], alignHoriz='center', name='mainText', text="aaa", height=params['visHeight'])

# ===== Set up checkerboard stimuli
t= numpy.linspace(0,12,256) # timeline

## # Create expanding-freq y-axis sinusoid # # #
f0y = .1 # begining freq
t1y = 12 # time of reference freq
f1y = 1  # reference freq

y = scipy.signal.chirp(t, f0y, t1y, f1y, method='logarithmic')
ally = numpy.zeros((len(t),len(t)))
for i in xrange(len(ally)):
    ally[:,i] = y #create cols of texture

allys = numpy.append(ally, ally, axis = 1) # this stuff is a dirty way to get the larger texture
reversedy = numpy.flipud(allys) * -1      # this stuff is a dirty way to get the larger texture
yTex = numpy.append(allys, reversedy, axis = 0) # this stuff is a dirty way to get the larger texture

## # Create standard x-axis sinusoid
f0x = .5 
t1x = 12
f1x = .5 # freq is fixed at .5

x = scipy.signal.chirp(t, f0x, t1x, f1x, method='logarithmic')
allx = numpy.zeros((len(t),len(t)))
for i in xrange(len(allx)):
    allx[i,:] = x #create rows of texture

allxs = numpy.append(allx, allx, axis = 0)
reversedx = numpy.fliplr(allxs)
xTex= numpy.append(allxs, reversedx, axis = 1)
### #

fullStim = xTex * yTex #combined sinusoid

texture = numpy.where(fullStim>0, 1, -1) #binarize full sinusoid pattern

texture2 = ally * allx # only one quarter of the full sinusoid
texture2 = numpy.where(texture2>0, 1, -1) 

#print('TEST0')

# plot results
#plt.imshow(texture)
#plt.show()
#plt.imshow(texture2)
#plt.show()

# make checkerboard stimuli
check1 = visual.RadialStim(win, tex = texture, color=1, size=params['checkSize'],
    visibleWedge=[0, 360], radialCycles=1, angularCycles=1, interpolate=False)
check2 = visual.RadialStim(win, tex = -texture, color=1, size=params['checkSize'],
    visibleWedge=[0, 360], radialCycles=1, angularCycles=1, interpolate=False)

# make text messages
message1 = visual.TextStim(win, pos=[0, 0], wrapWidth=50, color='#000000', alignHoriz='center', name='topMsg', text="aaa", height=3)
message2 = visual.TextStim(win, pos=[0,-10], wrapWidth=50, color='#000000', alignHoriz='center', name='bottomMsg', text="bbb", height=3)
# initialize photodiode stimulus
#squareSize = 0.4
#diodeSquare = visual.Rect(win,pos=[squareSize/4-1,squareSize/4-1],lineColor='white',fillColor='white',size=[squareSize,squareSize],units='norm')

# Look up prompts
[topPrompts,bottomPrompts] = PromptTools.GetPrompts(os.path.basename(__file__),params['promptType'],params)
print('%d prompts loaded from %s'%(len(topPrompts),'PromptTools.py'))

# Declare sounds
audSound = [None]*len(params['audFiles'])
for i in range(0,len(params['audFiles'])):
#    print params['sequenceSounds'][i]
    audSound[i] = sound.Sound(value=(params['audFolder'] + params['audFiles'][i]), name='sound%d'%(i+1))
    audSound[i].setVolume(params['audVolume'])

# Declare constants
VIS = 0
AUD = 1
CHK = 2

# shuffle cues
if params['randomizeCues']:
    random.shuffle(params['cues'])

# ============================ #
# ======= SUBFUNCTIONS ======= #
# ============================ #

# increment time of next window flip
#def AddToFlipTime(tIncrement=1.0):
#    tNextFlip[0] += tIncrement

def RunBlock(params):
    
    # Get constants
    frameDur = 1.0/60.0 # duration of frame
    # get nFramesPerCheck
    nFramesPerCheck = 1.0/params['checkFreq']/frameDur
    print(nFramesPerCheck)
    
    # Display fixation cross
    win.clearBuffer()
    fixation.draw()
    win.logOnFlip(level=logging.EXP, msg='Display Fixation')
    win.flip()
    
    # set up block
    tStart = globalClock.getTime()
    tBlockEnd = tStart+params['blockDur']
    # set up visual & aud stim
    iAud = random.randint(0,len(params['audFiles'])-1)
    iVis = random.randint(0,len(params['visWords'])-1)
    text.setText(params['visWords'][iVis])
    isVisOn = False # visual stim is off
    iCheck = 0 # checkerboard is off
    iFrame = 0 # frame of checkerboard
    
    # set up trial times
    visITI = random.uniform(params['minVisITI'],params['maxVisITI'])
    audITI = random.uniform(params['minAudITI'],params['maxAudITI'])
    checkITI = random.uniform(params['minCheckITI'],params['maxCheckITI'])
    tNextVis = tStart+params['tStartup']+visITI
    tNextAud = tStart+params['tStartup']+audITI
    tNextCheck = tStart+params['tStartup']+checkITI
    tNextEvent = min(tNextVis,tNextAud,tNextCheck) # which comes first?
    
    # flush response buffer
    event.clearEvents()
    
    while (globalClock.getTime()<tBlockEnd):
            
        # Update statuses
        if (globalClock.getTime()>=tNextEvent):
            if (tNextEvent==tNextAud):
                audSound[iAud].play() # play sound now!
                audITI = random.uniform(params['minAudITI'],params['maxAudITI'])
                tNextAud += audITI # update time
                iAud = random.randint(0,len(audSound)-1) # index of sound to play (random)
            elif (tNextEvent==tNextVis):
                isVisOn = not isVisOn # switch!
                if (isVisOn): # just turned on
                    win.logOnFlip(level=logging.EXP, msg='Display %s'%(params['visWords'][iVis]))
                    tNextVis += params['visDur']
                else: # just turned off
                    win.logOnFlip(level=logging.EXP, msg='Display Fixation')
                    # determine next visual stimulus
                    iVis = random.randint(0,len(params['visWords'])-1)
                    text.setText(params['visWords'][iVis])
                    visITI = random.uniform(params['minVisITI'],params['maxVisITI'])
                    tNextVis += (visITI - params['visDur'])
            elif (tNextEvent==tNextCheck):
                if (iCheck==0): # off, turn it on
                    iCheck = 1 # display 1st checkerboard 1st
                    iFrame = 0 # restart frame count
                    tNextCheck += params['checkDur'] # set off time
                    # log change
                    win.logOnFlip(level=logging.EXP, msg='Display check%d'%(iCheck))
                else: # on, turn it off
                    iCheck = 0 # turn off check display
                    checkITI = random.uniform(params['minCheckITI'],params['maxCheckITI']) # set next on time
                    tNextCheck += (checkITI - params['checkDur'])
                    # log change
                    win.logOnFlip(level=logging.EXP, msg='Display NoCheck')
            # set up next event
            tNextEvent = min(tNextVis,tNextAud,tNextCheck) # which comes next?
            # check for escape keys
            thisKey = event.getKeys(keyList=['q','escape'])
            if thisKey!=None and len(thisKey)>0:
                core.quit()
        
        # alternate checkerboard
        if (iCheck>0):
            # draw
            if (iCheck==1):
                check1.draw()
            elif (iCheck==2):
                check2.draw()
            #increment frame number
            iFrame += 1
            if (iFrame==nFramesPerCheck):
                # switch checkerboard
                if (iCheck==1):
                    iCheck = 2
                elif (iCheck==2):
                    iCheck=1
                # restart count
                iFrame = 0
                # log change
                win.logOnFlip(level=logging.EXP, msg='Display check%d'%(iCheck))
                    
        # draw fixation or vis
        if (isVisOn):
            text.draw()
        else:
            fixation.draw()
            
        # flip window
        win.flip()


def RunCount(expectedCount,respKeys,duration):
    # set deadline
    tEnd = globalClock.getTime()+duration
    # Set up text
    message1.setText("What was your count? Use the buttons to change it upward or downward, then wait for the count to reach zero.")
    count = expectedCount
    tLeft = round(tEnd-globalClock.getTime())
    message2.setText("Count: %d    (%d seconds left.)"%(count,tLeft))
    win.logOnFlip(level=logging.EXP, msg='Display EnterCount')
    # allow guess while counting down
    while (globalClock.getTime()<tEnd):
        # update countdown clock
        tLeftNow = round(tEnd-globalClock.getTime())
        if (tLeftNow<tLeft): # if countdown has decreased
            tLeft = tLeftNow
            message2.setText("Count: %d    (%d seconds left.)"%(count,tLeft))
        # Check for new keypresses
        newKeys = event.getKeys(keyList=(respKeys+['q','escape']))
        # update count based on keypresses
        for thisKey in newKeys:
            if thisKey!=None and len(thisKey)>0:
                if thisKey in ['q','escape']:
                    core.quit()
                elif thisKey == respKeys[0]:
                    count -= 1
                elif thisKey == respKeys[1]:
                    count +=1
                # update display
                message2.setText("Count: %d    (%d seconds left.)"%(count,tLeft))
        message1.draw()
        message2.draw()
        win.flip()
    # get the count
    logging.log(level=logging.EXP, msg='count: %d'%count)
    return count


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
tNextFlip = tStartSession + params['tStartup']

# set up other stuff
logging.log(level=logging.EXP, msg='---START EXPERIMENT---')

# wait before first stimulus
fixation.draw()
win.logOnFlip(level=logging.EXP, msg='Display Fixation')
win.flip()


# =========================== #
# ===== MAIN EXPERIMENT ===== #
# =========================== #

# Get constants
meanVisIti = (params['minVisITI'] + params['maxVisITI']) / 2
expectedVisCount = 2.5*params['blockDur']/meanVisIti
meanAudIti = (params['minAudITI'] + params['maxAudITI']) / 2
expectedAudCount = 2.5*params['blockDur']/meanAudIti
nBlocks = len(params['cues'])

# Run trials
for iBlock in range(0,nBlocks-1): # for each block of pages
    
    while (globalClock.getTime()<tNextFlip):
        core.wait(0.0001)
    
    # log new block
    logging.log(level=logging.EXP, msg='Start Block %d'%iBlock)
    
    # display task cue
    text.setText(params['cues'][iBlock])
    text.draw()
    win.logOnFlip(level=logging.EXP, msg='Display Cue %s'%(params['cues'][iBlock]))
    win.flip()
    tNextFlip = globalClock.getTime() + params['cueDur']
    while (globalClock.getTime()<tNextFlip):
        core.wait(0.0001)
    win.flip()
    
    # Run the block!
    RunBlock(params)
    
    # get count
    print(params['cues'][iBlock])
    if (params['cues'][iBlock] =='Audio: Add'):
        RunCount(expectedAudCount,params['respKeys'],params['countDur'])
    elif (params['cues'][iBlock] =='Visual: Add'):
        RunCount(expectedVisCount,params['respKeys'],params['countDur'])
        
    # do IBI
    win.logOnFlip(level=logging.EXP, msg='Display IBI')
    win.flip()
    if iBlock<(nBlocks-1):
        tNextFlip = globalClock.getTime() + params['IBI']
    else:
        tNextFlip = globalClock.getTime() + params['tCoolDown']
        message1.setText("That's the end of this run!")
        message2.setText("Please stay still until the scanner noise stops.")
        win.logOnFlip(level=logging.EXP, msg='Display TheEnd')
        message1.draw()
        message2.draw()

# handle end of run
# wait until it's time
while (globalClock.getTime()<tNextFlip):
    core.wait(0.0001)
#        pass
# change the screen
win.flip()
# wait until a button is pressed to exit
thisKey = event.waitKeys(keyList=['q','escape'])

# exit experiment
core.quit()
