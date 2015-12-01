#!/usr/bin/env python2
"""Display resting-state instructions, pause, then administer a questionnaire about the subject's experience, 
such as the Amsterdam Resting-State Questionnaire."""
# RestingStateQuestionnaire_d1.py
# Created 9/8/15 by DJ.
# Updated 9/9/15 by DJ - switched from PromptTools to QuestionTools.
# Updated 11/9/15 by DJ - switched from QuestionTools to BasicPromptTools, used ParsePromptFile.

# Import packages
from psychopy import core, gui, data, event, sound, logging #, visual # visual causes a bug in the guis, so I moved it down.
from psychopy.tools.filetools import fromFile, toFile
import time as ts, numpy as np
import AppKit, os # for monitor size detection, files
import random
import BasicPromptTools

# Declare parameter filenames
saveParams = True; # take the parameters below and save them to a .pickle file
newParamsFilename = 'RsqParams_ARSQ_5min_EyesClosed.pickle' # the .pickle file where the params should be saved (the user can edit/confirm in a GUI)
expInfoFilename = 'lastRsqInfo_d1_behavior.pickle' # the .pickle file where the script loads/saves the 'latest' settings (e.g., subject, session, params file)

# Declare primary task parameters.
params = {
# Declare response parameters
    'skipPrompts': False,     # go right to the scanner-wait page
    'triggerKey': 't',        # key from scanner that says scan is starting
    'upKey': 'r',#'up',
    'downKey': 'y',#'down',
    'selectKey': 'b',#'space',
    'tRest': 0, #300, # time (in seconds) of rest period
# declare movie and question files
    'textDir': 'stimuli/',
    'restPromptsFile': 'restPrompts_ARSQ_5min_EyesClosed.txt', 
    'questionnairePromptsFile': 'questionnairePrompts_ARSQ_ButtonBox.txt',
    'questionFile': 'ARSQ_PsychoPy.txt', 
    'randomizeQuestionOrder': False, # randomize order of questions (if true, questionOrder will be overwritten later)
    'questionOrder': range(0,30,3) + range(1,30,3) + range(2,30,3) + range(30,55), # one from each of the main areas, then the second, then the third, then the others, and finally the validation. 
# declare other stimulus parameters
    'fullScreen': True,       # run in full screen mode?
    'screenToShow': 1,        # display on primary screen (0) or secondary (1)?
    'fixCrossSize': 10,       # size of cross, in pixels
    'fixCrossPos': [0,0],     # (x,y) pos of fixation cross displayed during each session
}

# allow user to save the parameters
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
    expInfo = fromFile(expInfoFilename)
    expInfo['session'] +=1 # automatically increment session number
    expInfo['paramsFile'] = [expInfo['paramsFile'],'Load...']
except:#if not there then use a default set
    expInfo = {'subject':'1', 'session':1, 'skipPrompts':False, 'paramsFile':['DEFAULT','Load...']}
# overwrite if you just saved a new parameter set
if saveParams:
    expInfo['paramsFile'] = [newParamsFilename,'Load...']
dateStr = ts.strftime("%b_%d_%H%M", ts.localtime()) # add the current time

#present a dialogue to change params
dlg = gui.DlgFromDict(expInfo, title='Resting state params', order=['subject','session','skipPrompts','paramsFile'])
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

# transfer skipPrompts
params['skipPrompts'] = expInfo['skipPrompts']

# read questions and answers from text files
[questions,options,_] = BasicPromptTools.ParseQuestionFile(params['textDir']+params['questionFile'],optionsType='Likert')
print('%d questions loaded from %s'%(len(questions),params['questionFile']))
[topRestPrompts,bottomRestPrompts] = BasicPromptTools.ParsePromptFile(params['textDir']+params['restPromptsFile'])
print('%d prompts loaded from %s'%(len(topRestPrompts),params['restPromptsFile']))
[topQuestionnairePrompts,bottomQuestionnairePrompts] = BasicPromptTools.ParsePromptFile(params['textDir']+params['questionnairePromptsFile'])
print('%d prompts loaded from %s'%(len(topQuestionnairePrompts),params['questionnairePromptsFile']))

# shuffle the order
if params['randomizeQuestionOrder']:
    newOrder = range(0,len(questions_all))
    random.shuffle(newOrder)
    questions = [questions[i] for i in newOrder]
    options = [options[i] for i in newOrder]
    params['questionOrder'] = newOrder
# reorder the questions and options
questions = [questions[i] for i in params['questionOrder']]
options = [options[i] for i in params['questionOrder']]

# print params to Output
print 'params = {'
for key in sorted(params.keys()):
    print "   '%s': %s"%(key,params[key]) # print each value as-is (no quotes)
print '}'
    

#make a log file to save parameter/event  data
filename = 'RsqTask-%s-%d-%s'%(expInfo['subject'], expInfo['session'], dateStr) #'Sart-' + expInfo['subject'] + '-' + expInfo['session'] + '-' + dateStr
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
# ===== GET SCREEN RES ===== #
# ========================== #

# kluge for secondary monitor
if params['fullScreen']: 
    screens = AppKit.NSScreen.screens()
    screenRes = (int(screens[params['screenToShow']].frame().size.width), int(screens[params['screenToShow']].frame().size.height))
#    screenRes = [1920, 1200]
    if params['screenToShow']>0:
        params['fullScreen'] = False
else:
    screenRes = [800,600]

print "screenRes = [%d,%d]"%screenRes


# ========================== #
# ===== SET UP STIMULI ===== #
# ========================== #
from psychopy import visual

# Initialize deadline for displaying next frame
tNextFlip = [0.0] # put in a list to make it mutable? 

#create clocks and window
globalClock = core.Clock()#to keep track of time
win = visual.Window(screenRes, fullscr=params['fullScreen'], allowGUI=False, monitor='testMonitor', screen=params['screenToShow'], units='deg', name='win',rgb=[1,1,1])

# create stimuli
fCS = params['fixCrossSize'] # size (for brevity)
fCP = params['fixCrossPos'] # position (for brevity)
fixation = visual.ShapeStim(win,lineColor='#000000',lineWidth=3.0,vertices=((fCP[0]-fCS/2,fCP[1]),(fCP[0]+fCS/2,fCP[1]),(fCP[0],fCP[1]),(fCP[0],fCP[1]+fCS/2),(fCP[0],fCP[1]-fCS/2)),units='pix',closeShape=False,name='fixCross');
message1 = visual.TextStim(win, pos=[0,+.5], wrapWidth=1.5, color='#000000', alignHoriz='center', name='topMsg', text="aaa",units='norm')
message2 = visual.TextStim(win, pos=[0,-.5], wrapWidth=1.5, color='#000000', alignHoriz='center', name='bottomMsg', text="bbb",units='norm')

# ============================ #
# ======= SUBFUNCTIONS ======= #
# ============================ #

def CoolDown():
    # display cool-down message
    message1.setText("That's the end! ")
    message2.setText("Press 'q' or 'escape' to end the session.")
    win.logOnFlip(level=logging.EXP, msg='Display TheEnd')
#    win.callOnFlip(SendMessage,'Display TheEnd')
    message1.draw()
    message2.draw()
    win.flip()
    thisKey = event.waitKeys(keyList=['q','escape'])
    
    # save experimental info (if we reached here, we didn't have an error)
    toFile(expInfoFilename, expInfo) # save params to file for next time
    
    # exit
    core.quit()


# =========================== #
# ======= RUN PROMPTS ======= #
# =========================== #

# display prompts
if not params['skipPrompts']:
    BasicPromptTools.RunPrompts(topRestPrompts,bottomRestPrompts,win,message1,message2)

# wait for scanner
message1.setText("Waiting for scanner to start...")
message2.setText("(Press '%c' to override.)"%params['triggerKey'].upper())
message1.draw()
message2.draw()
win.logOnFlip(level=logging.EXP, msg='Display WaitingForScanner')
#win.callOnFlip(SendMessage,'Display WaitingForScanner')
win.flip()
event.waitKeys(keyList=params['triggerKey'])
# determine when session should end
tStartSession = globalClock.getTime()
tEndSession = tStartSession + params['tRest']

# wait before first stimulus
fixation.draw()
win.logOnFlip(level=logging.EXP, msg='Display Fixation')
#win.callOnFlip(SendMessage,'Display Fixation')
win.flip()


# =========================== #
# ===== MAIN EXPERIMENT ===== #
# =========================== #

# log rest period
logging.log(level=logging.EXP, msg='---START REST---')
# Wait for rest period to end
while globalClock.getTime()<tEndSession:
    # check for escape keys
    newKeys = event.getKeys(keyList=['q','escape'],timeStamped=globalClock)
    for newKey in newKeys:
        if newKey[0] in ['q','escape']:
            CoolDown()
# log end of rest period
logging.log(level=logging.EXP, msg='---END REST---')

# ============================ #
# ========= RUN QUIZ ========= #
# ============================ #
# display prompts
if not params['skipPrompts']:
    BasicPromptTools.RunPrompts(topQuestionnairePrompts,bottomQuestionnairePrompts,win,message1,message2)

# log questionnaire
logging.log(level=logging.EXP, msg='---START QUESTIONNAIRE---')

# ------- Run the questions ------- #
allKeys = BasicPromptTools.RunQuestions_Move(question_list=questions,options_list=options,win=win,name='Question',upKey=params['upKey'],downKey=params['downKey'],selectKey=params['selectKey'])
# --------------------------------- #

# log end of questionnaire
logging.log(level=logging.EXP, msg='---END QUESTIONNAIRE---')


# exit experiment
CoolDown()

