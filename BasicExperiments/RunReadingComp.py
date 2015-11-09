#!/usr/bin/env python2

# RunReadingComprehension.py
# Created 12/11/14 by DJ based on PlaySoundsWithQuestions.py.
# Updated 11/9/15 by DJ - cleanup

import os, random
from psychopy import visual, event, core, sound

#declare parameters
questionDur_sec = 8 # time between questions
randomize_questions = True
#nTrials = 3
ITI_min = 1.5 # in seconds
ITI_range = 1.0 # in seconds. ITI will range from ITI_min to (ITI_min+ITI_range)

#The path to the sound files - os.getcwd()=the current working directory (where you're running the script from)
sound_dir = 'ReadingComp/'
soundfile = 'woodpecker.aiff'#'abigailadams.aiff'
questionfile = 'woodpecker_questions.txt'#'abigailadams_questions.txt'

# read words from text file
questions_all = []
answers_all = []
options_all = []
options_this = []
with open(sound_dir+questionfile) as f:
    for line in f:
        if line.startswith("  ?"): # incorrect answer
            options_this.append(line[5:-1]) # omit leading ? and trailing newline
        elif line.startswith(":-)"): # correct answer
            options_this.append(line[5:-1]) # omit leading text and trailing newline
            answers_all.append(len(options_this))
        else: # question
            questions_all.append(line[:-1]) # omit trailing newline char
            # if it's not the first question, add the options to the list.
            if options_this:
                options_all.append(options_this)
                options_this = []
nQuestions = len(options_all)

# DEBUGGING: print options
#for options in options_all:
#    print options

#create a window to draw in
myWin =visual.Window((600,600), allowGUI=False,
    bitsMode=None, units='norm', winType='pyglet')
msg_question =visual.TextStim(myWin,text='Hit Q to quit',
    pos=(0,0.5), height=0.08, wrapWidth=1.5)
msg_opt = visual.TextStim(myWin,text='Or Escape.',
    pos=(0,-0.5), height=0.08, wrapWidth=1.5)
fixCross = visual.TextStim(myWin,text='+',pos=(0,0))

#Create a clock object.
clock = core.Clock()


# Play the requested lecture as a sound file until the user presses a key.
def PlayLecture(filename):
    # draw fix cross
    fixCross.draw()
    myWin.flip()
    # set up sound
    sound1 = sound.Sound(value=filename)#, sampleRate=48000, bits=24)
    sound1.setVolume(1)
    # play sound
    sound1.play()
    
    # look for key press
    clock.reset()
    while True:
        if len(event.getKeys())>0: 
            # stop lecture if key was pressed
            sound1.stop()
            break
    event.clearEvents()


def RunQuestionTrial(question,options,trialDuration):
    # adjust question & answers
    msg_question.setText(question)
    msg_opt.setText("1: %s\n2: %s\n3: %s\n4: %s\n" % (options[0], options[1], options[2], options[3]))
    # draw question & answers
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



# ======================= #
# === MAIN EXPERIMENT ===
# ======================= #

# Learning Portion
# play lecture
PlayLecture(sound_dir+soundfile)

# pause briefly
ITI = ITI_min + (ITI_range * random.random())
core.wait(ITI)


# Testing Portion
# shuffle questions
question_order = range(0,nQuestions)
if randomize_questions:
    random.shuffle(question_order)

# present questions & options
for i in question_order:
    
    #get question, options
    question = questions_all[i]
    options = options_all[i]
    answer = answers_all[i]
    
    #display new question
    keys = RunQuestionTrial(question,options,questionDur_sec)
    
    # print trial number
    print "---Question %d ---" %(i+1)
    print question
    print "(Answer = %d: %s)" % (answer,options[answer-1])
    # log result
    for key in keys:
        if key[0] == str(answer):
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