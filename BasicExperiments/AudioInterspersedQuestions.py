#!/usr/bin/env python2

# AudioInsterspersedQuestions.py
# Created 12/15/14 by DJ based on PlaySoundsWithQuestions.py.
# Updated 11/9/15 by DJ - cleanup

import os, random
from psychopy import visual, event, core, sound

#declare parameters
trialDur_sec = 5
soundDur_sec = 80
randomize = False

#The path to the sound files - os.getcwd()=the current working directory (where you're running the script from)
sound_dir = 'lectures/'
sound_file = '15MinHistory_Episode01_TheFebruaryRevolutionOf1917.wav'

#declare Q&A
question_times = (5.5,15.5,23.5)#(20, 40, 60)
questions_all = ('In what year did the revolution occur?','Who was the Czar?','what party came to power in October?')
options_all = (('1901','1917','1923','1944'),('Nicholas II','Christopher I','Josef I','Alexander III'),('Liberal Democrat Party','Fascist Party','Extreme Socialist Party','Communist Party'))
answers_all = ('2','1','3')

#create a window to draw in
myWin =visual.Window((600,600), allowGUI=False,
    bitsMode=None, units='norm', winType='pyglet')
msg_question =visual.TextStim(myWin,text='Hit Q to quit',
    pos=(0,0.5))
msg_opt = visual.TextStim(myWin,text='Or Escape.',
    pos=(0,-0.5))
fixCross = visual.TextStim(myWin,text='+',pos=(0,0))

#Create a clock object.
clock = core.Clock()



def RunSoundFile(filename,startTime,duration):

    # draw fix cross
    fixCross.draw()
    myWin.flip()
    # play sound
    print filename
    newSound = sound.Sound(value=filename,start=startTime)#, sampleRate=48000, bits=24)
    newSound.setVolume(1)
    newSound.play()
    
    # look for key press or time elapse
    clock.reset()
    while clock.getTime() < duration:
        if len(event.getKeys())>0:
            break
    newSound.stop()
    event.clearEvents()


def RunQuestionTrial(question,options,trialDuration):
    # adjust question
    msg_question.setText(question)
    msg_opt.setText("1: %s\n2: %s\n3: %s\n4: %s\n" % options)
    # draw question
    msg_question.draw()
    msg_opt.draw()
    
     #Flush the key buffer and mouse movements
    event.clearEvents()
    #Put the image on the screen
    myWin.flip()
    #Reset our clock to zero  - I think this call should take less time than window.flip, so resetting after the flip should be slightly more accurate.
    clock.reset()
    #Wait for trialDuration seconds.  Tie up the CPU the entire time (this is more accurate than letting other processes go)
    core.wait(trialDuration,trialDuration)
    #Get a list of all keys that were pressed during our wait.  Tell it to give also give us the amount of time since our clock was reset when the key was pressed (reaction time).
    keypresses = event.getKeys(None,clock)
    return keypresses


order = range(0,len(questions_all))
if randomize:
    #Randomize our question list
    random.shuffle(order)


# Main Experiment
soundfile = sound_dir + sound_file
for i in range(0,len(questions_all)):
    
    question = questions_all[order[i]]
    options = options_all[order[i]]
    answer = answers_all[order[i]]
    
    if i==0:
        startTime = 0
        duration = question_times[i]
    else:
        startTime = question_times[i-1]
        duration = question_times[i] - question_times[i-1]
    
    # play new sound
    RunSoundFile(soundfile,startTime,duration)
    print 'Played sound file %s for %d s.' %(soundfile, duration)
    
    #display new question
    keys = RunQuestionTrial(question,options,trialDur_sec)
    
    # print trial number
    print "Question %d:" %i
    # log result
    for key in keys:
        if key[0] == answer:
            print "Correct!"
        else:
            print "Incorrect."
        print "Key: %s  RT: %.3f" %(key[0],key[1]*1000)
    
        # check for end command
        if key[0] in ['escape','q']:
            # abort experiment
            print 'Experiment aborted by user.'
            myWin.close()
            core.quit()
    event.clearEvents('mouse')#only really needed for pygame windows