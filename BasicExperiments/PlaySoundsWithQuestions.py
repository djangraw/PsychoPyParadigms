#!/usr/bin/env python2

# PlaySoundsWithQuestions.py
#
# Play a sound file, then ask a single question on that file.
#
# Created 12/10/14 by DJ.
# Updated 11/9/15 by DJ - cleanup

import os, random
from psychopy import visual, event, core, sound

#declare parameters
trialDur_sec = 3
soundDur_sec = 60
randomize = True

#The path to the sound files - os.getcwd()=the current working directory (where you're running the script from)
sound_dir = 'lectures/'
#sound_dir = os.getcwd()
#Find all .wav files in directory
sounds_all = os.listdir(sound_dir)
sounds_wav = []
for file in sounds_all:
    if file.endswith(".wav"):
        sounds_wav.append(file)
print(sounds_wav)

#declare Q&A
questions_all = ('What is 2+2?','What is 3-2?','What is 3*1?')
options_all = (('1','2','3','4'),('1','2','3','4'),('1','2','3','4'))
answers_all = ('4','1','3')

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



def RunSoundFile(filename,duration):

    # draw fix cross
    fixCross.draw()
    myWin.flip()
    # play sound
    print filename
    newSound = sound.Sound(value=filename)#, sampleRate=48000, bits=24)
    newSound.setVolume(1)
    newSound.play()
    
    # look for key press or time elapse
    clock.reset()
    while True:
        if len(event.getKeys())>0:
            newSound.stop()
            break
    event.clearEvents()


def RunQuestionTrial(question,options,trialDuration):
    # adjust question
    msg_question.setText(question)
    msg_opt.setText("a: %s\nb: %s\nc: %s\nd: %s\n" % options)
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


order = range(0,len(sounds_wav))
if randomize:
    #Randomize our question list
    random.shuffle(order)


# Main Experiment
for i in order:
    
    soundfile = sound_dir + sounds_wav[i]
    question = questions_all[i]
    options = options_all[i]
    answer = answers_all[i]
    
    # play new sound
    RunSoundFile(soundfile,soundDur_sec)
    print 'Played sound file %s for %d s.' %(soundfile, soundDur_sec)
    
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