#!/usr/bin/env python2
"""Implement a sequence learning task 
described in Mason et al., Science 2007 (doi: 10.1126/science.1131295)"""
# SequenceLearningTask.py
# Created 12/17/14 by DJ based on RhythmicTappingTask.py

from psychopy import core, visual, gui, data, event, sound
from psychopy.tools.filetools import fromFile, toFile
import time, numpy as np
from psychopy import logging

# ====================== #
# ===== PARAMETERS ===== #
# ====================== #
# Declare primary task parameters
nBlocks = 4
nTrialsPerBlock = 1
fixDur = 0.5 # before square
squareDur = 0.2
gapDur = 0.5
respDur = 2
ITI = 0.5 # time between end of one trial and beginning of next trial
IBI = 1 # time between end of block/probe and beginning of next block
randomize_seq  = True;
sequences = ([1,2,3,4],[1,2,3,4],[1,2,3,4],[1,2,3,4])
if randomize_seq:
    np.random.shuffle(sequences[0])
    for i in range(1,len(sequences)):
        np.random.shuffle(sequences[i])
        while sequences[i] in sequences[0:i-1]:
            np.random.shuffle(sequences[i])
            


# declare probe parameters
probe_prob = 0 # probablilty that a given trial will be preceded by a probe
probe1_string = 'Where was your attention focused just before this?'
probe1_options = ('Completely on the task','Mostly on the task','Not sure','Mostly on inward thoughts','Completely on inward thoughts')
probe2_string = 'How aware were you of where your attention was?'
probe2_options = ('Very aware','Somewhat aware','Neutral','Somewhat unaware','Very unaware')

# ========================== #
# ===== SET UP STIMULI ===== #
# ========================== #
try:#try to get a previous parameters file
    expInfo = fromFile('lastSequenceLearningParams.pickle')
except:#if not there then use a default set
    expInfo = {'subject':'abc', 'session':'1'}
dateStr = time.strftime("%b_%d_%H%M", time.localtime())#add the current time

#present a dialogue to change params
dlg = gui.DlgFromDict(expInfo, title='Sequence Learning task', fixed=['date'])
if dlg.OK:
    toFile('lastSequenceLearningParams.pickle', expInfo)#save params to file for next time
else:
    core.quit()#the user hit cancel so exit

#make a text file to save data
fileName = 'SequenceLearning-' + expInfo['subject'] + '-' + expInfo['session'] + '-' + dateStr
dataFile = open(fileName+'.txt', 'w')
dataFile.write('key	RT	AbsTime\n')

#create window and stimuli
globalClock = core.Clock()#to keep track of time
trialClock = core.Clock()#to keep track of time
win = visual.Window([800,600],allowGUI=False, monitor='testMonitor', units='deg')
fixation = visual.GratingStim(win, color='black', tex=None, mask='circle',size=0.2)
message1 = visual.TextStim(win, pos=[0,+3],text="You will see a pattern of 4 squares, followed by one or more arrows. If an arrow points to the right, repeat the pattern you saw on the number keys (1-4). If it points to the left, repeat the pattern backwards.")
message2 = visual.TextStim(win, pos=[0,-3], text="When you're ready to begin, press any key.")

# make squares
squares = []
for i in range(0,4):
    xpos = i*2-3
    squares.append(visual.Rect(win,pos=[xpos,0], width=1, height=1, lineColor='black',fillColor='gray'))
# make arrows
line = visual.Line(win,start=(-2,0),end=(2,0),lineColor='black')
leftArrow = visual.Polygon(win,edges=3,radius=0.5,pos=(-2,0),ori=30,lineColor='black',fillColor='black')
rightArrow = visual.Polygon(win,edges=3,radius=0.5,pos=(2,0),ori=-30,lineColor='black',fillColor='black')

# ========================== #
# ===== SET UP LOGGING ===== #
# ========================== #
logging.LogFile((fileName+'.log'), level=logging.INFO)#, mode='w') # w=overwrite
logging.log(level=logging.INFO, msg='Subject %s, Session %s'%(expInfo['subject'],expInfo['session']))
for i in range(0,len(sequences)):
    logging.log(level=logging.INFO, msg='sequence %d: %s'%(i,sequences[i]))

# ============================ #
# ======= SUBFUNCTIONS ======= #
# ============================ #

def PlaySequence(sequence):
    # get block start time
    tBlock = globalClock.getTime()*1000
    
    #draw fixation dot
    fixation.draw()
    win.logOnFlip(level=logging.EXP, msg='Fixation')
    win.flip()
    core.wait(fixDur)#wait for specified ms (use a loop of x frames for more accurate timing)
    
    # display squares
    for i in range(0,len(sequence)):
        # set
        squares[sequence[i]-1].setFillColor('black')
        if i>0:
            squares[sequence[i-1]-1].setFillColor('gray')
        # redraw
        for j in range(0,4):
            squares[j].draw()
        win.logOnFlip(level=logging.EXP, msg='Square %d/%d'%(i+1,len(sequence)))
        win.flip()
        core.wait(squareDur,squareDur)
    squares[sequence[-1]-1].setFillColor('gray') # set back to gray for next trial
    return tBlock


def RunTrial(goForward,nKeys):
    
    # get trial start time
    tTrial = globalClock.getTime()*1000
    # reset trial clock
    trialClock.reset()
    # clear event buffer
    event.clearEvents()
    
    # display response direction
    line.draw()
    if goForward:
        rightArrow.draw()
        win.logOnFlip(level=logging.EXP, msg='Right Arrow')
    else:
        leftArrow.draw()
        win.logOnFlip(level=logging.EXP, msg='Left Arrow')
    win.flip()
    # wait for responses
#    core.wait(respDur) 
    
    #get responses
    allKeys = []
    while len(allKeys)<nKeys and trialClock.getTime()<respDur:
        newKeys = event.getKeys(timeStamped=trialClock)
        for thisKey in newKeys:
            allKeys.append(thisKey) #,keyList=['1','2','3','4','q','Escape']
        
#    allKeys = event.getKeys(timeStamped=trialClock)
    return (tTrial,allKeys)


def RunProbes():
    # reset clock
    trialClock.reset()
    # set up stimuli
    message1.setText(probe1_string)
    message2.setText("1) %s\n2) %s\n3) %s\n4) %s\n5) %s" % probe1_options)
    message1.draw()
    message2.draw()
    win.logOnFlip(level=logging.EXP, msg='Probe 1')
    win.flip()
    
    # get response
    key1 = event.waitKeys(keyList=['1','2','3','4','5','q','Escape'],timeStamped=trialClock)
    
    # reset clock
    trialClock.reset()
    # set up stimuli
    message1.setText(probe2_string)
    message2.setText("1) %s\n2) %s\n3) %s\n4) %s\n5) %s" % probe2_options)
    message1.draw()
    message2.draw()
    win.logOnFlip(level=logging.EXP, msg='Probe 2')
    win.flip()
    
    # get response
    key2 = event.waitKeys(keyList=['1','2','3','4','5','q','Escape'],timeStamped=trialClock)
    
    # return results
    return (key1[0],key2[0])
    

# =========================== #
# ===== MAIN EXPERIMENT ===== #
# =========================== #
#display instructions and wait
message1.draw()
message2.draw()
win.logOnFlip(level=logging.EXP, msg='Instructions')
win.flip()
#check for a keypress
event.waitKeys()

# do brief wait before first stimulus
fixation.draw()
win.logOnFlip(level=logging.EXP, msg='Fixation')
win.flip()
core.wait(ITI)

for iBlock in range(0,nBlocks): #will step through the blocks
    
    # determine sequence
    iSeq = np.random.choice(range(0,len(sequences)))
    sequence = sequences[iSeq]
    logging.log(level=logging.EXP, msg='Block %d, Sequence %d: %s'%(iBlock,iSeq,sequence))
    # play sequence
    tBlock = PlaySequence(sequence)
    core.wait(gapDur)#wait for specified ms (use a loop of x frames for more accurate timing)
    
    for iTrial in range(0,nTrialsPerBlock):
        # determine direction
        goForward = np.random.random()>0.5
        logging.log(level=logging.EXP, msg='Trial %d, goForward %r'%(iTrial,goForward))
        # Run Trial
        (tTrial,allKeys) = RunTrial(goForward,len(sequence))
        
        # Evaluate results
        for thisKey in allKeys:
            keyChar = thisKey[0]
            RT = thisKey[1]*1000 # in ms
            #log the data
            dataFile.write('%s	%.1f	%.1f\n' %(keyChar, RT, RT+tTrial))
            print("key=%s, RT=%.1f"%(keyChar,RT))
            # look for escape character
            if thisKey[0] in ['q', 'escape']:
                core.quit()#abort experiment
        event.clearEvents('mouse')#only really needed for pygame windows
        # do ITI
        fixation.draw()
        win.flip()
        core.wait(ITI)
    
    # Run probe trial
    if (np.random.random() < probe_prob):
        # run probe trial
        allKeys = RunProbes()
        # check for escape keypresses
        for thisKey in allKeys:
            if thisKey[0] in ['q', 'escape']:
                core.quit()#abort experiment
        event.clearEvents('mouse')#only really needed for pygame windows
        # record keypresses
        attentionLevel = allKeys[0][0]
        attentionRT = allKeys[0][1]*1000
        awarenessLevel = allKeys[1][0]
        awarenessRT = allKeys[1][1]*1000
        #log the data
        print('Probe: attention %s, awareness %s'%(attentionLevel,awarenessLevel))
        dataFile.write('Probe1	%.1f	%s\n' %(attentionRT, attentionLevel))
        dataFile.write('Probe2	%.1f	%s\n' %(awarenessRT, awarenessLevel))
    
    # do IBI
    fixation.draw()
    win.flip()
    core.wait(IBI)

# close log file
dataFile.close()

#give some performance output to user
print('Performance:')
#print('%d/%d = %.2f%% correct' %(np.sum(isCorrect_alltrials), len(isCorrect_alltrials), 100*np.average(isCorrect_alltrials)))
#RT_correct = RT_alltrials[np.logical_and(isCorrect_alltrials, np.logical_not(isTarget_alltrials))]
#print('RT: std/mean = %f/%f = %.4f' %(np.std(RT_correct),np.average(RT_correct),np.std(RT_correct)/np.average(RT_correct)))
# exit experiment
core.quit()
