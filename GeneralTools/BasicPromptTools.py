#!/usr/bin/env python2
"""Load Questions, Run Prompts, and Run Probe Trials."""
# BasicPromptTools.py
# Created 1/30/15 by DJ based on VidLecTask.py - called PromptTools.py.
# Updated 3/16/15 by DJ - added ReadingTask_dict.py
# Updated 9/8/15 by DJ - added Likert option and RunQuestions_Move.
# Updated 10/29/15 by DJ - updated distraction/reading task prompts to ask subjects to read top to bottom.
# Updated 11/9/15 by DJ - added ParsePromptFile function, pared down and renamed to BasicPromptTools.py
# Updated 11/12/15 by DJ - moved visual package import to fns so it doesn't interfere with parent script's GUI (weird PsychoPy bug)
# Updated 9/13/18 by DJ - added ignoreKeys parameter to RunPrompts function (for trigger keys)
# Updated 10/11/18 by DJ - prevent RunPrompts from redrawing/logging every time an ignored key is pressed.

from psychopy import core, event, logging#, visual
import time


# --- PARSE QUESTION FILE INTO QUESTIONS AND OPTIONS --- #
def ParseQuestionFile(filename,optionsType=None): # optionsType 'Likert' returns the Likert scale for every question's options.
    # initialize
    questions_all = []
    answers_all = []
    options_all = []
    if optionsType is None:
        options_this = []
    elif optionsType == 'Likert':
        options_likert = ['Strongly agree','Agree','Neutral','Disagree','Strongly disagree']
        options_this = options_likert
        
    # parse questions & answers
    with open(filename) as f:
        for line in f:
            # remove the newline character at the end of the line
            line = line.replace('\n','')
            # replace any newline strings with newline characters
            line = line.replace('\\n','\n')
            # pass to proper output
            if line.startswith("-"): # incorrect answer
                options_this.append(line[1:]) # omit leading -
            elif line.startswith("+"): # correct answer
                options_this.append(line[1:]) # omit leading +
                answers_all.append(len(options_this))
            elif line.startswith("?"): # question
                questions_all.append(line[1:]) # omit leading ?
                # if it's not the first question, add the options to the list.
                if options_this:
                    options_all.append(options_this)
                    if optionsType is None:
                        options_this = [] #reset
                    elif optionsType == 'Likert':
                        options_this = options_likert
                        
    # make sure last set of options is included
    options_all.append(options_this) 
    # return results
    return (questions_all,options_all,answers_all)

# --- PARSE PROMPT FILE INTO TOP AND BOTTOM PROMPTS --- #
# Each top prompt should be preceded by a +. Each bottom prompt should be preceded by a -. Everything else will be ignored.
def ParsePromptFile(filename): 
    # initialize
    topPrompts = []
    bottomPrompts = []
        
    # parse questions & answers
    with open(filename) as f:
        for line in f:
            # remove the newline character at the end of the line
            line = line.replace('\n','')
            # replace any newline strings with newline characters
            line = line.replace('\\n','\n')
            # pass to proper output
            if line.startswith("-"): # bottom prompt
                bottomPrompts.append(line[1:]) # omit leading -
            elif line.startswith("+"): # top prompt
                topPrompts.append(line[1:]) # omit leading +
                # if it's not the first question, add the options to the list.
                        
    # return results
    return (topPrompts,bottomPrompts)

# Display prompts and let the subject page through them one by one.
def RunPrompts(topPrompts,bottomPrompts,win,message1,message2,backKey='backspace',backPrompt=0,name='Instructions',ignoreKeys=[]):
    iPrompt = 0
    redraw = True # redraw a new prompt?
    while iPrompt < len(topPrompts):
        if redraw:
            message1.setText(topPrompts[iPrompt])
            message2.setText(bottomPrompts[iPrompt])
            #display instructions and wait
            message1.draw()
            message2.draw()
            win.logOnFlip(level=logging.EXP, msg='Display %s%d'%(name,iPrompt+1))
            win.flip()
        #check for a keypress
        thisKey = event.waitKeys()
        if thisKey[0] in ['q','escape']:
            core.quit()
        elif thisKey[0] == backKey:
            iPrompt = backPrompt
            redraw = True
        elif thisKey[0] in ignoreKeys:
            redraw = False
            pass # ignore these keys
        else:
            iPrompt += 1
            redraw = True


# Display questions and let user select each one's answer with a single keypress.
def RunQuestions(question_list,options_list,win,message1,message2, name='Question', questionDur=float('inf'), isEndedByKeypress=True,respKeys=['1','2','3','4']):
    # set up
    nQuestions = len(question_list)
    allKeys = ['']*nQuestions
    trialClock = core.Clock()
    iQ = 0
    while iQ < nQuestions:
        print('iQ = %d/%d'%(iQ+1,nQuestions))
        # get response lists
        respText = "" # to be displayed to subject
#        respKeys = [] # allowable responses
        for iResp in range(0,len(options_list[iQ])):
            respText += '%d) %s\n'%((iResp+1),options_list[iQ][iResp])
#            respKeys += str(iResp+1)
        # set text
        message1.setText(question_list[iQ])
        message2.setText(respText)
        
        # draw question & answers
        message1.draw()
        message2.draw()
        
        #Flush the key buffer and mouse movements
        event.clearEvents()
        #Put the image on the screen
        win.logOnFlip(level=logging.EXP, msg='Display %s%d'%(name,iQ));
        win.flip()
        #Reset our clock to zero  - I think this call should take less time than window.flip, so resetting after the flip should be slightly more accurate.
        trialClock.reset()
        # Wait for keypress
        endQuestion = False;
        while (trialClock.getTime()<questionDur and not endQuestion):
            newKeys = event.getKeys(keyList=(respKeys + ['q','escape','backspace','period']),timeStamped=trialClock)
            for newKey in newKeys:
                # check for quit keys
                if newKey[0] in ['q', 'escape']:
                    endQuestion = True; # end the loop
                elif newKey[0] == 'backspace':
                    print('backspace')
                    iQ = max(0,iQ-1) # go back one
                    endQuestion = True;
                elif newKey[0] == 'period': 
                    iQ +=1 # skip fwd without recording response
                    endQuestion = True;
                else: # ok response keys 
                    iA = respKeys.index(newKey[0]) # convert from key to index in respKeys list
                    allKeys[iQ] = (iA+1, newKey[1]) # make new tuple with answer index and response time
                    # allKeys[iQ] = newKey
                    iQ +=1
                    if isEndedByKeypress:
                        endQuestion = True;
        
        if len(newKeys)>0 and newKey[0] in ['q', 'escape']: 
            break # end the loop
    # return result
    return allKeys


# Display questions and let the subject navigate selection up and down before selecting.
def RunQuestions_Move(question_list,options_list, win, name='Question', questionDur=float('inf'), isEndedByKeypress=True, upKey='up', downKey='down', selectKey='enter'):
    # import visual package
    from psychopy import visual
    # set up
    nQuestions = len(question_list)
    allKeys = ['']*nQuestions
    trialClock = core.Clock()
    iQ = 0
    iA = 0
    respKeys=[upKey,downKey,selectKey]
    # make visuals
    questionText = visual.TextStim(win, pos=[0,+.5], wrapWidth=1.5, color='#000000', alignHoriz='center', name='questionText', text="aaa",units='norm')
    optionsText = []
    for iResp in range(0,len(options_list[0])):
        optionsText.append(visual.TextStim(win, pos=[0,-.1*iResp], wrapWidth=1.5, color='#000000', alignHoriz='center', name='option%d'%(iResp+1), text="aaa",units='norm',autoLog=False))
    
    while iQ < nQuestions:
        print('iQ = %d/%d'%(iQ+1,nQuestions))
        # default response is middle response (and round down)
        iA = int((len(options_list[iQ])-1)*0.5)
        # set and draw text
        questionText.setText(question_list[iQ])
        questionText.draw()
        optionsText[iA].bold = True # make currently selected answer bold
        for iResp in range(0,len(options_list[iQ])):
            optionsText[iResp].setText('%d) %s'%((iResp+1),options_list[iQ][iResp]))
            optionsText[iResp].draw()
                
        # Flush the key buffer and mouse movements
        event.clearEvents()
        # Put the image on the screen
        win.logOnFlip(level=logging.EXP, msg='Display %s%d'%(name,iQ));
        win.flip()
        # Reset our clock to zero  - I think this call should take less time than window.flip, so resetting after the flip should be slightly more accurate.
        trialClock.reset()
        # Wait for keypress
        endQuestion = False;
        while (trialClock.getTime()<questionDur and not endQuestion):
            newKeys = event.getKeys(keyList=(respKeys + ['q','escape','backspace','period']),timeStamped=trialClock)
            for newKey in newKeys:
                # check for quit keys
                if newKey[0] in ['q', 'escape']:
                    endQuestion = True; # end the loop
                elif newKey[0] == 'backspace':
                    print('backspace')
                    iQ = max(0,iQ-1) # go back one
                    endQuestion = True;
                elif newKey[0] == 'period': 
                    iQ +=1 # skip fwd without recording response
                    endQuestion = True;
                elif newKey[0] == upKey: # move response up
                    # remove old bold
                    optionsText[iA].bold = False
                    # update answer
                    iA -= 1
                    if iA<0:
                        iA=0
                    # make newly selected answer bold
                    optionsText[iA].bold = True
                    # redraw everything
                    questionText.draw()
                    for iResp in range(0,len(options_list[iQ])):
                        optionsText[iResp].draw()
                    win.flip()
                elif newKey[0] == downKey: # move response down
                    # remove old bold
                    optionsText[iA].bold = False
                    # update answer
                    iA += 1
                    if iA>=len(options_list[iQ]):
                        iA = len(options_list[iQ])-1
                    # make newly selected answer bold
                    optionsText[iA].bold = True
                    # redraw everything
                    questionText.draw()
                    for iResp in range(0,len(options_list[iQ])):
                        optionsText[iResp].draw()
                    win.flip()
                elif newKey[0] == selectKey:
                    # log response
                    allKeys[iQ] = (iA+1, newKey[1]) # make new tuple with answer index and response time
                    logging.log(level=logging.EXP, msg= 'Responded %d'%(iA+1))
                    # remove old bold
                    optionsText[iA].bold = False
                    # advance question index
                    iQ +=1
                    if isEndedByKeypress:
                        endQuestion = True;
                else:
                    print('pressed %s'%newKey[0])
        
        if len(newKeys)>0 and newKey[0] in ['q', 'escape']: 
            break # end the loop
    # return result
    return allKeys
