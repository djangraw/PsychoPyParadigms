#!/usr/bin/env python2
"""Display images from a specified folder and present them to the subject."""
# ExtinctioRecallAndVasTask.py
# Created 8/21/18 by DJ.
# Updated 8/29/18 by DJ - added parallel port triggers, opening prompt, baseline period 
# Updated 11/14/18 by DJ - changed port ID for OP4, changed parallel port codes: 0-5 for image in block type 1, 
#    6-10 in block type 2, image code + 10 for face rating, 31 and 32 for baseline and mood rating VAS.
# Updated 11/28/18 by DJ - Debugged DoRun function, added RunMoodVas function and PreFinalVasMsg parameter.
# Updated 12/3/18 by DJ - added moodVasScreenColor, vasMarkerSize, and vasLabelYDist as parameters
# Updated 12/19/18 by DJ - split mood VASs into multiple independent files, changed screen colors & spaces, changed fORP keys.

# Import packages
from psychopy import visual, core, gui, data, event, logging, parallel, sound 
from psychopy.tools.filetools import fromFile, toFile # saving and loading parameter files
import time as ts, numpy as np # for timing and array operations
import os, glob # for file manipulation
import BasicPromptTools # for loading/presenting prompts and questions
import random # for randomization of trials
import RatingScales # for VAS sliding scale

# ====================== #
# ===== PARAMETERS ===== #
# ====================== #
# Save the parameters declared below?
saveParams = True;
newParamsFilename = 'ExtinctionRecallParams.psydat'

# Declare primary task parameters.
params = {
# Declare experiment flow parameters
    'nTrialsPerBlock': 5,            # number of trials in a block
    'nBlocksPerGroup': 2,
    'nGroupsPerRun': 2,# 4,
# Declare timing parameters
    'tStartup': 3.,         # 16., #time displaying instructions while waiting for scanner to reach steady-state
    'tBaseline': 4.,        # 60., # pause time before starting first stimulus
    'tPreBlockPrompt': 5.,  # duration of prompt before each block
    'tStim': 4.,            # time when stimulus is presented (in seconds)
    'questionDur': 4.,      # duration of the image rating (in seconds)
    'tIsiMin': 4.,          # min time between when one stimulus disappears and the next appears (in seconds)
    'tIsiMax': 6.,          # max time between when one stimulus disappears and the next appears (in seconds)
    'tBreak': 60,           # duration of break between runs
    'tDummyRun': 30,        # duration of dummy run at end
    'fixCrossDur': 20.,     # duration of cross fixation before each run
# Declare stimulus and response parameters
    'preppedKey': 'y',         # key from experimenter that says scanner is ready
    'triggerKey': '5',        # key from scanner that says scan is starting
    'imageDir': 'Faces/',    # directory containing image stimluli
    'imageNames': ['R0_B100.jpg','R25_B75.jpg','R50_B50.jpg','R75_B25.jpg','R100_B0.jpg'],   # images will be selected randomly (without replacement) from this list of files in imageDir.
                  # Corresponding Port codes will be 1-len(imageNames) for versions 2 & 4, len(imageNames)-1 for versions 1 & 3 (to match increasig CSplus level). 
# declare prompt files
    'skipPrompts': False,     # go right to the scanner-wait page
    'promptFile': 'Prompts/ExtinctionRecallPrompts.txt', # Name of text file containing prompts 
    'PreSoundCheckFile': "Prompts/ExtinctionRecallSoundCheckPrompts.txt", # text file containing prompts shown before the sound check
    'PreVasMsg': "Let's do some rating scales.", # text (not file) shown BEFORE each VAS except the final one
    'BreakMsg': "You can rest now.", # text shown during break between runs
    'PreFinalVasMsg': "We're done!", # text shown before final VAS
# declare VAS info
    'faceQuestionFile': 'Questions/ERFaceRatingScales.txt', # Name of text file containing image Q&As
    'moodQuestionFile1': 'Questions/ERVas1RatingScales.txt', # Name of text file containing mood Q&As presented before sound check
    'moodQuestionFile2': 'Questions/ERVasRatingScales.txt', # Name of text file containing mood Q&As presented after 1st run
    'moodQuestionFile3': 'Questions/ERVasRatingScales.txt', # Name of text file containing mood Q&As presented after 2nd run
    'moodQuestionFile4': 'Questions/ERVas4RatingScales.txt', # Name of text file containing mood Q&As presented after final dummy run
    'questionDownKey': '4', # red on fORP
    'questionUpKey':'2', # yellow on fORP
    'questionSelectKey':'3', # green on fORP
    'questionSelectAdvances': False,
# sound info
    'badSoundFile': "media/tone_noise_rany.wav",
# parallel port parameters
    'sendPortEvents': True, # send event markers to biopac computer via parallel port
    'portAddress': 0xE050, # 0x0378, # address of parallel port
    'codeBaseline': 31, # parallel port code for baseline period (make sure it's greater than nBlocks*2*len(imageNames)!)
    'codeVas': 32, # parallel port code for mood ratings (make sure it's greater than nBlocks*2*len(imageNames)!)
# declare display parameters
    'fullScreen': True,       # run in full screen mode?
    'screenToShow': 0,        # display on primary screen (0) or secondary (1)?
    'fixCrossSize': 50,       # size of cross, in pixels
    'fixCrossPos': [0,0],     # (x,y) pos of fixation cross displayed before each stimulus (for gaze drift correction)
    'screenColor':(120,120,120),    # (120,120,120) in rgb space: (r,g,b) all between 0 and 255
    'textColor': (-1,-1,-1),  # color of text outside of VAS
    'moodVasScreenColor': (110,110,200),  # background behind mood VAS and its pre-VAS prompt. Ideally luminance-matched to screen color via luminance meter/app, else keep in mind gamma correction Y = 0.2126 * R + 0.7152 * G + 0.0722 * B
    'vasTextColor': (-1,-1,-1), # color of text in both VAS types (-1,-1,-1) = black
    'vasMarkerSize': 0.1,     # in norm units (2 = whole screen)
    'vasLabelYDist': 0.1,     # distance below line that VAS label/option text should be, in norm units
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
    expInfo['version'] = ['1','2','3','4']
    expInfo['paramsFile'] = [expInfo['paramsFile'],'Load...']
except: # if not there then use a default set
    expInfo = {
        'subject':'1', 
        'session': 1, 
        'version': ['1','2','3','4'], # group determining which stim is CS+
        'skipPrompts':False, 
        'sendPortEvents': True,
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
print 'params = {'
for key in sorted(params.keys()):
    print "   '%s': %s"%(key,params[key]) # print each value as-is (no quotes)
print '}'
    
# save experimental info
toFile('%s-lastExpInfo.psydat'%scriptName, expInfo)#save params to file for next time

#make a log file to save parameter/event  data
dateStr = ts.strftime("%b_%d_%H%M", ts.localtime()) # add the current time
filename = 'Logs/%s-%s-%d-%s'%(scriptName,expInfo['subject'], expInfo['session'], dateStr) # log filename
logging.LogFile((filename+'.log'), level=logging.INFO)#, mode='w') # w=overwrite
logging.log(level=logging.INFO, msg='---START PARAMETERS---')
logging.log(level=logging.INFO, msg='filename: %s'%filename)
logging.log(level=logging.INFO, msg='subject: %s'%expInfo['subject'])
logging.log(level=logging.INFO, msg='session: %s'%expInfo['session'])
logging.log(level=logging.INFO, msg='version: %s'%expInfo['version'])
logging.log(level=logging.INFO, msg='date: %s'%dateStr)
# log everything in the params struct
for key in sorted(params.keys()): # in alphabetical order
    logging.log(level=logging.INFO, msg='%s: %s'%(key,params[key])) # log each parameter

logging.log(level=logging.INFO, msg='---END PARAMETERS---')


# ========================== #
# ===== GET SCREEN RES ===== #
# ========================== #

# kluge for secondary monitor
#if params['fullScreen']: 
#    screens = AppKit.NSScreen.screens()
#    screenRes = (int(screens[params['screenToShow']].frame().size.width), int(screens[params['screenToShow']].frame().size.height))
##    screenRes = [1920, 1200]
#    if params['screenToShow']>0:
#        params['fullScreen'] = False
#else:
#    screenRes = [800,600]
screenRes = params['screenRes'] # hard-coded because AppKit isn't available on PCs

print "screenRes = [%d,%d]"%screenRes


# ========================== #
# == SET UP PARALLEL PORT == #
# ========================== #

if params['sendPortEvents']:
    port = parallel.ParallelPort(address=params['portAddress'])
    port.setData(0) # initialize to all zeros
else:
    print "Parallel port not used."
    

# ========================== #
# ===== SET UP STIMULI ===== #
# ========================== #

# Initialize deadline for displaying next frame
tNextFlip = [0.0] # put in a list to make it mutable (weird quirk of python variables) 

#create clocks and window
globalClock = core.Clock()#to keep track of time
trialClock = core.Clock()#to keep track of time
win = visual.Window(screenRes, fullscr=params['fullScreen'], allowGUI=False, monitor='testMonitor', screen=params['screenToShow'], units='deg', name='win',color=params['screenColor'],colorSpace='rgb255')
# create fixation cross
fCS = params['fixCrossSize'] # size (for brevity)
fCP = params['fixCrossPos'] # position (for brevity)
lineWidth = int(params['fixCrossSize']/3)
fixation = visual.ShapeStim(win,lineColor=params['textColor'],lineWidth=lineWidth,vertices=((fCP[0]-fCS/2,fCP[1]),(fCP[0]+fCS/2,fCP[1]),(fCP[0],fCP[1]),(fCP[0],fCP[1]+fCS/2),(fCP[0],fCP[1]-fCS/2)),units='pix',closeShape=False,name='fixCross');
duration = params['fixCrossDur'] # duration (for brevity)

# create text stimuli
message1 = visual.TextStim(win, pos=[0,+.4], wrapWidth=1.5, color=params['textColor'], alignHoriz='center', name='topMsg', text="aaa",units='norm')
message2 = visual.TextStim(win, pos=[0,-.6], wrapWidth=1.5, color=params['textColor'], alignHoriz='center', name='bottomMsg', text="bbb",units='norm')

# get stimulus files
allImages = [params['imageDir'] + name for name in params['imageNames']] # assemble filenames: <imageDir>/<imageNames>.
# create corresponding names & codes
if expInfo['version'] in [2,4]:
    allCodes = range(1,len(allImages)+1)
    allNames = ['CSplus0','CSplus25','CSplus50','CSplus75','CSplus100']
else: # if it's version 1 or 3, reverse order
    allCodes = range(len(allImages),0,-1)
    allNames = ['CSplus100','CSplus75','CSplus50','CSplus25','CSplus0']
    
print('%d images loaded from %s'%(len(allImages),params['imageDir']))
# make sure there are enough images
if len(allImages)<params['nTrialsPerBlock']:
    raise ValueError("# images found in '%s' (%d) is less than # trials (%d)!"%(params['imageDir'],len(allImages),params['nTrials']))

# initialize main image stimulus
imageName = allImages[0] # initialize with first image
stimImage = visual.ImageStim(win, pos=[0.,0.3], name='ImageStimulus',image=imageName, units='norm', size=[0.7,1.0])

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


# declare order of blocks for later randomization
blockOrder = range(params['nBlocksPerGroup'])


# ============================ #
# ======= SUBFUNCTIONS ======= #
# ============================ #

# increment time of next window flip
def AddToFlipTime(tIncrement=1.0):
    tNextFlip[0] += tIncrement

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
    # wait until it's time
    WaitForFlipTime()
    # update display 
    win.flip()
    # Update next stim time
    AddToFlipTime(params['tPreBlockPrompt'])
    

# Display an image
def ShowImage(imageFile, stimDur=float('Inf'),imageName='image'):
    # display info to experimenter
    print('Showing Stimulus %s'%imageName) 
    
    # Draw image
    stimImage.setImage(imageFile)
    stimImage.draw()
    # Wait until it's time to display
    WaitForFlipTime()
    # log & flip window to display image
    win.logOnFlip(level=logging.EXP, msg='Display %s %s'%(imageFile,imageName))
    win.flip()
    # Update next stim time
    AddToFlipTime(stimDur) # add to tNextFlip[0]
    

# Run a set of visual analog scale (VAS) questions
def RunVas(questions,options,pos=(0.,-.5),scaleTextPos=[0.,-0.3],questionDur=params['questionDur'],isEndedByKeypress=params['questionSelectAdvances']):
    
    # wait until it's time
    WaitForFlipTime()
    
    # Show questions and options
    [rating,decisionTime,choiceHistory] = RatingScales.ShowVAS(questions,options, win, questionDur=questionDur, \
        upKey=params['questionUpKey'], downKey=params['questionDownKey'], selectKey=params['questionSelectKey'],\
        isEndedByKeypress=isEndedByKeypress, textColor=params['vasTextColor'], name='Vas', pos=pos,\
        scaleTextPos=scaleTextPos, labelYPos=pos[1]-params['vasLabelYDist'], markerSize=params['vasMarkerSize'])
    
    # Update next stim time
    if params['questionSelectAdvances']:
        SetFlipTimeToNow() # no duration specified, so timing creep isn't an issue
    else:
        AddToFlipTime(params['questionDur']*len(questions)) # add question duration * # of questions



def RunMoodVas(questions,options):
    
    
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
    RunVas(questions,options,pos=(0,0.),scaleTextPos=[0,0.5],questionDur=float("inf"), isEndedByKeypress=True)
    
    # Set screen color back
    win.color = params['screenColor']
    win.flip() # flip so the color change 'takes' right away

def DoRun(allImages,allCodes,allNames):
    # wait for scanner
    WaitForScanner() # includes SetFlipTimeToNow
    # Log state of experiment
    logging.log(level=logging.EXP,msg='===== START RUN =====')
    
    # Display instructions while waiting to reach steady state
    win.logOnFlip(level=logging.EXP, msg='Display RestInstructions')
    message1.text = 'For the next minute or so, stare at the cross and rest.'
    message1.draw()
    win.flip()
    AddToFlipTime(params['tStartup'])
    
    
    # display fixation before first stimulus
    fixation.draw()
    win.callOnFlip(SetPortData,data=params['codeBaseline'])
    win.logOnFlip(level=logging.EXP, msg='Display Fixation')
    # wait until it's time to show screen
    WaitForFlipTime()
    # Update time of next stim
    AddToFlipTime(params['fixCrossDur']) # duration of cross before each run
    # show screen and update next flip time
    win.flip()
    AddToFlipTime(params['tBaseline'])
    
    
    # RUN GROUP OF BLOCKS
    for iGroup in range(params['nGroupsPerRun']):
        # Log state of experiment
        logging.log(level=logging.EXP,msg='==== START GROUP %d/%d ===='%(iGroup+1,params['nGroupsPerRun']))
        # randomize order of blocks
        random.shuffle(blockOrder)
        
        # RUN BLOCK
        for iBlock in range(params['nBlocksPerGroup']):
            
            # Log state of experiment
            logging.log(level=logging.EXP,msg='=== START BLOCK %d/%d ==='%(iBlock+1,params['nBlocksPerGroup']))
            
            # randomize order of images and codes the same way
            ziplist = list(zip(allImages, allCodes, allNames))
            random.shuffle(ziplist)
            allImages, allCodes, allNames = zip(*ziplist)
            
            # Display pre-block prompt
            ShowPreBlockPrompt(questions[blockOrder[iBlock]].upper(), blockOrder[iBlock])
            
            # RUN TRIAL
            for iTrial in range(params['nTrialsPerBlock']):
                # display image
                portCode = len(allCodes)*(blockOrder[iBlock]) + allCodes[iTrial]
                win.callOnFlip(SetPortData,data=portCode)
                ShowImage(imageFile=allImages[iTrial],stimDur=params['tStim'],imageName=allNames[iTrial])
                
                # Add image to VAS
                stimImage.autoDraw = True
                # Display VAS
                portCode = len(allCodes)*(blockOrder[iBlock]+2) + allCodes[iTrial]
                win.callOnFlip(SetPortData,data=portCode)
                RunVas([questions[blockOrder[iBlock]]],[options[blockOrder[iBlock]]])
                # Remove image
                stimImage.autoDraw = False
                
                # get randomized ISI
                tIsi = random.uniform(params['tIsiMin'],params['tIsiMax'])
                # Display Fixation Cross (ISI)
                if iTrial < (params['nTrialsPerBlock']-1):
                    # Display the fixation cross
                    fixation.draw() # draw it
                    win.logOnFlip(level=logging.EXP, msg='Display Fixation')
                    win.callOnFlip(SetPortData,data=0)
                    # VAS keeps control to the end, so no need to wait for flip time
                    win.flip()
                    AddToFlipTime(tIsi)


def DoDummyRun():
    # wait for scanner
    WaitForScanner() # includes SetFlipTimeToNow
    # Log state of experiment
    logging.log(level=logging.EXP,msg='===== START DUMMY RUN =====')
    
    # Display instructions while waiting to reach steady state
    win.logOnFlip(level=logging.EXP, msg='Display RestInstructions')
    message1.text = 'For the next minute or so, stare at the cross and rest.'
    message1.draw()
    win.flip()
    AddToFlipTime(params['tStartup'])
    
    # display fixation before first stimulus
    fixation.draw()
    win.callOnFlip(SetPortData,data=params['codeBaseline'])
    win.logOnFlip(level=logging.EXP, msg='Display Fixation')
    # wait until it's time to show screen
    WaitForFlipTime()
    # Update time of next stim
    AddToFlipTime(params['fixCrossDur']) # duration of cross before each run
    # show screen and update next flip time
    win.flip()
    AddToFlipTime(params['tDummyRun'])
    


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

# ---VAS
RunMoodVas(questions_vas1,options_vas1)

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

# wait for keypress
thisKey = event.waitKeys()
if thisKey[0] in ['q','escape']: # quit if excape keypress
    core.quit()

# ---Run 1
DoRun(allImages,allCodes,allNames)

# ---VAS
RunMoodVas(questions_vas2,options_vas2)

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

# ---Run 2
DoRun(allImages,allCodes,allNames)

# ---VAS
RunMoodVas(questions_vas3,options_vas3)

# ---dummyRun (30s)
DoDummyRun()

# ---DonePrompt
WaitForFlipTime()
# display done prompt
if not params['skipPrompts']:
    BasicPromptTools.RunPrompts([params['PreFinalVasMsg']],["Press any button to continue."],win,message1,message2)

# ---VAS
RunMoodVas(questions_vas4,options_vas4)

# Log end of experiment
logging.log(level=logging.EXP, msg='--- END EXPERIMENT ---')

# exit experiment
CoolDown()
