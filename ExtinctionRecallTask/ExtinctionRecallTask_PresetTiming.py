#!/usr/bin/env python2
"""
ExtinctioRecallTask_PresetTiming.py
Display images from a specified folder and present them to the subject, rating the images on given scales.
Also present rest periods, sound checks, and mood ratings to the subject in between runs.

Created 8/21/18 by DJ.
Updated 8/29/18 by DJ - added parallel port triggers, opening prompt, baseline period 
Updated 11/14/18 by DJ - changed port ID for OP4, changed parallel port codes: 0-5 for image in block type 1, 
   6-10 in block type 2, image code + 10 for face rating, 31 and 32 for baseline and mood rating VAS.
Updated 11/28/18 by DJ - Debugged DoRun function, added RunMoodVas function and PreFinalVasMsg parameter.
Updated 12/3/18 by DJ - added moodVasScreenColor, vasMarkerSize, and vasLabelYDist as parameters
Updated 12/19/18 by DJ - split mood VASs into multiple independent files, changed screen colors & spaces, changed fORP keys.
Updated 1/8/19 by DJ - added support for "versions" 5-8, added end block/group/run messages, named VASs more descriptively in log
Updated 1/10/19 by DJ - added year to datestring, incorporated log parsing
Updated 1/11/19 by DJ - fixed "versions" check, RunMoodVas end delays, comments
Updated 1/22/19 by DJ - modified "range" calls to make compatible with python3
Updated 2/21/19 by DJ - changed timing, added MSI, removed dummy run, moved stimuli, 15 groups/run, randomize Q order for each run but not each group
Updated 2/25/19 by DJ - switched to 3 runs, 5 groups/run, changed timing, added visible tick marks to VAS, changed final VAS name to PostRun3.
Updated 3/25/19 by GF - added sound check VAS, second sound check & VAS, second break
Updated 4/12/19 by DJ - no processing at end of task, changed log filename, renamed sound check VASs
Updated 4/25/19 by DJ - added tPreStartup parameter for added fix cross time before Run 1's instructions, added startAtRun option to GUI
Updated 4/26/19 by DJ - renamed tPreStartup->tGetReady and tStartup->tRestInstructions, added corresponding Msg parameters, removed duplicate fixCrossDur
Updated 6/3/19 by GF - added reminder prompt after sound VAS
Updated 6/20-25/19 by DJ - switched to _PresetTiming version that reads in timing files
Updated 6/25/19 by DJ - cleaned up unnecesary code
"""

# Import packages
from psychopy import visual, core, gui, data, event, logging, sound 
from psychopy.tools.filetools import fromFile, toFile # saving and loading parameter files
import time as ts, numpy as np # for timing and array operations
import pandas as pd # for timing file importing/manipulation
import io # for reading files with specified newlines
import os # for file manipulation
import BasicPromptTools # for loading/presenting prompts and questions
import RatingScales # for VAS sliding scale

# ====================== #
# ===== PARAMETERS ===== #
# ====================== #
# Save the parameters declared below?
saveParams = True;
newParamsFilename = 'ER_PresetTiming-params.psydat'

# Declare primary task parameters.
params = {
# Declare timing parameters
    'speedUp': 1., # 1 = normal speed, 10=10x speed
    'tCoolDown': 20,        # duration of fixation cross at end of run
    'tBreak': 60,           # duration of break between runs
# Declare timing files
    'timingFileDir': 'TimingFiles/',                             # where the AFNI timing text files sit
    'usedTimingFileList': 'TimingFiles/ER3.usedIterList.txt',     # subject number and timing file
    'unusedTimingFileList': 'TimingFiles/ER3.unusedIterList.txt', # timing files
# Declare stimulus and response parameters
    'preppedKey': 'y',      # key from experimenter that says scanner is ready
    'triggerKey': '5',      # key from scanner that says scan is starting
    'imageDir': 'Faces/',   # directory containing image stimluli
    'imageNames': ['R0_B100.jpg','R25_B75.jpg','R50_B50.jpg','R75_B25.jpg','R100_B0.jpg'],   # images will be selected randomly (without replacement) from this list of files in imageDir.
                  # Corresponding Port codes will be 1-len(imageNames) for even versions, len(imageNames)-1 for odd versions (to match increasing CSplus level). 
# declare prompts
    'skipPrompts': False,   # go right to the scanner-wait page
    'promptFile': 'Prompts/ExtinctionRecallPrompts.txt', # Name of text file containing prompts 
    'GetReadyMsg': 'Get Ready...',                                         # Text displayed at start of each run
    'RestInstructionsMsg': 'For the next minute or so, stare at the cross and rest.', # Text displayed before fixation cross at start of each run
    'PreSoundCheckFile': "Prompts/ExtinctionRecallSoundCheckPrompts.txt",    # Text FILE containing prompts shown before the sound check
    'PreVasMsg': "Let's do some rating scales.",                             # Text shown BEFORE each VAS except the final one
    'BreakMsg': "You can rest now.",                                         # Text shown during break between runs
    'BetweenRunsReminderMsg': "Please remember, in this next part, the faces might scream, so be prepared for that.", # text file shown after rest before following run 
    'PreFinalVasMsg': "Before we continue, let's do some more rating scales", # Text shown before final VAS
# declare VAS info
    'faceQuestionFile': 'Questions/ERFaceRatingScales.txt', # Name of text file containing image Q&As
    'moodQuestionFile1': 'Questions/ERVas1RatingScales.txt', # Name of text file containing mood Q&As presented before sound check
    'moodQuestionFile2': 'Questions/ERVasRatingScales.txt', # Name of text file containing mood Q&As presented after 1st run
    'moodQuestionFile3': 'Questions/ERVasRatingScales.txt', # Name of text file containing mood Q&As presented after 2nd run
    'moodQuestionFile4': 'Questions/ERVas4RatingScales.txt', # Name of text file containing mood Q&As presented after 3rd run
    'PostSoundCheckFile': 'Questions/PostSoundCheckFile.txt', # Name of text file containing rating scale of volume post sound
    'questionDownKey': '4', # red on fORP
    'questionUpKey':'2',    # yellow on fORP
    'questionSelectKey':'3', # green on fORP
    'questionSelectAdvances': False, # will locking in an answer advance past an image rating?
# sound info
    'badSoundFile': "media/tone_noise_rany.wav",
# parallel port parameters
    'sendPortEvents': True, # send event markers to biopac computer via parallel port
    'portAddress': 0xE050,  # 0xE050,  0x0378,  address of parallel port
    'codeBaseline': 31,     # parallel port code for baseline period (make sure it's greater than nBlocks*2*len(imageNames)!)
    'codeVas': 32,          # parallel port code for mood ratings (make sure it's greater than nBlocks*2*len(imageNames)!)
# declare display parameters
    'fullScreen': True,     # run in full screen mode?
    'screenToShow': 0,      # display on primary screen (0) or secondary (1)?
    'fixCrossSize': 50,     # size of cross, in pixels
    'fixCrossPos': [0,0],   # (x,y) pos of fixation cross displayed before each stimulus (for gaze drift correction)
    'faceHeight': 2.,       # in norm units: 2 = height of screen
    'screenColor':(120,120,120),    # in rgb255 space: (r,g,b) all between 0 and 255
    'textColor': (-1,-1,-1),  # color of text outside of VAS
    'moodVasScreenColor': (110,110,200),  # background behind mood VAS and its pre-VAS prompt. Ideally luminance-matched to screen color via luminance meter/app, else keep in mind gamma correction Y = 0.2126 * R + 0.7152 * G + 0.0722 * B
    'vasTextColor': (-1,-1,-1), # color of text in both VAS types (-1,-1,-1) = black
    'vasMarkerSize': 0.1,   # in norm units (2 = whole screen)
    'vasLabelYDist': 0.1,   # distance below line that VAS label/option text should be, in norm units
    'screenRes': (1024,768) # screen resolution (hard-coded because AppKit isn't available on PCs)
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
    expInfo['version'] = ['1','2','3','4','5','6','7','8']
    expInfo['startAtRun'] = ['1','2','3']
    expInfo['paramsFile'] = [expInfo['paramsFile'],'Load...']
except: # if not there then use a default set
    expInfo = {
        'subject':'1', 
        'session': 1, 
        'version': ['1','2','3','4','5','6','7','8'], # group determining which stim is CS+
        'skipPrompts':False, 
        'sendPortEvents': True,
        'startAtRun': ['1','2','3'],
        'paramsFile':['DEFAULT','Load...']}
# overwrite params struct if you just saved a new parameter set
if saveParams:
    expInfo['paramsFile'] = [newParamsFilename,'Load...']

#present a dialogue to change select params
dlg = gui.DlgFromDict(expInfo, title=scriptName, order=['subject','session','version','skipPrompts','sendPortEvents','paramsFile'])
if not dlg.OK:
    core.quit() # the user hit cancel, so exit

expInfo['paramsFile'] = ''.join(expInfo['paramsFile']) # convert from list of characters to string
# find parameter file
if expInfo['paramsFile'] == 'Load...':
    dlgResult = gui.fileOpenDlg(prompt='Select parameters file',tryFilePath=os.getcwd(),
        allowed="PSYDAT files (*.psydat);;All files (*.*)")
    expInfo['paramsFile'] = dlgResult[0]
# load parameter file
if expInfo['paramsFile'] not in ['DEFAULT', None]: # otherwise, just use defaults.
    # load params file
    print(expInfo)
    params = fromFile(expInfo['paramsFile'])


# transfer experimental flow items from expInfo (gui input) to params (logged parameters)
for flowItem in ['skipPrompts','sendPortEvents']:
    params[flowItem] = expInfo[flowItem]


# print params to Output
print('params = {')
for key in sorted(params.keys()):
    print("   '%s': %s"%(key,params[key])) # print each value as-is (no quotes)
print('}')
    
# save experimental info
toFile('%s-lastExpInfo.psydat'%scriptName, expInfo) #save params to file for next time

#make a log file to save parameter/event  data
dateStr = ts.strftime("%m-%d-%Y", ts.localtime()) # add the current time
logFilename = 'Logs/ER3_%s-%d_%s.log'%(expInfo['subject'], expInfo['session'], dateStr) # log filename
logging.LogFile((logFilename), level=logging.INFO)#, mode='w') # w=overwrite
logging.log(level=logging.INFO, msg='---START PARAMETERS---')
logging.log(level=logging.INFO, msg='filename: %s'%logFilename)
logging.log(level=logging.INFO, msg='subject: %s'%expInfo['subject'])
logging.log(level=logging.INFO, msg='session: %s'%expInfo['session'])
logging.log(level=logging.INFO, msg='version: %s'%expInfo['version'])
logging.log(level=logging.INFO, msg='startAtRun: %s'%expInfo['startAtRun'])
logging.log(level=logging.INFO, msg='date: %s'%dateStr)
# log everything in the params struct
for key in sorted(params.keys()): # in alphabetical order
    logging.log(level=logging.INFO, msg='%s: %s'%(key,params[key])) # log each parameter

logging.log(level=logging.INFO, msg='---END PARAMETERS---')


# ========================== #
# == SET UP PARALLEL PORT == #
# ========================== #

if params['sendPortEvents']:
    from psychopy import parallel
    port = parallel.ParallelPort(address=params['portAddress'])
    port.setData(0) # initialize to all zeros
else:
    print("Parallel port not used.")
    

# ========================== #
# ===== SET UP STIMULI ===== #
# ========================== #

# Initialize deadline for displaying next frame
tNextFlip = [0.0] # put in a list to make it mutable (weird quirk of python variables) 

#create clocks and window
globalClock = core.Clock() #to keep track of time
trialClock = core.Clock() #to keep track of time
win = visual.Window(params['screenRes'], fullscr=params['fullScreen'], allowGUI=False, monitor='testMonitor', screen=params['screenToShow'], units='deg', name='win',color=params['screenColor'],colorSpace='rgb255')
# create fixation cross
fCS = params['fixCrossSize'] # size (for brevity)
fCP = params['fixCrossPos'] # position (for brevity)
lineWidth = int(params['fixCrossSize']/3)
fixation = visual.ShapeStim(win,lineColor=params['textColor'],lineWidth=lineWidth,vertices=((fCP[0]-fCS/2,fCP[1]),(fCP[0]+fCS/2,fCP[1]),(fCP[0],fCP[1]),(fCP[0],fCP[1]+fCS/2),(fCP[0],fCP[1]-fCS/2)),units='pix',closeShape=False,name='fixCross');

# create text stimuli
message1 = visual.TextStim(win, pos=[0,+.4], wrapWidth=1.5, color=params['textColor'], alignHoriz='center', name='topMsg', text="aaa",units='norm')
message2 = visual.TextStim(win, pos=[0,-.4], wrapWidth=1.5, color=params['textColor'], alignHoriz='center', name='bottomMsg', text="bbb",units='norm')

# get stimulus files
allImages = [params['imageDir'] + name for name in params['imageNames']] # assemble filenames: <imageDir>/<imageNames>.
# create corresponding names & codes
if int(expInfo['version']) in [2,4,6,8]: # if it's one of these versions, first in list params['imageNames'] list is CS+0.
    allCodes = list(range(1,len(allImages)+1))
    allNames = ['CSplus0','CSplus25','CSplus50','CSplus75','CSplus100']
else: # if it's version 1, 3, 5, or 7, reverse order
    allCodes = list(range(len(allImages),0,-1))
    allNames = ['CSplus100','CSplus75','CSplus50','CSplus25','CSplus0']
    
print('%d images loaded from %s'%(len(allImages),params['imageDir']))

# initialize main image stimulus
imageName = allImages[0] # initialize with first image
stimImage = visual.ImageStim(win, pos=[0.,0.], name='ImageStimulus',image=imageName, units='norm')
aspectRatio = float(stimImage.size[0])/stimImage.size[1];
stimImage.size = (aspectRatio*params['faceHeight'], params['faceHeight']); # to maintain aspect ratio

# load sound file
badSound = sound.Sound(params['badSoundFile'])

# read prompts, questions and answers from text files
[topPrompts,bottomPrompts] = BasicPromptTools.ParsePromptFile(params['promptFile'])
print('%d prompts loaded from %s'%(len(topPrompts),params['promptFile']))

[topPrompts_sound,bottomPrompts_sound] = BasicPromptTools.ParsePromptFile(params['PreSoundCheckFile'])
print('%d prompts loaded from %s'%(len(topPrompts),params['PreSoundCheckFile']))

[questions,options,answers] = BasicPromptTools.ParseQuestionFile(params['faceQuestionFile'])
print('%d questions loaded from %s'%(len(questions),params['faceQuestionFile']))

[questions_vas1,options_vas1,answers_vas1] = BasicPromptTools.ParseQuestionFile(params['moodQuestionFile1'])
print('%d questions loaded from %s'%(len(questions_vas1),params['moodQuestionFile1']))

[questions_vas2,options_vas2,answers_vas2] = BasicPromptTools.ParseQuestionFile(params['moodQuestionFile2'])
print('%d questions loaded from %s'%(len(questions_vas2),params['moodQuestionFile2']))

[questions_vas3,options_vas3,answers_vas3] = BasicPromptTools.ParseQuestionFile(params['moodQuestionFile3'])
print('%d questions loaded from %s'%(len(questions_vas3),params['moodQuestionFile3']))

[questions_vas4,options_vas4,answers_vas4] = BasicPromptTools.ParseQuestionFile(params['moodQuestionFile4'])
print('%d questions loaded from %s'%(len(questions_vas4),params['moodQuestionFile4']))

[questions_postsoundcheck,options_postsoundcheck,answers_postsoundcheck] = BasicPromptTools.ParseQuestionFile(params['PostSoundCheckFile'])
print('%d questions loaded from %s'%(len(questions_postsoundcheck),params['PostSoundCheckFile']))

# ========================== #
# ===== SET UP TIMING ===== #
# ========================== #
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
dfTiming = [pd.DataFrame()]*3; #initialize list
for i in range(3):
    dfTiming[i] = pd.read_csv('%s/ER3.iter%s.run%d.events.txt'%(params['timingFileDir'],timingFile,i+1))
    # fill in prompts
    dfTiming[i].loc[0,'event_type'] = 'GetReadyMsg';
    dfTiming[i].loc[1,'event_type'] = 'RestInstructionsMsg';
    iPrompts = np.where(dfTiming[i]['event_type']=='prompt')[0];
    for j in iPrompts:
        iNextQ = j+2
        iQ = int(dfTiming[i].loc[iNextQ,'event_type'][1])
        dfTiming[i].loc[j,'event_type'] = 'prompt_q%d'%iQ;
     # fill in fixations
    for j in range(dfTiming[i].shape[0]-1):
        tOffset = (dfTiming[i].loc[j,'onset'] + dfTiming[i].loc[j,'duration'])
        if tOffset < dfTiming[i].loc[j+1,'onset']:
            dfTiming[i] = dfTiming[i].append(pd.DataFrame([['fixation',tOffset,dfTiming[i].loc[j+1,'onset']-tOffset]],columns = dfTiming[i].columns));
    # re-sort
    dfTiming[i] = dfTiming[i].sort_values('onset').reset_index(drop=True)
    # re-label baseline
    dfTiming[i].loc[2,'event_type'] = 'Baseline';
    # add cool-down
    tEnd = dfTiming[i].onset.values[-1] + dfTiming[i].duration.values[-1] # time when task ends
    dfTiming[i] = dfTiming[i].append(pd.DataFrame([['coolDown',tEnd,params['tCoolDown']]],columns = dfTiming[i].columns));
    # re-sort
    dfTiming[i] = dfTiming[i].sort_values('onset').reset_index(drop=True)
    
# print('%d conditions found in timing file. Parameters specified %d trials per run.'%(len(conditions),params['nTrialsPerRun']))



# ============================ #
# ======= SUBFUNCTIONS ======= #
# ============================ #

# increment time of next window flip
def AddToFlipTime(tIncrement=1.0):
    tNextFlip[0] += tIncrement/params['speedUp']

# flip window as soon as possible
def SetFlipTimeToNow():
    tNextFlip[0] = globalClock.getTime()

def WaitForFlipTime():
    while (globalClock.getTime()<tNextFlip[0]):
        keyList = event.getKeys()
        # Check for escape characters
        for key in keyList:
            if key in ['q','escape']:
                CoolDown()

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
    keyList = event.waitKeys(keyList=[params['preppedKey'],'q','escape'])
    # Check for escape characters
    for key in keyList:
        if key in ['q','escape']:
            CoolDown()
    
    # wait for scanner
    message1.setText("Waiting for scanner to start...")
    message2.setText("(Press '%c' to override.)"%params['triggerKey'].upper())
    message1.draw()
    message2.draw()
    win.logOnFlip(level=logging.EXP, msg='Display WaitingForScanner')
    win.flip()
    keyList = event.waitKeys(keyList=[params['triggerKey'],'q','escape'])
    SetFlipTimeToNow()
    # Check for escape characters
    for key in keyList:
        if key in ['q','escape']:
            CoolDown()

# Display the prompt before a block
def ShowPreBlockPrompt(question,iPrompt):
    # update messages and draw them
    message1.setText("In this block, when you see a face, answer:")
    message2.setText(question)
    message1.draw()
    message2.draw()
    # set up logging
    win.logOnFlip(level=logging.EXP, msg='Display PreBlockPrompt%d'%iPrompt)

# Display an image
def ShowImage(imageFile, imageName='image'):
    # display info to experimenter
    print('Showing Stimulus %s'%imageName) 
    # Draw image
    stimImage.setImage(imageFile)
    stimImage.draw()
    # log image
    win.logOnFlip(level=logging.EXP, msg='Display %s %s'%(imageFile,imageName))
    

# Run a set of visual analog scale (VAS) questions
def RunVas(questions,options,pos=(0.,-0.25),scaleTextPos=[0.,0.25],questionDur=float('inf'),isEndedByKeypress=params['questionSelectAdvances'],name='Vas'):
    
    # wait until it's time
    WaitForFlipTime()
    
    # Show questions and options
    [rating,decisionTime,choiceHistory] = RatingScales.ShowVAS(questions,options, win, questionDur=questionDur/params['speedUp'], \
        upKey=params['questionUpKey'], downKey=params['questionDownKey'], selectKey=params['questionSelectKey'],\
        isEndedByKeypress=isEndedByKeypress, textColor=params['vasTextColor'], name=name, pos=pos,\
        scaleTextPos=scaleTextPos, labelYPos=pos[1]-params['vasLabelYDist'], markerSize=params['vasMarkerSize'],\
        tickHeight=1,tickLabelWidth = 0.9)
    
    # Update next stim time
    if isEndedByKeypress:
        SetFlipTimeToNow() # no duration specified, so timing creep isn't an issue
    else:
        AddToFlipTime(questionDur*len(questions)) # add question duration * # of questions


def RunMoodVas(questions,options,name='MoodVas'):
    
    # Wait until it's time
    WaitForFlipTime()
    # Set screen color
    win.color = params['moodVasScreenColor']
    win.flip() # must flip twice for color change to take
    
    # display pre-VAS prompt
    if not params['skipPrompts']:
        BasicPromptTools.RunPrompts([params['PreVasMsg']],["Press any button to continue."],win,message1,message2)
    
    # Display this VAS
    win.callOnFlip(SetPortData,data=params['codeVas'])
    RunVas(questions,options,questionDur=float("inf"), isEndedByKeypress=True,name=name)
    
    # Set screen color back
    win.color = params['screenColor']
    win.flip() # flip so the color change 'takes' right away

def RunSoundVas(questions_postsoundcheck,options_postsoundcheck,name='SoundVas'):
    
    # Wait until it's time
    WaitForFlipTime()
    
    # Display this VAS
    win.callOnFlip(SetPortData,data=params['codeVas'])
    RunVas(questions_postsoundcheck,options_postsoundcheck,questionDur=float("inf"), isEndedByKeypress=True,name=name)


def DoRun(allImages,allCodes,allNames,dfRunTiming):
    # wait for scanner
    WaitForScanner() # includes SetFlipTimeToNow
    # Log state of experiment
    logging.log(level=logging.EXP,msg='===== START RUN =====')
    iBlock = 0; # reset block number
    
    for iStim in range(dfRunTiming.shape[0]):
        # extract info from timing dataframe
        eventType = dfRunTiming.loc[iStim,'event_type'];
        eventDur = dfRunTiming.loc[iStim,'duration'];
        
        if eventType=='GetReadyMsg':
            # Display get ready message
            message1.text = params['GetReadyMsg']
            message1.draw()
            win.logOnFlip(level=logging.EXP, msg='Display GetReady')
        elif eventType=='RestInstructionsMsg':
            # Display instructions before rest
            message1.text = params['RestInstructionsMsg']
            message1.draw()
            win.logOnFlip(level=logging.EXP, msg='Display RestInstructions')
        elif eventType=='Baseline':
            # display fixation before first stimulus
            fixation.draw()
            win.callOnFlip(SetPortData,data=params['codeBaseline'])
            win.logOnFlip(level=logging.EXP, msg='Display Fixation')
        elif eventType=='fixation':
            # display fixation and reset port
            fixation.draw()
            win.callOnFlip(SetPortData,data=0)
            win.logOnFlip(level=logging.EXP, msg='Display Fixation')
        elif eventType.startswith('prompt'):
            # Log state of experiment
            if iBlock>0:
                logging.log(level=logging.EXP,msg='=== END BLOCK %d, TYPE %d ==='%(iBlock,iBlockType))
            # update block index
            iBlock = iBlock + 1;
            iBlockType = int(eventType[-1]);
            # Log state of experiment
            logging.log(level=logging.EXP,msg='=== START BLOCK %d, TYPE %d ==='%(iBlock,iBlockType))
            # Display pre-block prompt
            ShowPreBlockPrompt(questions[iBlockType].upper(), iBlockType)
        elif eventType.startswith('face'):
            # extract image index
            CS = int(eventType[-3:])
            iImage = allNames.index('CSplus%d'%CS)
            # display image
            portCode = len(allCodes)*(iBlockType) + allCodes[iImage]
            win.callOnFlip(SetPortData,data=portCode)
            ShowImage(imageFile=allImages[iImage],imageName=allNames[iImage])
        elif eventType.startswith('q'):
            # Display VAS
            portCode = len(allCodes)*(iBlockType+2) + allCodes[iImage]
            win.callOnFlip(SetPortData,data=portCode)
            RunVas([questions[iBlockType]],[options[iBlockType]],name='ImageRating',questionDur=eventDur)
            # skip wait/display (it's included in the RunVas function)
            continue
        elif eventType=='coolDown':
            # Log state of experiment
            logging.log(level=logging.EXP,msg='=== END BLOCK %d TYPE %d ==='%(iBlock,iBlockType))
            # display fixation and reset port
            fixation.draw()
            win.callOnFlip(SetPortData,data=0)
            win.logOnFlip(level=logging.EXP, msg='Display Fixation')
        # wait until it's time to show screen
        WaitForFlipTime()
        # show screen and update next flip time 
        win.flip()
        AddToFlipTime(eventDur)
        
    
    WaitForFlipTime()
    # Log state of experiment
    logging.log(level=logging.EXP,msg='===== END RUN =====')


# Handle end of a session
def CoolDown():
    
    # turn off auto-draw of image
    stimImage.autoDraw = False
    win.flip()
    
    # display cool-down message
    message1.setText("That's the end! We will take you out of the scanner now. ")
    message2.setText("Press 'q' or 'escape' to end the session.")
    win.logOnFlip(level=logging.EXP, msg='Display TheEnd')
    message1.draw()
    message2.draw()
    win.flip()
    thisKey = event.waitKeys(keyList=['q','escape'])
    
    # exit
    core.quit()


# === SET UP GLOBAL ESCAPE KEY === #
event.globalKeys.clear()
event.globalKeys.add(key='q', modifiers=['ctrl'], func=CoolDown)


# === MAIN EXPERIMENT === #

# log experiment start and set up
logging.log(level=logging.EXP, msg='---START EXPERIMENT---')

if int(expInfo['startAtRun'])==1:
    # ---VAS
    RunMoodVas(questions_vas1,options_vas1,name='PreSoundCheck-')

    # ---Instructions
    # display prompts
    if not params['skipPrompts']:
        BasicPromptTools.RunPrompts(topPrompts,bottomPrompts,win,message1,message2)

    # ---Sound Check
    # show instructions
    if not params['skipPrompts']:
        BasicPromptTools.RunPrompts(topPrompts_sound,bottomPrompts_sound,win,message1,message2)

    # show blank screen
    win.logOnFlip(level=logging.EXP, msg='Display Blank')
    win.flip()
    # wait briefly
    core.wait(0.5)

    # play sound
    badSound.play()
    # wait briefly
    core.wait(1.5)

    # ---VAS
    RunSoundVas(questions_postsoundcheck,options_postsoundcheck,name='SoundCheck1-')
    
    #---reminder prompt
    if not params['skipPrompts']:
        BasicPromptTools.RunPrompts([params['BetweenRunsReminderMsg']],["Press any button to continue."],win,message1,message2)

    # ---Run 1
    DoRun(allImages,allCodes,allNames,dfTiming[0])

    # ---VAS
    RunMoodVas(questions_vas2,options_vas2,name='PostRun1-')

    # ---break (60s)
    # display break prompt
    message1.text = params['BreakMsg']
    # Set up display
    win.logOnFlip(level=logging.EXP, msg='Display BreakMsg')
    message1.draw()
    # Wait until it's time to display
    WaitForFlipTime()
    # Display prompt
    win.flip()
    AddToFlipTime(params['tBreak'])
    WaitForFlipTime()


if int(expInfo['startAtRun'])<=2:
    # ---Sound Check
    # show instructions
    if not params['skipPrompts']:
        BasicPromptTools.RunPrompts(topPrompts_sound,bottomPrompts_sound,win,message1,message2)

    # show blank screen
    win.logOnFlip(level=logging.EXP, msg='Display Blank')
    win.flip()
    # wait briefly
    core.wait(0.5)

    # play sound
    badSound.play()
    # wait briefly
    core.wait(1.5)

    # ---VAS
    RunSoundVas(questions_postsoundcheck,options_postsoundcheck,name='SoundCheck2-')

    #---reminder prompt 
    if not params['skipPrompts']:
        BasicPromptTools.RunPrompts([params['BetweenRunsReminderMsg']],["Press any button to continue."],win,message1,message2)

    # ---Run 2
    DoRun(allImages,allCodes,allNames,dfTiming[1])

    # ---VAS
    RunMoodVas(questions_vas3,options_vas3,name='PostRun2-')

    # ---break (60s)
    # display break prompt
    message1.text = params['BreakMsg']
    # Set up display
    win.logOnFlip(level=logging.EXP, msg='Display BreakMsg')
    message1.draw()
    # Wait until it's time to display
    WaitForFlipTime()
    # Display prompt
    win.flip()
    AddToFlipTime(params['tBreak'])
    WaitForFlipTime()


# ---Sound Check
# show instructions
if not params['skipPrompts']:
    BasicPromptTools.RunPrompts(topPrompts_sound,bottomPrompts_sound,win,message1,message2)

# show blank screen
win.logOnFlip(level=logging.EXP, msg='Display Blank')
win.flip()
# wait briefly
core.wait(0.5)

# play sound
badSound.play()
# wait briefly
core.wait(1.5)

# ---VAS
RunSoundVas(questions_postsoundcheck,options_postsoundcheck,name='SoundCheck3-')

#---reminder prompt 
if not params['skipPrompts']:
    BasicPromptTools.RunPrompts([params['BetweenRunsReminderMsg']],["Press any button to continue."],win,message1,message2)

# ---Run 3
DoRun(allImages,allCodes,allNames,dfTiming[2])

# ---DonePrompt
WaitForFlipTime()
# display done prompt
if not params['skipPrompts']:
    BasicPromptTools.RunPrompts([params['PreFinalVasMsg']],["Press any button to continue."],win,message1,message2)

# ---VAS
RunMoodVas(questions_vas4,options_vas4,name='PostRun3-')

# Log end of experiment
logging.log(level=logging.EXP, msg='--- END EXPERIMENT ---')

# exit experiment
CoolDown()
