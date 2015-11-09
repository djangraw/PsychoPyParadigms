#!/usr/bin/env python2

# LearnNonsenseWords.py
# Created 12/11/14 by DJ based on PlaySoundsWithQuestions.py.
# Updated 11/9/15 by DJ - cleanup

import os, random
from psychopy import visual, event, core, sound

#declare parameters
questionDur_sec = 5 # time between questions
randomize_words = True
randomize_questions = True
nTrials = 3
ITI_min = 1.5 # in seconds
ITI_range = 1.0 # in seconds. ITI will range from ITI_min to (ITI_min+ITI_range)

#The path to the sound files - os.getcwd()=the current working directory (where you're running the script from)
sound_dir = 'nonsensewords/'
wordfile = 'twosyllablewords.txt'

# read words from text file
with open(sound_dir+wordfile) as f:
    words = f.readlines()
# remove newline characters
words = [x.strip(' \n') for x in words]

# assign pairs
if randomize_words:
    #Randomize our question list
    random.shuffle(words)

i=0
pairs = []
while (i+1) < len(words):
    print(words[i])
    pairs.append((words[i], words[i+1]))
    i+=2
    
print "len(words) = %d" % len(words)
print "len(pairs) = %d" % len(pairs)


#create a window to draw in
myWin =visual.Window((600,600), allowGUI=False,
    bitsMode=None, units='norm', winType='pyglet')
msg_question =visual.TextStim(myWin,text='Hit Q to quit',
    pos=(0,0.5))
msg_opt = visual.TextStim(myWin,text='Or Escape.',
    pos=(0,-0.5))
fixCross = visual.TextStim(myWin,text='+',pos=(0,0))
# create reusable sounds
sound_theword = sound.Sound(value=sound_dir+'theword.aiff')#, sampleRate=48000, bits=24)
sound_theword.setVolume(1)
sound_means = sound.Sound(value=sound_dir+'means.aiff')#, sampleRate=48000, bits=24)
sound_means.setVolume(1)

#Create a clock object.
clock = core.Clock()



def PlayWordPair(word1,word2):

    # draw fix cross
    fixCross.draw()
    myWin.flip()
    # set up sound
    sound1 = sound.Sound(value=sound_dir+word1+'.aiff')#, sampleRate=48000, bits=24)
    sound1.setVolume(1)
    sound2 = sound.Sound(value=sound_dir+word2+'.aiff')#, sampleRate=48000, bits=24)
    sound2.setVolume(1)
    # play sound
    sound_theword.play()
    core.wait(sound_theword.getDuration())
    sound1.play()
    core.wait(sound1.getDuration())
    sound_means.play()
    core.wait(sound_means.getDuration())
    sound2.play()
    core.wait(sound2.getDuration())
    
#    # look for key press or time elapse
#    clock.reset()
#    while True:
#        if len(event.getKeys())>0:
#            newSound.stop()
#            break
#    event.clearEvents()


def RunQuestionTrial(word1,options,trialDuration):
    # adjust question & answers
    msg_question.setText("%s = ?" % word1)
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


# === MAIN EXPERIMENT ===
# Learning Portion
for i in range(0,nTrials):
    #get word pair
    (word1, word2) = pairs[i]
    
    # play word pair
    PlayWordPair(word1,word2)
    
    # pause briefly
    ITI = ITI_min + (ITI_range * random.random())
    core.wait(ITI)


# Testing Portion
question_order = range(0,nTrials)
if randomize_questions:
    random.shuffle(question_order)

for i in question_order:
    
    #get word pair
    (word1, word2) = pairs[i]
    options = []
    #assign 4 answers at random
    for i in range(0,4):
        randomword = word1
        while randomword in [word1, word2] + options:
            randomword = random.choice(words)
        options.append(randomword)
    
    #replace one with the correct answer
    answer = random.choice(range(0,len(options)))+1
    options[answer-1] = word2
    
    #display new question
    keys = RunQuestionTrial(word1,options,questionDur_sec)
    
    # print trial number
    print "---Question %d ---" %i
    print "%s = %s" %(word1,word2)
    print "(Answer = %d)" % answer
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