#!/usr/bin/env python2
"""Ask the subject comprehension questions at the end of a reading task."""
# ReadingTask_questions_d2.py.
# Created 4/16/15 by DJ based on ReadingTask_eyelink_d1.py.
# Updated 10/30/15 by DJ - switched to audio 22min question file.

from psychopy import core, gui, data, event, sound, logging #, visual # visual causes a bug in the guis, so I moved it down.
from psychopy.tools.filetools import fromFile, toFile
import time as ts, numpy as np
import AppKit, os # for monitor size detection, files
import PromptTools
import random

# ====================== #
# ===== PARAMETERS ===== #
# ====================== #
# Save the parameters declared below?
saveParams = True;
newParamsFilename = 'ReadingQuestionParams_L10.pickle'
expInfoFilename = 'lastReadingQuestionInfo.pickle'

# Declare primary task parameters.
params = {
    'skipPrompts': False,      # go right to the scanner-wait page
    'tStartup': 3,            # pause time before starting first page
    'triggerKey': 't',        # key from scanner that says scan is starting
# declare movie and question files
    'textDir': 'questions/', # directory containing questions and probes
    'questionsFile': 'Lecture10Questions_d4_audio_22min.txt', # 'Lecture02Questions_d3.txt', #
    'promptType': 'TestSound', # 'Test', # option in PromptTools.GetPrompts (options are ['Test','TestBoth','TestSound'])
# declare other stimulus parameters
    'fullScreen': True,       # run in full screen mode?
    'screenToShow': 0,        # display on primary screen (0) or secondary (1)?
    'screenColor':(128,128,128),
    'fixCrossSize': 10,       # size of cross, in pixels
    'fixCrossPos': [0,0], # (x,y) pos of fixation cross displayed before each page (for drift correction)
    'randomizeOrder': True, # randomize order of questions?
    'questionOrder': None
}

# read questions and answers from text file
[questions_all,options_all,answers_all] = PromptTools.ParseQuestionFile(params['textDir']+params['questionsFile'])
print('%d questions loaded from %s'%(len(questions_all),params['questionsFile']))

if params['randomizeOrder']:
    newOrder = range(0,len(questions_all))
    random.shuffle(newOrder)
    questions_all = [questions_all[i] for i in newOrder]
    options_all = [options_all[i] for i in newOrder]
    answers_all = [answers_all[i] for i in newOrder]
    params['questionOrder'] = newOrder
#    logging.log(level=logging.INFO, msg='questionOrder: ' + str(newOrder))

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
    expInfo = fromFile(expInfoFilename)
    expInfo['session'] +=1 # automatically increment session number
    expInfo['paramsFile'] = [expInfo['paramsFile'],'Load...']
except:#if not there then use a default set
    expInfo = {'subject':'1', 'session':1, 'paramsFile':['DEFAULT','Load...']}
# overwrite if you just saved a new parameter set
if saveParams:
    expInfo['paramsFile'] = [newParamsFilename,'Load...']
dateStr = ts.strftime("%b_%d_%H%M", ts.localtime()) # add the current time

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
    

#make a log file to save parameter/event  data
filename = 'ReadingQuestion-%s-%d-%s'%(expInfo['subject'], expInfo['session'], dateStr) #'Sart-' + expInfo['subject'] + '-' + expInfo['session'] + '-' + dateStr
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

#create window and stimuli
globalClock = core.Clock()#to keep track of time
win = visual.Window(screenRes, fullscr=params['fullScreen'], allowGUI=False, monitor='testMonitor', screen=params['screenToShow'], units='deg', name='win',color=params['screenColor'],colorSpace='rgb255')
fCS = params['fixCrossSize'] # size (for brevity)
fCP = params['fixCrossPos'] # position (for brevity)
fixation = visual.ShapeStim(win,lineColor='#000000',lineWidth=3.0,vertices=((fCP[0]-fCS/2,fCP[1]),(fCP[0]+fCS/2,fCP[1]),(fCP[0],fCP[1]),(fCP[0],fCP[1]+fCS/2),(fCP[0],fCP[1]-fCS/2)),units='pix',closeShape=False,name='fixCross');
message1 = visual.TextStim(win, pos=[0,+.5], wrapWidth=1.5, color='#000000', alignHoriz='center', name='topMsg', text="aaa",units='norm')
message2 = visual.TextStim(win, pos=[0,-.5], wrapWidth=1.5, color='#000000', alignHoriz='center', name='bottomMsg', text="bbb",units='norm')

# Look up prompts
[topPrompts,bottomPrompts] = PromptTools.GetPrompts(os.path.basename(__file__),params['promptType'],params)
print('%d prompts loaded from %s'%(len(topPrompts),'PromptTools.py'))



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
nextFlipTime = (tStartSession+params['tStartup'])

# wait before first stimulus
fixation.draw()
win.logOnFlip(level=logging.EXP, msg='Display Fixation')
win.flip()
# wait until it's time to start
while globalClock.getTime()<nextFlipTime:
    fixation.draw()
    win.flip()


# =========================== #
# ===== MAIN EXPERIMENT ===== #
# =========================== #


# set up other stuff
logging.log(level=logging.EXP, msg='---START EXPERIMENT---')

# ------- Run the questions ------- #
allKeys = PromptTools.RunQuestions(questions_all,options_all,win,message1,message2,'Question')
# --------------------------------- #

# check for escape keypresses
#for thisKey in allKeys:
#    if len(thisKey)>0 and thisKey[0] in ['q', 'escape']: # check for quit keys
#        core.quit()#abort experiment
        
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

# display cool-down message
message1.setText("That's the end! Please stay still until the scan is complete.")
message2.setText("(Press 'q' or 'escape' to override.)")
win.logOnFlip(level=logging.EXP, msg='Display TheEnd')
message1.draw()
message2.draw()
win.flip()
thisKey = event.waitKeys(keyList=['q','escape'])

# save experimental info (if we reached here, we didn't have an error)
toFile(expInfoFilename, expInfo) # save params to file for next time

# exit experiment
core.quit()
