#!/usr/bin/env python2
"""Display a video lecture with interspersed thought probes.
Then ask the subject comprehension questions at the end."""
# VidLecTask.py
# Created 1/28/15 by DJ based on AuditorySartTask.py

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
newParamsFilename = 'DarkAgesTestParams_L2_inVrHall.pickle'

# Declare primary task parameters.
params = {
    'isPractice': False,      # give subject feedback when they get it wrong?
    'movieClipRanges': [[0, 44]],#[[1,210], [210,300], [300,480], [480,660], [660,990], [990,1200]], # times (in seconds) at which movie should start and stop in each block
    'IBI': 1,                 # time between end of block/probe and beginning of next block (in seconds)
    'probeDur': 7,            # max time subjects have to answer a Probe Q
    'keyEndsProbe': False,    # will a keypress end the probe?
    'wanderKey': 'z',         # key to be used to indicate mind-wandering
    'triggerKey': 't',        # key from scanner that says scan is starting
# declare movie and question files
    'movieDir': 'VideoLectures/',
    'movieFile': 'TheDarkAges_InVrHall.mp4', #'AncientGreece02-DarkAges.mov', #'Reverse_TheDarkAges.mp4', #
    'questionsFile': 'DarkAgesQuestions_30min_d2.txt', #'BLANK.txt', # 'DarkAgesQuestions.txt', #
    'probesFile': 'BLANK.txt', # 'VidLecProbes.txt', #
    'promptType': 'Test', # 'Attend', # 'Reverse', #     # option in PromptTools.GetPrompts (options are ['Test','Backwards','Wander','Attend'])
# declare other stimulus parameters
    'fullScreen': True,       # run in full screen mode?
    'screenToShow': 0,        # display on primary screen (0) or secondary (1)?
    'fixCrossSize': 10,       # size of cross, in pixels
    'movieVolume': 0.5,       # the volume (0-1) of the movie audio
    'movieSize': [854, 480] # [640,360]# [700, 500]   # width, height of movie (in pixels)
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

# Pilot-only parameters
skipDur = 20 # the time (in seconds) that you can skip back or forward by pressing < or >


# ========================== #
# ===== SET UP LOGGING ===== #
# ========================== #
try:#try to get a previous parameters file
    expInfo = fromFile('lastVidLecInfo.pickle')
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
toFile('lastVidLecInfo.pickle', expInfo)#save params to file for next time

#make a log file to save parameter/event  data
filename = 'VidLec-%s-%d-%s'%(expInfo['subject'], expInfo['session'], dateStr) #'Sart-' + expInfo['subject'] + '-' + expInfo['session'] + '-' + dateStr
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
# initialize video stimulus
mov = visual.MovieStim2(win, (params['movieDir']+params['movieFile']), size=params['movieSize'], name='Movie',
    pos=[0,0],flipVert=False,flipHoriz=False,loop=False)


# read questions and answers from text file
[questions_all,options_all,answers_all] = PromptTools.ParseQuestionFile(params['movieDir']+params['questionsFile'])
# declare probe parameters
[probe_strings, probe_options,_] = PromptTools.ParseQuestionFile(params['movieDir']+params['probesFile'])
# Look up prompts
[topPrompts,bottomPrompts] = PromptTools.GetPrompts(os.path.basename(__file__),params['promptType'],params)

# ============================ #
# ======= SUBFUNCTIONS ======= #
# ============================ #

def PlayMovie(startTime,stopTime):
    win.logOnFlip(level=logging.EXP, msg='Display Movie')
    shouldflip = mov.play()
    ntime = min(startTime, mov.duration)
    mov.seek(ntime)
    #Flush the key buffer and mouse movements
    event.clearEvents()
    while mov.status != visual.FINISHED and mov.getCurrentFrameTime()<stopTime:
        
        # Only flip when a new frame should be displayed. Can significantly reduce
        # CPU usage. This only makes sense if the movie is the only /dynamic/ stim
        # displayed.
        if shouldflip:
            # Movie has already been drawn , so just draw text stim and flip
            win.flip()
        else:
            # Give the OS a break if a flip is not needed
            time.sleep(0.001)
        # Drawn movie stim again. Updating of movie stim frames as necessary
        # is handled internally.
        shouldflip = mov.draw()

        # Check for action keys (stolen from MovieTest.py).....
        for key in event.getKeys():
            if key in ['escape', 'q']:
                win.close()
                core.quit()
            elif key in ['s',]:
                break
#                if mov.status in [visual.PLAYING, visual.PAUSED]:
#                    # To stop the movie being played.....
#                    mov.stop()
#                    # Clear screen of last displayed frame.
#                    win.flip()
#                    # When movie stops, clear screen of last displayed frame,
#                    # and display blank screen....
#                    win.flip()
#                else:
#                    # To replay a movie that was stopped.....
#                    mov.loadMovie(videopath)
#                    shouldflip = mov.play()
            elif key in ['p',]:
                # To pause the movie while it is playing....
                if mov.status == visual.PLAYING:
                    mov.pause()
                elif mov.status == visual.PAUSED:
                    # To /unpause/ the movie if pause has been called....
                    mov.play()
                    text.draw()
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
                cv = max(mov.getVolume()-5, 0)
                mov.setVolume(cv)
            elif key == 'equal':
                # To increase movie sound a bit ....
                cv = mov.getVolume()
                cv = min(mov.getVolume()+5, 100)
                mov.setVolume(cv)
    mov.pause()
    win.flip() # clear movie
    fixation.draw()
    win.logOnFlip(level=logging.EXP, msg='Display Fixation')
    win.flip()



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
blockTimes = params['movieClipRanges']
nBlocks = len(blockTimes)

for iBlock in range(0,nBlocks): # for each block of trials
    
    # log new block
    logging.log(level=logging.EXP, msg='Start Block %d'%iBlock)
    # play movie segment
    tStart = blockTimes[iBlock][0]
    tEnd = blockTimes[iBlock][1]
    PlayMovie(tStart,tEnd)
    # pause before probe
    core.wait(params['IBI'],params['IBI'])
    # run probes
    allKeys = PromptTools.RunQuestions(probe_strings,probe_options,win,message1,message2,'Probe',questionDur=params['probeDur'], isEndedByKeypress=params['keyEndsProbe'])
    # check for escape keypresses
    for thisKey in allKeys:
        if thisKey[0] in ['q', 'escape']: # check for quit keys
            core.quit()#abort experiment
    # tell the subject if the lecture is over.
    if iBlock == (nBlocks-1):
        message1.setText("That's the end! Now we'll ask you a few questions about what you heard in the lecture.")
        message2.setText("When you're ready to begin, press any key.")
        win.logOnFlip(level=logging.EXP, msg='Display QuestionTime')
        message1.draw()
        message2.draw()
        # change the screen
        win.flip()
        thisKey = event.waitKeys()
        if thisKey[0] in ['q', 'escape']:
            core.quit() #abort experiment
    # display fixation
    fixation.draw()
    win.logOnFlip(level=logging.EXP, msg='Display Fixation')
    win.flip()
    core.wait(params['IBI'],params['IBI'])
    
# Display the questions and record the answers.
allKeys = PromptTools.RunQuestions(questions_all,options_all,win,message1,message2,'Question')
# check for escape keypresses
for thisKey in allKeys:
    if thisKey[0] in ['q', 'escape']: # check for quit keys
        core.quit()#abort experiment
isCorrect = np.zeros(len(allKeys))
RT = np.zeros(len(allKeys))
print(allKeys)
for iKey in range(0,len(allKeys)):
    RT[iKey] = allKeys[iKey][1] # keep in seconds
    if allKeys[iKey][0] == answers_all[iKey]:
        isCorrect[iKey] = 1

#give some performance output to user
print('Performance:')
print('%d/%d = %.2f%% correct' %(np.sum(isCorrect), len(isCorrect), 100*np.average(isCorrect)))
print('RT: mean = %f, std = %f' %(np.average(RT),np.std(RT)))

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
