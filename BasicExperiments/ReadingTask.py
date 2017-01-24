#!/usr/bin/env python2
"""Display multi-page text with interspersed thought probes.
Then ask the subject comprehension questions at the end."""
# ReadingTask.py
#
# Created 3/16/15 by DJ based on VidLecTask.py - named ReadingTask_dict_d2.py
# Updated 1/24/17 by DJ - renamed and debugged

from psychopy import core, gui, data, event, sound, logging #, visual # visual causes a bug in the guis, so I moved it down.
from psychopy.tools.filetools import fromFile, toFile
import time, numpy as np
import AppKit, os # for monitor size detection, files
import PromptTools
import ParseReading

# ====================== #
# ===== PARAMETERS ===== #
# ====================== #
# Save the parameters declared below?
saveParams = True;
newParamsFilename = 'ReadingTestParams_L2.pickle'

# Declare primary task parameters.
params = {
    'isPractice': False,      # give subject feedback when they get it wrong?
    'skipPrompts': False,      # go right to the scanner-wait page
    'pageRanges': [[0, 9],[10,19]],#[[1,210], [210,300], [300,480], [480,660], [660,990], [990,1200]], # pages (starting from 0) at which reading should start and stop in each block
    'maxPageTime': 10,        # max time the subject is allowed to read each page (in seconds)
    'IPI': 0,                 # time between when one page disappears and the next appears (in seconds)
    'IBI': 1,                 # time between end of block/probe and beginning of next block (in seconds)
    'tStartup': 3,            # pause time before starting first page
    'probeDur': 7,            # max time subjects have to answer a Probe Q
    'keyEndsProbe': True,    # will a keypress end the probe?
    'pageKey': 'space',       # key to turn page
    'wanderKey': 'z',         # key to be used to indicate mind-wandering
    'triggerKey': 't',        # key from scanner that says scan is starting
# declare movie and question files
    'textDir': 'VideoLectures/',
    'textFile': 'Greeks_Lec02_transcript_pages.txt', #'Greeks-Lec07-transcript.txt', #'Greeks-Lec10-transcript.txt', #
    'questionsFile': 'DarkAgesQuestions_30min_d2.txt', #'BLANK.txt', # 'DarkAgesQuestions.txt', #
    'probesFile': 'ReadingProbes.txt', # 'BLANK.txt', #
    'promptType': 'Test', # 'Attend', # 'Reverse', #     # option in PromptTools.GetPrompts (options are ['Test','Backwards','Wander','Attend'])
    'respKeys': ['1','2','3','4','5'], # keys the subject can press in response to the probes
# declare other stimulus parameters
    'fullScreen': True,       # run in full screen mode?
    'screenToShow': 0,        # display on primary screen (0) or secondary (1)?
    'fixCrossSize': 10,       # size of cross, in pixels
    'fixCrossPos': (-490,300), # (x,y) pos of fixation cross displayed before each page (for drift correction)
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
    expInfo = fromFile('lastReadingInfo.pickle')
    expInfo['session'] +=1 # automatically increment session number
    expInfo['paramsFile'] = [expInfo['paramsFile'],'Load...']
except:#if not there then use a default set
    expInfo = {'subject':'1', 'session':1, 'paramsFile':['DEFAULT','Load...']}
# overwrite if you just saved a new parameter set
if saveParams:
    expInfo['paramsFile'] = [newParamsFilename,'Load...']
dateStr = time.strftime("%b_%d_%H%M", time.localtime()) # add the current time

#present a dialogue to change params
dlg = gui.DlgFromDict(expInfo, title='Reading task', order=['subject','session','paramsFile'])
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
toFile('lastReadingInfo.pickle', expInfo)#save params to file for next time

#make a log file to save parameter/event  data
filename = 'Reading-%s-%d-%s'%(expInfo['subject'], expInfo['session'], dateStr) #'Sart-' + expInfo['subject'] + '-' + expInfo['session'] + '-' + dateStr
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
message1 = visual.TextStim(win, pos=[0,+3], wrapWidth=30, color='#000000', alignHoriz='center', name='topMsg', text="aaa")
message2 = visual.TextStim(win, pos=[0,-3], wrapWidth=30, color='#000000', alignHoriz='center', name='bottomMsg', text="bbb")
# initialize main text stimulus
textLines = ParseReading.GetTextStims(win) 
# initialize photodiode stimulus
squareSize = 0.4
diodeSquare = visual.Rect(win,pos=[squareSize/4-1,squareSize/4-1],lineColor='white',fillColor='white',size=[squareSize,squareSize],units='norm')

#Read in all pages of text
[pages_all,_,_]=PromptTools.ParseQuestionFile(params['textDir']+params['textFile'])
print('%d pages loaded from %s'%(len(pages_all),params['textFile']))
lines_all = []
for page in pages_all:
    newlines = ParseReading.ParseText(page)
    lines_all += newlines
print('%d lines extracted' %(len(lines_all)))

# read questions and answers from text file
[questions_all,options_all,answers_all] = PromptTools.ParseQuestionFile(params['textDir']+params['questionsFile'])
print('%d questions loaded from %s'%(len(questions_all),params['questionsFile']))
# declare probe parameters
[probe_strings, probe_options,_] = PromptTools.ParseQuestionFile(params['textDir']+params['probesFile'])
print('%d probes loaded from %s'%(len(probe_strings),params['probesFile']))
# Look up prompts
[topPrompts,bottomPrompts] = PromptTools.GetPrompts(os.path.basename(__file__),params['promptType'],params)
print('%d prompts loaded from %s'%(len(topPrompts),'PromptTools.py'))

# Set up serial port
#serialPort = serial.SERIAL("COM1",baudrate=114200,bytesize=8,parity='N',stopbits=1,timeout=0.0001)
#serialPort.writelines("_d1")


# ============================ #
# ======= SUBFUNCTIONS ======= #
# ============================ #

# increment time of next window flip
def AddToFlipTime(tIncrement=1.0):
    tNextFlip[0] += tIncrement
#    print("%1.3f --> %1.3f"%(globalClock.getTime(),tNextFlip[0]))

def SendPortEvent(number):
    print('Page %d'%number)
#    serialPort.writelines(number)

def ShowPage(lines, maxPageTime=float('Inf'), iPage=0):
    # Display text
    win.logOnFlip(level=logging.EXP, msg='Display Page%d'%iPage)
#    win.callOnFlip(SendPortEvent,mod(page,256))
    while (globalClock.getTime()<tNextFlip[0]):
        pass
#        win.flip(clearBuffer=False)
    # draw & flip
    win.clearBuffer()
    for i in range(0,np.minimum(len(textLines),len(lines))):
        textLines[i].setText(lines[i])
        textLines[i].draw()
    if params['usePhotodiode']:
        diodeSquare.draw()
        win.flip()
        # erase diode square and re-draw
        for i in range(0,np.minimum(len(textLines),len(lines))):
            textLines[i].draw()
    win.flip()
    # Flush the key buffer and mouse movements
    event.clearEvents()
    # Wait for relevant key press or 'maxPageTime' seconds
    thisKey = event.waitKeys(maxWait=maxPageTime,keyList=[params['pageKey'],'q','escape'])
    # Process key press
    if thisKey!=None and thisKey[0] in ['q','escape']:
        core.quit()
    elif params['IPI']>0:
        fixation.draw()
        win.logOnFlip(level=logging.EXP, msg='Display Fixation')
        if params['usePhotodiode']:
            diodeSquare.draw()
            win.flip()
            # erase diode square and re-draw
            fixation.draw()
        win.flip()
    # either way, allow the screen to update immediately
    tNextFlip[0]=globalClock.getTime()

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
nBlocks = len(params['pageRanges'])
# Run trials
for iBlock in range(0,nBlocks): # for each block of pages
    
    # log new block
    logging.log(level=logging.EXP, msg='Start Block %d'%iBlock)
    
    for iPage in range(params['pageRanges'][iBlock][0],params['pageRanges'][iBlock][1]):
        # display text
        iStart = (iPage*len(textLines))
        iEnd = np.minimum(((iPage+1)*len(textLines)),len(lines_all))
        ShowPage(lines_all[iStart:iEnd],iPage=iPage)
        if iPage < params['pageRanges'][iBlock][1]-1 and params['IPI']>0:
            # pause
            AddToFlipTime(params['IPI'])
        
    # run probes
    allKeys = PromptTools.RunQuestions(probe_strings,probe_options,win,message1,message2,'Probe',questionDur=params['probeDur'], isEndedByKeypress=params['keyEndsProbe'],respKeys=params['respKeys'])
    # check for escape keypresses
    for thisKey in allKeys:
        if len(thisKey)>0 and thisKey[0] in ['q', 'escape']: # check for quit keys
            core.quit()#abort experiment
    # tell the subject if the lecture is over.
    if iBlock == (nBlocks-1):
        message1.setText("That's the end! Now we'll ask you a few questions about what you read.")
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
    win.callOnFlip(AddToFlipTime,params['IBI'])
    win.flip()
    
# Display the questions and record the answers.
allKeys = PromptTools.RunQuestions(questions_all,options_all,win,message1,message2,'Question',respKeys=params['respKeys'])
# check for escape keypresses
for thisKey in allKeys:
    if len(thisKey)>0 and thisKey[0] in ['q', 'escape']: # check for quit keys
        core.quit()#abort experiment
isCorrect = np.zeros(len(allKeys))
RT = np.zeros(len(allKeys))
#print(allKeys)
for iKey in range(0,len(allKeys)):
    RT[iKey] = allKeys[iKey][1] # keep in seconds
    if float(allKeys[iKey][0]) == answers_all[iKey]:
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
thisKey = event.waitKeys(keyList=['q','escape'])

# exit experiment
core.quit()
