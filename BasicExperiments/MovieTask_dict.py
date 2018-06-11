#!/usr/bin/env python
"""Display a video lecture with interspersed thought probes.
Then ask the subject comprehension questions at the end."""
# MovieTask_dict.py
# Created 5/7/18 by DJ based on VidLecTask_dict.py

from psychopy import core, gui, data, event, sound, logging, visual # visual causes a bug in the guis, so I moved it down.
from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,
                                STOPPED, FINISHED, PRESSED, RELEASED, FOREVER)
from psychopy.tools.filetools import fromFile, toFile
import time
import numpy as np
import AppKit, os, sys # for monitor size detection, files
import PromptTools

# Ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__)).decode(sys.getfilesystemencoding())
os.chdir(_thisDir)

# ====================== #
# ===== PARAMETERS ===== #
# ====================== #
# Save the parameters declared below?
saveParams = True;
newParamsFilename = 'MovieTaskTest.pkl'

# Declare primary task parameters.
params = {
    'skipPrompts': False,     # go straight to trigger wait screen
    'movieClipRanges': [[0.0, 10.0]],#[[1,210], [210,300], [300,480], [480,660], [660,990], [990,1200]], # times (in seconds) at which movie should start and stop in each block
    'tStartup': 2,            # fixation cross time before starting movie
    'tCoolDown': 2,           # fixation cross time after ending movie
    'IBI': 0,                 # time between end of block/probe and beginning of next block (in seconds)
    'triggerKey': 't',        # key from scanner that says scan is starting
# declare visuals
    'movieDir': 'Movies/',
    'movieFile': 'Paperman.mp4', #'AncientGreece02-DarkAges.mov', #'Reverse_TheDarkAges.mp4', #
    'promptType': 'Watch', # 'Test',  # option in PromptTools.GetPrompts (options are ['Watch','Test'])
# declare other stimulus parameters
    'fullScreen': True,       # run in full screen mode?
    'screenToShow': 0,        # display on primary screen (0) or secondary (1)?
    'fixCrossSize': 10,       # size of cross, in pixels
    'movieVolume': 0.5,       # the volume (0-1) of the movie audio
    'movieSize': [640,360]# [854, 480] # [700, 500]   # width, height of movie (in pixels)
}

# save parameters
if saveParams:
    dlgResult = gui.fileSaveDlg(prompt='Save Params...',initFilePath = os.getcwd() + '/Params', initFileName = newParamsFilename,
        allowed="PICKLE files (*.pkl);;All files (*.*)")
    newParamsFilename = dlgResult
    if newParamsFilename is None: # keep going, but don't save
        saveParams = False
    else:
        print("Saving %s"%newParamsFilename)
        toFile(newParamsFilename, params)# save it!

# Pilot-only parameters
skipDur = 5.0 # the time (in seconds) that you can skip back or forward by pressing < or >


# ========================== #
# ===== SET UP LOGGING ===== #
# ========================== #
try:#try to get a previous parameters file
    expInfo = fromFile('lastMovieInfo.pkl')
    expInfo['session'] +=1 # automatically increment session number
    expInfo['paramsFile'] = [expInfo['paramsFile'],'Load...']
except:#if not there then use a default set
    expInfo = {'subject':'1', 'session':1, 'paramsFile':['DEFAULT','Load...']}
# overwrite if you just saved a new parameter set
if saveParams:
    expInfo['paramsFile'] = [newParamsFilename,'Load...']
dateStr = time.strftime("%b_%d_%H%M", time.localtime()) # add the current time

#present a dialogue to change params
dlg = gui.DlgFromDict(expInfo, title='Video Lecture task', order=['subject','session','paramsFile'])
if not dlg.OK:
    core.quit()#the user hit cancel so exit

# find parameter file
if expInfo['paramsFile'] == 'Load...':
    dlgResult = gui.fileOpenDlg(prompt='Select parameters file',tryFilePath=os.getcwd(),
        allowed="PICKLE files (*.pkl);;All files (*.*)")
    expInfo['paramsFile'] = dlgResult[0]
# load parameter file
if expInfo['paramsFile'] not in ['DEFAULT', None]: # otherwise, just use defaults.
    # load params file
    print("loading %s"%expInfo['paramsFile'])
#    params = fromFile(expInfo['paramsFile'])

# print params to Output
print 'params = {'
for key in sorted(params.keys()):
    print "   '%s': %s"%(key,params[key]) # print each value as-is (no quotes)
print '}'
    
# save experimental info
toFile('lastMovieInfo.pkl', expInfo)#save params to file for next time

#make a log file to save parameter/event  data
filename = 'Movie-%s-%d-%s'%(expInfo['subject'], expInfo['session'], dateStr) #'Sart-' + expInfo['subject'] + '-' + expInfo['session'] + '-' + dateStr
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
#from psychopy import visual

# Initialize deadline for displaying next frame
tNextFlip = [0.0] # put in a list to make it mutable (weird quirk of python variables) 

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
win = visual.Window(screenRes, fullscr=params['fullScreen'], allowGUI=False, monitor='testMonitor', screen=params['screenToShow'], units='deg', name='win',useFBO=True)
print(win) 
#fixation = visual.GratingStim(win, color='black', tex=None, mask='circle',size=0.2)
fCS = params['fixCrossSize'] # for brevity
fixation = visual.ShapeStim(win,lineColor='black',lineWidth=3.0,vertices=((-fCS/2,0),(fCS/2,0),(0,0),(0,fCS/2),(0,-fCS/2)),units='pix',closeShape=False,lineColorSpace='rgb');
message1 = visual.TextStim(win, pos=(0, 3), wrapWidth=30, color='black', alignHoriz='center', name='topMsg', text="aaa",colorSpace='rgb')
message2 = visual.TextStim(win, pos=(0,-3), wrapWidth=30, color='black', alignHoriz='center', name='bottomMsg', text="bbb",colorSpace='rgb')
# initialize video stimulus
#mov = visual.MovieStim(win, (params['movieDir']+params['movieFile']), size=params['movieSize'], name='Movie',
#    pos=[0,0],flipVert=False,flipHoriz=False,loop=False)
#mov = MovieStim2(win, (params['movieDir']+params['movieFile']), size=params['movieSize'], name='Movie',
#    pos=[0,0],flipVert=False,flipHoriz=False,loop=False)
mov = visual.MovieStim3(win=win, filename=params['movieDir']+params['movieFile'], name='Movie',
    pos=(0,0),flipVert=False,flipHoriz=False,loop=False,noAudio=False) # size=params['movieSize'], 
movieClock = core.Clock()
print(mov)

# Look up prompts
[topPrompts,bottomPrompts] = PromptTools.GetPrompts(os.path.basename(__file__),params['promptType'],params)

# ============================ #
# ======= SUBFUNCTIONS ======= #
# ============================ #

# increment time of next window flip
def AddToFlipTime(tIncrement=1.0):
    tNextFlip[0] += tIncrement

# flip window as soon as possible
def SetFlipTimeToNow():
    tNextFlip[0] = globalClock.getTime()

def PlayMovie(startTime,stopTime):
    # set up
    startTime = min(startTime, mov.duration)
    stopTime = min(stopTime, mov.duration)
    win.logOnFlip(level=logging.EXP, msg='Display Movie')
    # Wait until it's time to display
    while (globalClock.getTime()<tNextFlip[0]):
        pass
    # update clocks
    AddToFlipTime(stopTime-startTime) # advance the clock
    #Flush the key buffer and mouse movements
    event.clearEvents()
#    # start the movie
#    shouldflip = mov.play()
#    mov.seek(ntime)
    t = 0.0
    movieClock.reset()
    frameN = -1
    mov.status = NOT_STARTED
    tEnd = stopTime-startTime
    print(0)
    win.flip()
    print(1)
    # print('%f %f %f %f'%(mov.getCurrentFrameTime(), startTime,stopTime,ntime))
    while mov.status != FINISHED and t<tEnd:
        
        # get time
        t = movieClock.getTime()
        frameN = frameN + 1 # num of completed frames (0 is 1st frame)
        
        # movie updates
        if t>=0.0 and mov.status == NOT_STARTED:
            # keep track of start time/frame for later
            mov.tStart = t
            mov.frameNStart = frameN # exact frame index
            mov.setAutoDraw(True)
        frameRemains = tEnd - win.monitorFramePeriod * 0.75 # most of 1 frame period left
        if mov.status == STARTED and t >= frameRemains:
            mov.setAutoDraw(False)
            
        # Check for action keys (stolen from MovieTest.py).....
        for key in event.getKeys():
            if key in ['escape', 'q']:
                # End the experiment.
                win.close()
                core.quit()
            elif key in ['s',]:
                # Stop this trial.
                break
            elif key in ['p',]:
                # To pause the movie while it is playing....
                if mov.status == PLAYING:
                    mov.pause()
                    mov.setAutoDraw(False)
                elif mov.status == PAUSED:
                    # To /unpause/ the movie if pause has been called....
                    mov.play()
                    mov.setAutoDraw(True)
                    win.flip()
            elif key == 'period':
                # To skip ahead 1 second in movie.
                ntime = min(mov.getCurrentFrameTime()+skipDur, mov.duration)
                mov.seek(ntime)
            elif key == 'comma':
                # To skip back 1 second in movie ....
                ntime = max(mov.getCurrentFrameTime()-skipDur,0.0)
                mov.seek(ntime)
            elif key == 'minus':
                # To decrease movie sound a bit ....
                cv = max(mov.getVolume()-0.05, 0)
                mov.setVolume(cv)
            elif key == 'equal':
                # To increase movie sound a bit ....
                cv = mov.getVolume()
                cv = min(mov.getVolume()+0.05, 1.0)
                mov.setVolume(cv)
                
        # Draw new frame if everything's good
        if mov.status != FINISHED:
            print(2)
            # draw frame
            win.flip()
    # Pause movie
#    mov.pause()
    mov.setAutoDraw(False)
#    win.flip() # clear movie


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
blockTimes = params['movieClipRanges']
nBlocks = len(blockTimes)

for iBlock in range(0,nBlocks): # for each block of trials
    # log new block
    logging.log(level=logging.EXP, msg='Start Block %d'%iBlock)
    # extract start/end times
    tStart = blockTimes[iBlock][0]
    tEnd = blockTimes[iBlock][1]
    # play movie segment
    PlayMovie(tStart,tEnd)
    
    # display fixation
    fixation.draw()
    win.logOnFlip(level=logging.EXP, msg='Display Fixation')
    # Wait until it's time to display
    while (globalClock.getTime()<tNextFlip[0]):
        # check for escape character
        for key in event.getKeys():
            if key in ['escape', 'q']:
                core.quit()
    # show new display
    win.flip()
    # set up pause
    if iBlock<(nBlocks-1):
        AddToFlipTime(params['IBI'])
    else:
        AddToFlipTime(params['tCoolDown'])


# display cool-down message
message1.setText("That's the end! Please stay still until the scan is complete.")
message2.setText("(Experimenter: press 'q' or 'escape' to override.)")
win.logOnFlip(level=logging.EXP, msg='Display TheEnd')
message1.draw()
message2.draw()
# Wait until it's time to display
while (globalClock.getTime()<tNextFlip[0]):
    # check for escape character
    for key in event.getKeys():
        if key in ['escape', 'q']:
            core.quit()
win.flip()
thisKey = event.waitKeys(['q','escape'])

# exit experiment
core.quit()
