 #!/usr/bin/env python2
"""Display multi-page text with simultaneous auditory distractions, recording eye position data using the SMI eye tracker."""
# DistractionTask_serial_d6.py
# Created 3/16/15 by DJ based on VidLecTask.py
# Updated 3/31/15 by DJ - renamed from ReadingTask_dict_d2.py.
# Updated 4/1-16/15 by DJ - incorporated eyelink fully, renamed ReadingTask_eyelink_d1.py.
# Updated 4/16/15 by DJ - removed questions, added randomized thought probes and automatic pick up where you left off.
# Updated 4/17/15 by DJ - removed Eyelink again to have same behavioral version
# Updated 6/29/15 by DJ - removed random session length ranges and probe times - page ranges specified in params. 
# Updated 7/7/15 by DJ - Renamed from ReadingImageTask_dict_d4, added audio.
# Updated 7/15/15 by DJ - added sound time limits
# Updated 7/20/15 by DJ - switched to premade sound files, switched back to eyelink version, debugged
# Updated 7/24/15 by DJ - added quiz files list, imagePrefix list, readingQuiz list and audioQuiz list
# Updated 7/28/15 by DJ - made sounds play on page-by-page basis, sound is randomized, 
# Updated 8/18/15 by DJ - added serial port (and changed name from _behavior to _serial), but haven't tried it yet.
# Updated 8/21/15 by DJ - tested in 3T-C and debugged as necessary
# Updated 9/17/15 by DJ - added logging of each message sent
# Updated 10/22/15 by DJ - added saving
# Updated 10/29/15 by DJ - cleaned up slightly, edited PromptTools to ask subjects not to skip around.
# Updated 11/11/15 by DJ - added additional calibration parameters (changed name to _d6)
# Updated 11/12/15 by DJ - switched to 1024x768 (max res of rear projector)

# Import packages
from psychopy import core, gui, data, event, sound, logging #, visual # visual causes a bug in the guis, so I moved it down.
from psychopy.tools.filetools import fromFile, toFile
import time as ts, numpy as np
import AppKit, os # for monitor size detection, files
import PromptTools
import random
import serial 
from LibSmi_PsychoPy import LibSmi_PsychoPy
"""
# import eyelink's libraries
from pylink import *
from EyeLinkCoreGraphicsPsychoPy import EyeLinkCoreGraphicsPsychoPy
"""

# ====================== #
# ===== PARAMETERS ===== #
# ====================== #
# Save the parameters declared below?
saveParams = True
newParamsFilename = 'DistractionParams_serial_d6.pickle'
expInfoFilename = 'lastDistractionInfo_serial_d6.pickle'

# Declare primary task parameters.
params = {
    # FOR INITIAL PILOTS
    'imagePrefixList': ['Greeks_Lec02_stretch_gray','Greeks_Lec02_stretch_gray','Greeks_Lec02_stretch_gray','Greeks_Lec02_stretch_gray','Greeks_Lec07_stretch_gray','Greeks_Lec07_stretch_gray'],
    'startPageList': [1,31,61,91,1,31], # page where each session should start
    'endPageList': [30,60,90,120,30,60], # inclusive
    'readingQuizList':['Lecture02Questions_d4_read1.txt','Lecture02Questions_d4_read2.txt','Lecture02Questions_d4_read3.txt','Lecture02Questions_d4_read4.txt','Lecture07Questions_d3_read1.txt','Lecture07Questions_d3_read2.txt',],
    'soundFileList': ['Lecture10_40min.wav']*6,
#    'imagePrefixList': ['Greeks_Lec07_stretch_gray','Greeks_Lec07_stretch_gray','Greeks_Lec10_stretch_gray','Greeks_Lec10_stretch_gray','Greeks_Lec02_stretch_gray','Greeks_Lec02_stretch_gray'],
#    'startPageList': [1,31,1,31,61,91], # page where each session should start
#    'endPageList': [30,60,30,60,90,120], # inclusive
#    'soundFileList': ['Lecture02_40min.wav']*6,
#    'readingQuizList':['Lecture07Questions_d3_read1.txt','Lecture07Questions_d3_read2.txt','Lecture10Questions_d4_read1.txt','Lecture10Questions_d4_read2.txt','Lecture02Questions_d4_read3.txt','Lecture02Questions_d4_read4.txt'],
#    'soundFileList': ['Lecture02_40min.wav']*6,
    'promptTypeList': ['AttendReading','AttendBoth_short','AttendReading_short','AttendBoth_short','AttendBoth_short','AttendReading_short'],
    'soundQuizList':['BLANK.txt']*6,
    'quizPromptList':['TestReading_box']*6,
    'probSoundList':[0.5]*6,
    # REST OF PARAMS
    'skipPrompts': False,    # go right to the scanner-wait page
    'maxPageTime': 14,        # max time the subject is allowed to read each page (in seconds)
    'pageFadeDur': 3,         # for the last pageFadeDur seconds, the text will fade to white.
    'IPI': 2,                 # time between when one page disappears and the next appears (in seconds)
    'probSound': 0.5,         # probability that sound will be played on any given page
    'IBI': 1,                 # time between end of block/probe and beginning of next block (in seconds)
    'tStartup': 2,            # pause time before starting first page
    'probeDur': 60,           # max time subjects have to answer a Probe Q
    'keyEndsProbe': True,     # will a keypress end the probe?
    'pageKey': 'b',#'space',       # key to turn page
    'respKeys': ['g','r','b','y'], # keys to be used for responses (clockwise from 9:00) - "DIAMOND" RESPONSE BOX
    'wanderKey': 'z',         # key to be used to indicate mind-wandering
    'triggerKey': 't',        # key from scanner that says scan is starting
# declare image and question files
    'imageDir': 'ReadingImages/',
    'imagePrefix': '', # images must start with this and end with _page<number>.jpg
    'soundDir': 'sounds/',
    'soundFile': '', # fill in later
    'promptType': '', # fill in later
    'soundVolume': 0.5,
    'whiteNoiseFile': 'Lecture10_40min_phasescrambled.wav', #'WhiteNoise-7m30s.wav', # this plays when the lecture doesn't.
    'pageRange': [1, 1], # pages (starting from 1) at which reading should start and stop in each block
    'textDir': 'questions/', # directory containing questions and probes
    'probesFile': 'BLANK.txt', #'ReadingProbes_d2.txt', #'ReadingProbes_behavior.txt', #
    'readingQuiz':'', # fill in later
    'soundQuiz':'', # fill in later
    'quizPrompt':'', # fill in later
    'questionOrder':[], # fill in later
# declare other stimulus parameters
    'fullScreen': True,       # run in full screen mode?
    'screenToShow': 1,        # display on primary screen (0) or secondary (1)?
    'imageSize': (960,709), # (FOR 1024x768 SCREEN) # in pixels... set to None for exact size of screen    #(1201,945), # (FOR 1280x1024 SCREEN)
    'fixCrossSize': 10,       # size of cross, in pixels
    'fixCrossPos': (-480,354), # (x,y) pos of fixation cross displayed before each page (for drift correction)   #[-600, 472],
    'usePhotodiode': False,     # add sync square in corner of screen
# declare serial port & calibration parameters
    'portName': '/dev/tty.usbserial',
    'portBaud': 115200,
    'screenColor':(128,128,128),
    'calNPoints': 13, # number of points in the calibration (and validation)The number of points to be used for the validation (standard=9)
    'calAutoAccept': False, # Let SMI pick when to accept a point (True [default]) or accept manually (False).
    'calGoFast': False, # Go quickly from point to point (True) or slower and more precise (False [default]).
    'calCheckLevel': 3 #calibration check level (0=none,1=weak,2=medium,3=strong [default])
}

# save parameters
if saveParams:
    print("Opening save dialog:")
    dlgResult = gui.fileSaveDlg(prompt='Save Params...',initFilePath = os.getcwd() + '/params', initFileName = newParamsFilename,
        allowed="PICKLE files (.pickle)|.pickle|All files (.*)|")
    newParamsFilename = dlgResult
    print("dlgResult: %s"%dlgResult)
    if newParamsFilename is None: # keep going, but don't save
        saveParams = False
        print("Didn't save params.")
    else:
        toFile(newParamsFilename, params)# save it!
        print("Saved params to %s."%newParamsFilename)
#    toFile(newParamsFilename, params)
#    print("saved params to %s."%newParamsFilename)

# ========================== #
# ===== SET UP LOGGING ===== #
# ========================== #
try:#try to get a previous parameters file
    expInfo = fromFile(expInfoFilename)
    expInfo['session'] +=1 # automatically increment session number
    expInfo['paramsFile'] = [expInfo['paramsFile'],'Load...']
except:#if not there then use a default set
    expInfo = {'subject':'1', 'session':1, 'skipPrompts':False, 'tSound':0.0, 'paramsFile':['DEFAULT','Load...']}
# overwrite if you just saved a new parameter set
if saveParams:
    expInfo['paramsFile'] = [newParamsFilename,'Load...']
dateStr = ts.strftime("%b_%d_%H%M", ts.localtime()) # add the current time

#present a dialogue to change params
dlg = gui.DlgFromDict(expInfo, title='Distraction task', order=['subject','session','skipPrompts','paramsFile'])
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

# GET NEW START AND STOP PAGES
params['pageRange'][0] = params['startPageList'][expInfo['session']-1] # use session-1 as index of list
params['pageRange'][1] = params['endPageList'][expInfo['session']-1] # use session-1 as index of list
# GET SOUND FILE AND OTHER SESSION-DEPENDENT INFO
params['soundFile'] = params['soundFileList'][expInfo['session']-1]
params['promptType'] = params['promptTypeList'][expInfo['session']-1]
params['imagePrefix'] = params['imagePrefixList'][expInfo['session']-1]
params['readingQuiz'] = params['readingQuizList'][expInfo['session']-1]
params['soundQuiz'] = params['soundQuizList'][expInfo['session']-1]
params['quizPrompt'] = params['quizPromptList'][expInfo['session']-1]
params['probSound'] = params['probSoundList'][expInfo['session']-1]
tSound = expInfo['tSound']

# transfer skipPrompts
params['skipPrompts'] = expInfo['skipPrompts']

# read questions and answers from text files
[questions_reading,options_reading,answers_reading] = PromptTools.ParseQuestionFile(params['textDir']+params['readingQuiz'])
print('%d questions loaded from %s'%(len(questions_reading),params['readingQuiz']))
[questions_sound,options_sound,answers_sound] = PromptTools.ParseQuestionFile(params['textDir']+params['soundQuiz'])
print('%d questions loaded from %s'%(len(questions_sound),params['soundQuiz']))
# append the two
questions_all = questions_reading + questions_sound
options_all = options_reading + options_sound
answers_all = answers_reading + answers_sound
# shuffle the order
newOrder = range(0,len(questions_all))
random.shuffle(newOrder)
questions_all = [questions_all[i] for i in newOrder]
options_all = [options_all[i] for i in newOrder]
answers_all = [answers_all[i] for i in newOrder]
params['questionOrder'] = newOrder


# ========================== #
# ===== GET SCREEN RES ===== #
# ========================== #

# kluge for secondary monitor
if params['fullScreen']: 
    screens = AppKit.NSScreen.screens()
    screenRes = (int(screens[params['screenToShow']].frame().size.width), int(screens[params['screenToShow']].frame().size.height))
#    screenRes = (1920, 1200)
    if params['screenToShow']>0:
        params['fullScreen'] = False
else:
    screenRes = (1024,768)

# save screen size to params struct 
params['screenSize'] = screenRes

# adjust image size if one was not entered.
if params['imageSize'] is None:
    params['imageSize'] = (screenRes[0], screenRes[1])
    
    
# ========================== #
# ===== LOG PARAMETERS ===== #
# ========================== #

# print params to Output
print 'params = {'
for key in sorted(params.keys()):
    print "   '%s': %s"%(key,params[key]) # print each value as-is (no quotes)
print '}'

#make a log file to save parameter/event  data
filename = 'DistractionTask-%s-%d-%s'%(expInfo['subject'], expInfo['session'], dateStr) #'Sart-' + expInfo['subject'] + '-' + expInfo['session'] + '-' + dateStr
logging.LogFile((filename+'.log'), level=logging.INFO)#, mode='w') # w=overwrite
logging.log(level=logging.INFO, msg='---START PARAMETERS---')
logging.log(level=logging.INFO, msg='filename: %s'%filename)
logging.log(level=logging.INFO, msg='subject: %s'%expInfo['subject'])
logging.log(level=logging.INFO, msg='session: %s'%expInfo['session'])
logging.log(level=logging.INFO, msg='date: %s'%dateStr)
logging.log(level=logging.INFO, msg='tSound: %s'%expInfo['tSound'])
for key in sorted(params.keys()): # in alphabetical order
    logging.log(level=logging.INFO, msg='%s: %s'%(key,params[key]))

logging.log(level=logging.INFO, msg='---END PARAMETERS---')
# ========================== #
# ===== SET UP TRACKER ===== #
# ========================== #

# Set up serial port by declaring LibSmi object
myTracker = LibSmi_PsychoPy(experiment='DistractionTask_serial_d4',port=params['portName'], baudrate=params['portBaud'], useSound=True, w=screenRes[0], h=screenRes[1], bgcolor=params['screenColor'],fullScreen=params['fullScreen'],screenToShow=params['screenToShow'])
print "Port %s isOpen = %d"%(myTracker.tracker.name,myTracker.tracker.isOpen())


# ========================== #
# ===== SET UP STIMULI ===== #
# ========================== #
from psychopy import visual

# Initialize deadline for displaying next frame
tNextFlip = [0.0] # put in a list to make it mutable? 

#create clocks and window
globalClock = core.Clock()#to keep track of time
trialClock = core.Clock()#to keep track of time
#win = visual.Window(screenRes, fullscr=params['fullScreen'], allowGUI=False, monitor='testMonitor', screen=params['screenToShow'], units='deg', name='win',rgb=[1,1,1])
win = myTracker.win
"""
win = genv.win # eyelink version
"""
# create stimuli
fCS = params['fixCrossSize'] # size (for brevity)
fCP = params['fixCrossPos'] # position (for brevity)
fixation = visual.ShapeStim(win,lineColor='#000000',lineWidth=3.0,vertices=((fCP[0]-fCS/2,fCP[1]),(fCP[0]+fCS/2,fCP[1]),(fCP[0],fCP[1]),(fCP[0],fCP[1]+fCS/2),(fCP[0],fCP[1]-fCS/2)),units='pix',closeShape=False,name='fixCross');
message1 = visual.TextStim(win, pos=[0,+.5], wrapWidth=1.5, color='#000000', alignHoriz='center', name='topMsg', text="aaa",units='norm')
message2 = visual.TextStim(win, pos=[0,-.5], wrapWidth=1.5, color='#000000', alignHoriz='center', name='bottomMsg', text="bbb",units='norm')

# initialize main text stimulus
imageName = '%s%s/%s_page%d.jpg'%(params['imageDir'],params['imagePrefix'],params['imagePrefix'],1)
textImage = visual.ImageStim(win, pos=[0,0], name='Text',image=imageName, units='pix', size=params['imageSize'])

# initialize photodiode stimulus
squareSize = 0.4
diodeSquare = visual.Rect(win,pos=[squareSize/4-1,squareSize/4-1],lineColor='white',fillColor='black',size=[squareSize,squareSize],units='norm',name='diodeSquare')

# declare probe parameters
[probe_strings, probe_options,_] = PromptTools.ParseQuestionFile(params['textDir']+params['probesFile'])
print('%d probes loaded from %s'%(len(probe_strings),params['probesFile']))
# Look up prompts
[topPrompts,bottomPrompts] = PromptTools.GetPrompts(os.path.basename(__file__),params['promptType'],params)
print('%d prompts loaded from %s'%(len(topPrompts),'PromptTools.py'))
# Look up question prompts
[topQuizPrompts,bottomQuizPrompts] = PromptTools.GetPrompts(os.path.basename(__file__),params['quizPrompt'],params)
print('%d prompts loaded from %s'%(len(topPrompts),'PromptTools.py'))


# declare sound!
# fullSound = sound.Sound(value='%s%s'%(params['soundDir'], params['soundFile']), volume=params['soundVolume'], name='fullSound')
pageSound = sound.Sound(value='%s%s'%(params['soundDir'], params['soundFile']), volume=params['soundVolume'], start=tSound, stop=tSound+params['maxPageTime'], name='pageSound')
whiteNoiseSound = sound.Sound(value='%s%s'%(params['soundDir'], params['whiteNoiseFile']), volume=params['soundVolume'], start=0, stop=params['maxPageTime'], name='whiteNoiseSound')

# ============================ #
# ======= SUBFUNCTIONS ======= #
# ============================ #

# increment time of next window flip
def AddToFlipTime(tIncrement=1.0):
    tNextFlip[0] += tIncrement
#    print("%1.3f --> %1.3f"%(globalClock.getTime(),tNextFlip[0]))

def SetFlipTimeToNow():
    tNextFlip[0] = globalClock.getTime()

def SendMessage(message):
    # send message preceded by SMI code ET_REM (generic remark) and surround multi-word remarks by quotes(?)
    myTracker.log(message)
    logging.log(level=logging.INFO,msg=message)
#    pass
    """
    if eyelinktracker is None:
        print('MSG: %s'%message)
    else:
        getEYELINK().sendMessage(message)
    """
    
    
def ShowPage(iPage, maxPageTime=float('Inf'), pageFadeDur=0, soundToPlay=None):
    
    print('Showing Page %d'%iPage)
    """
    # Start EyeLink's RealTime mode
    pylink.beginRealTimeMode(100)
    """
    
    # Display text
    imageName = '%s%s/%s_page%d.jpg'%(params['imageDir'],params['imagePrefix'],params['imagePrefix'],iPage)
    textImage.setImage(imageName)
    textImage.opacity = 1
    textImage.draw()
    while (globalClock.getTime()<tNextFlip[0]):
        pass
#        win.flip(clearBuffer=False)
    # draw & flip
    win.logOnFlip(level=logging.EXP, msg='Display Page%d'%iPage)
#    win.callOnFlip(SendMessage,'Display Page%d'%iPage)
    win.callOnFlip(SendMessage,'DisplayPage%d'%iPage) # CHANGED FOR SMI
    AddToFlipTime(maxPageTime)
#    win.callOnFlip(SendPortEvent,mod(page,256))
    if params['usePhotodiode']:
        diodeSquare.draw()
        win.flip()
        # erase diode square and re-draw
        textImage.draw()
    win.flip()
    
    # get time at which page was displayed
    pageStartTime = globalClock.getTime()
    # Play sound just after window flips
    if soundToPlay is not None:
        soundToPlay.play()
    
    # Flush the key buffer and mouse movements
    event.clearEvents()
    # Wait for relevant key press or 'maxPageTime' seconds
    fadeTime = tNextFlip[0]-pageFadeDur
    respKey = None
    while (globalClock.getTime()<tNextFlip[0]) and respKey==None:
        newKeys = event.getKeys(keyList=[params['pageKey'],params['wanderKey'],'q','escape'],timeStamped=globalClock)
        if len(newKeys)>0:
            for thisKey in newKeys:
                if thisKey[0] in ['q','escape']:
                    CoolDown()
                elif thisKey[0] == params['pageKey']:
                    respKey = thisKey
                    SetFlipTimeToNow() # reset flip time
        now = globalClock.getTime()
        if now > fadeTime:
            textImage.opacity = (tNextFlip[0]-now)/pageFadeDur
            textImage.draw()
            win.flip()
    
    """
    # Stop EyeLink's RealTime mode
    pylink.endRealTimeMode()
    """
    
    # Display the fixation cross
    if params['IPI']>0:
        fixation.draw()
        win.logOnFlip(level=logging.EXP, msg='Display Fixation')
        win.callOnFlip(SendMessage,'DisplayFixation')
        if params['usePhotodiode']:
            diodeSquare.draw()
            win.flip()
            # erase diode square and re-draw
            fixation.draw()
        win.flip()
    
    # return time for which page was shown
    pageDur = tNextFlip[0] - pageStartTime
    return pageDur

# Handle end ofeyelink session
def CoolDown():
    
    # display cool-down message
    message1.setText("That's the end! ")
    message2.setText("Press 'q' or 'escape' to end the session.")
    win.logOnFlip(level=logging.EXP, msg='Display TheEnd')
    win.callOnFlip(SendMessage,'DisplayTheEnd')
    message1.draw()
    message2.draw()
    win.flip()
    thisKey = event.waitKeys(keyList=['q','escape'])
    
    # stop recording via serial port
    myTracker.stop_recording()
    
    # save result
    myTracker.save_data(path=(filename+'.idf'))
    
    # close serial port
    myTracker.cleanup()
    
    """
    # End recording: add 100 msec of data to catch final events
    pylink.endRealTimeMode()
    pumpDelay(100)
    getEYELINK().stopRecording()
    while getEYELINK().getkey(): # not sure what this is for
        pass
    
    # File transfer and cleanup!
    getEYELINK().setOfflineMode()                          
    msecDelay(500)                 
    
    message1.setText("Sending EyeLink File...")
    message2.setText("Please Wait.")
    win.logOnFlip(level=logging.EXP, msg='Display SendingFile')
    message1.draw()
    message2.draw()
    win.flip()
    #Close the file and transfer it to Display PC
    getEYELINK().closeDataFile()
    getEYELINK().receiveDataFile(edfHostFileName, edfFileName)
    getEYELINK().close();
    
    #Close the experiment graphicss
    pylink.closeGraphics()
    """
    
    # stop sound
#    fullSound.stop()
    whiteNoiseSound.stop()
    pageSound.stop()
    
    # save experimental info (if we reached here, we didn't have an error)
    expInfo['tSound'] = tSound
    toFile(expInfoFilename, expInfo) # save params to file for next time
    
    # exit
    core.quit()


# =========================== #
# ======= RUN PROMPTS ======= #
# =========================== #

"""
#Do the tracker setup at the beginning of the experiment.
getEYELINK().doTrackerSetup()

# START RECORDING
error = getEYELINK().startRecording(1, 1, 1, 1)
if error:
    print("===WARNING: eyelink startRecording returned %s"%error)
"""
# run calibration and validation
myTracker.run_calibration(nr_of_pts=params['calNPoints'], auto_accept=params['calAutoAccept'], go_fast=params['calGoFast'], calib_level=params['calCheckLevel'])

# display prompts
if not params['skipPrompts']:
    PromptTools.RunPrompts(topPrompts,bottomPrompts,win,message1,message2)

# wait for scanner
message1.setText("Waiting for scanner to start...")
message2.setText("(Press '%c' to override.)"%params['triggerKey'].upper())
message1.draw()
message2.draw()
win.logOnFlip(level=logging.EXP, msg='Display WaitingForScanner')
win.callOnFlip(SendMessage,'DisplayWaitingForScanner')
win.flip()
event.waitKeys(keyList=params['triggerKey'])
tStartSession = globalClock.getTime()
AddToFlipTime(tStartSession+params['tStartup'])

# start recording via serial port
myTracker.start_recording(stream=False)

# wait before first stimulus
fixation.draw()
win.logOnFlip(level=logging.EXP, msg='Display Fixation')
win.callOnFlip(SendMessage,'DisplayFixation')
win.flip()


# =========================== #
# ===== MAIN EXPERIMENT ===== #
# =========================== #


# set up other stuff
logging.log(level=logging.EXP, msg='---START EXPERIMENT---')
nBlocks = 1
# start sound
#fullSound.play()
# Run trials
for iBlock in range(0,nBlocks): # for each block of pages
    
    # log new block
    logging.log(level=logging.EXP, msg='Start Block %d'%iBlock)
    # display pages
    for iPage in range(params['pageRange'][0],params['pageRange'][1]+1): # +1 to inclue final page
        # decide on sound
        if random.random()<=params['probSound']:
            playSound = True
            soundToPlay = pageSound
        else:
            playSound = False
            soundToPlay = whiteNoiseSound
        # display text
        pageDur = ShowPage(iPage=iPage,maxPageTime=params['maxPageTime'],pageFadeDur=params['pageFadeDur'],soundToPlay=soundToPlay)
        # update sound
        soundToPlay.stop()
        if playSound:
            tSound += pageDur #params['maxPageTime']
            logging.log(level=logging.INFO, msg='tSound: %.3f'%tSound)
            pageSound = sound.Sound(value='%s%s'%(params['soundDir'], params['soundFile']), volume=params['soundVolume'], start=tSound, stop=tSound+params['maxPageTime'], name='pageSound')
        
        if iPage < params['pageRange'][1]:
            # pause
            AddToFlipTime(params['IPI'])
        
    # Mute Sounds
    pageSound.setVolume(0) # mute but don't stop... save stopping for CoolDown!
    whiteNoiseSound.setVolume(0) # mute but don't stop... save stopping for CoolDown!
    # Pause recording via serial port
    myTracker.pause_recording() # save stop command for CoolDown.
    
#    fullSound.setVolume(0)
    # run probes
    allKeys = PromptTools.RunQuestions(probe_strings,probe_options,win,message1,message2,'Probe',questionDur=params['probeDur'], isEndedByKeypress=params['keyEndsProbe'])
    # check for escape keypresses
    for thisKey in allKeys:
        if len(thisKey)>0 and thisKey[0] in ['q', 'escape']: # check for quit keys
            CoolDown()#abort experiment
    # tell the subject if the lecture is over.
    message1.setText("It's time for some questions! Then, after a short break, we'll continue reading where you left off.")
    message2.setText("Press any key to end this recording.")
    win.logOnFlip(level=logging.EXP, msg='Display TakeABreak')
    win.callOnFlip(SendMessage,'DisplayTakeABreak')
    message1.draw()
    message2.draw()
    # change the screen
    win.flip()
    thisKey = event.waitKeys() # any keypress will end the session



# ============================ #
# ========= RUN QUIZ ========= #
# ============================ #
# display prompts
if not params['skipPrompts']:
    PromptTools.RunPrompts(topQuizPrompts,bottomQuizPrompts,win,message1,message2)

# set up other stuff
logging.log(level=logging.EXP, msg='---START QUIZ---')

# ------- Run the questions ------- #
allKeys = PromptTools.RunQuestions(questions_all,options_all,win,message1,message2,'Question',respKeys=params['respKeys'])
# --------------------------------- #

isResponse = np.zeros(len(allKeys),dtype=bool) # was any response given?
isCorrect = np.zeros(len(allKeys)) # was the response correct?
RT = np.zeros(len(allKeys)) # how long did it take them to press a key?
#print(allKeys)
for iKey in range(0,len(allKeys)):
    if len(allKeys[iKey])>0:
        isResponse[iKey] = 1
        RT[iKey] = allKeys[iKey][1] # keep in seconds
        if float(allKeys[iKey][0]) == answers_all[iKey]:
            isCorrect[iKey] = 1


#give some performance output to user
print('Performance:')
print('%d/%d = %.2f%% correct' %(np.sum(isCorrect), len(isCorrect), 100*np.average(isCorrect)))
print('RT: mean = %f, std = %f' %(np.average(RT[isResponse]),np.std(RT[isResponse])))


# exit experiment
CoolDown()
