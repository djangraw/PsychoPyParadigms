#!/usr/bin/env python2
"""Load Questions, Run Prompts, and Run Questions."""
# QuestionTools.py
# Created 9/9/15 by DJ as a trimmed-down version of PromptTools.

from psychopy import core, event, logging, visual
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


# Display prompts and let the subject page through them one by one.
def RunPrompts(topPrompts,bottomPrompts,win,message1,message2,backKey='backspace',backPrompt=0):
    iPrompt = 0
    while iPrompt < len(topPrompts):
        message1.setText(topPrompts[iPrompt])
        message2.setText(bottomPrompts[iPrompt])
        #display instructions and wait
        message1.draw()
        message2.draw()
        win.logOnFlip(level=logging.EXP, msg='Display Instructions%d'%(iPrompt+1))
        win.flip()
        #check for a keypress
        thisKey = event.waitKeys()
        if thisKey[0] in ['q','escape']:
            core.quit()
        elif thisKey[0] == backKey:
            iPrompt = backPrompt
        else:
            iPrompt += 1


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



# ===== DECLARE PROMPTS ===== %
def GetPrompts(experiment,promptType,params):
    
    if experiment == 'VidLecTask_dict.py':
        if promptType == 'Test':
            # declare default list of prompts
            topPrompts = ["You are about to watch a video of an academic lecture. Keep your eyes open and try to absorb as much of the material as you can.",
                "When the lecture is over, you'll be asked a few questions about it. Answer the questions using the number keys.", 
#                "If at any time you notice that your mind has been wandering, press the '%c' key with your left index finger."%params['wanderKey'].upper(),
#                "Sometimes during the lecture, a question about your attention may appear. When this happens, answer the question within a few seconds using the number keys.",
                "Just before and after the lecture, a cross will appear. Look directly at the cross while it's on the screen."]
    
        elif promptType == 'Reverse':
            # prompts for BACKWARDS MOVIE:    
            topPrompts = ["You are about to watch a video of an academic lecture played backwards. Try to ignore it and think about something else.",
                "This is the LOW ATTENTION RUN: it's extremely important that you do NOT focus on the lecture during this run.",
                "Stay awake and keep your eyes open, but let your mind wander freely: try not to do any repetitive task like counting or replaying a song.", 
                "If at any time you notice that your mind hasn't been wandering as instructed, press the '%c' key with your left index finger."%params['wanderKey'].upper(),
                "Sometimes during the lecture, a question about your attention may appear. When this happens, answer the question within a few seconds using the number keys.",
                "Just before and after the lecture, a cross will appear. Look directly at the cross while it's on the screen."]
                
        elif promptType == 'Wander':
            # prompts for LOW ATTENTION:    
            topPrompts = ["You are about to watch a video of an academic lecture. Try to ignore it and think about something else.",
                "This is the LOW ATTENTION RUN: it's extremely important that you do NOT focus on the lecture during this run.",
                "Stay awake and keep your eyes open, but let your mind wander freely: try not to do any repetitive task like counting or replaying a song.", 
                "When the lecture is over, you'll be asked a few questions about it. Answer the questions using the number keys.", 
                "If at any time you notice that your mind hasn't been wandering as instructed, press the '%c' key with your left index finger."%params['wanderKey'].upper(),
#                "Sometimes during the lecture, a question about your attention may appear. When this happens, answer the question within a few seconds using the number keys.",
                "Just before and after the lecture, a cross will appear. Look directly at the cross while it's on the screen."]
        
        elif promptType == 'Attend':
            # prompts for HIGH ATTENTION
            topPrompts = ["You are about to watch a video of an academic lecture. Try to absorb as much of the material as you can.",
                "This is the HIGH ATTENTION RUN: it's extremely important that you pay close attention to the lecture during this run.",
                "When the lecture is over, you'll be asked a few questions about it. Answer the questions using the number keys.", 
                "If at any time you notice that your mind has been wandering, press the '%c' key with your left index finger."%params['wanderKey'].upper(),
#                "Sometimes during the lecture, a question about your attention may appear. When this happens, answer the question within a few seconds using the number keys.",
                "Just before and after the lecture, a cross will appear. Look directly at the cross while it's on the screen."]
        else:
            raise Exception('Prompt Type %s not recognized!'%promptType)
            
        # declare bottom prompts
        bottomPrompts = ["Press any key to continue."]*len(topPrompts) # initialize
        bottomPrompts[-1] = "WHEN YOU'RE READY TO BEGIN, press any key."
            
    elif experiment == 'VidLecTask_vigilance.py':
        if promptType == 'Default':
            # declare default list of prompts
            topPrompts = ["You are about to watch a video of an academic lecture. Keep your eyes open and try to absorb as much of the material as you can.",
                "When the lecture is over, you'll be asked a few questions about it. Answer the questions using the number keys.", 
                "During the lecture, a %s dot will display in the middle of the screen. Look at the dot for the duration of the lecture. When the dot turns %s, press the %c key with your right index finger."%(params['dotColor'],params['targetColor'],params['respKey'].upper()),
#                "If at any time you notice that your mind has been wandering, press the '%c' key with your left index finger."%params['wanderKey'].upper(),
#                "Sometimes during the lecture, a question about your attention may appear. When this happens, answer the question within a few seconds using the number keys.",
                "Just before and after the lecture, a cross will appear. Look directly at the cross while it's on the screen."]
        else:
            raise Exception('Prompt Type %s not recognized!'%promptType)
            
        # declare bottom prompts
        bottomPrompts = ["Press any key to continue."]*len(topPrompts) # initialize
        bottomPrompts[-1] = "WHEN YOU'RE READY TO BEGIN, press any key."
        
        
    elif experiment.startswith('ReadingTask_dict') or experiment.startswith('ReadingImageTask_eyelink') or experiment.startswith('DistractionTask'):
        if promptType == 'Test':
            # declare default list of prompts
            topPrompts = ["You are about to read the transcript of an academic lecture. Try to absorb as much of the material as you can.",
                "Press the '%s' key to advance to the next page. If you don't advance within %.1f seconds, it will advance automatically. If the text starts to fade, that time is almost up."%(params['pageKey'].upper(),params['maxPageTime']), 
                "When the reading is over, you'll be asked a few questions about it. Answer the questions using the number keys.", 
#                "If at any time you notice that your mind has been wandering, press the '%c' key with your left index finger."%params['wanderKey'].upper(),
#                "Sometimes during the reading, a question about your attention may appear. When this happens, answer the question within a few seconds using the number keys.",
                "Between pages, a cross will appear. Look directly at the cross while it's on the screen."]
        elif promptType == 'Read':
            topPrompts = ["You are about to read the transcript of an academic lecture. Try to absorb as much of the material as you can.",
                "When the session is over, you'll be asked a few questions about the material.", 
#                "You will have %.1f seconds to read each page. When the text starts to fade, that time is almost up."%(params['maxPageTime']), 
                "Press the '%s' key to advance to the next page. If you don't advance within %.1f seconds, it will advance automatically. If the text starts to fade, that time is almost up."%(params['pageKey'].upper(),params['maxPageTime']), 
#                "If at any time you notice that your mind has been wandering, press the '%c' key with your left index finger."%params['wanderKey'].upper(),
#                "Sometimes during the reading, a question about your attention may appear. When this happens, answer the question within a few seconds using the number keys.",
                "Between pages, a cross will appear. Look directly at the cross while it's on the screen."]
        elif promptType == 'AttendReading':
            topPrompts = ["You are about to read the transcript of an academic lecture. At the same time, you will hear audio from a different lecture.",
                "When the session is over, you'll be asked a few questions about the reading. Questions about the audio will happen at the end of all the sessions.",
#                "You will have %.1f seconds to read each page. When the text starts to fade, that time is almost up."%(params['maxPageTime']), 
                "Press the '%s' key to advance to the next page. If you don't advance within %.1f seconds, it will advance automatically. If the text starts to fade, that time is almost up."%(params['pageKey'].upper(),params['maxPageTime']), 
#                "If at any time you notice that your mind has been wandering, press the '%c' key with your left index finger."%params['wanderKey'].upper(),
#                "Sometimes during the reading, a question about your attention may appear. When this happens, answer the question using the number keys.",
                "Between pages, a cross will appear. Look directly at the cross while it's on the screen.",
                "In this session, pay attention to ONLY the reading and IGNORE the audio."]
        elif promptType == 'AttendReading_short':
            topPrompts = ["In this session, pay attention to ONLY the reading and IGNORE the audio."]
        elif promptType == 'AttendBoth':
            topPrompts = ["You are about to read the transcript of an academic lecture. At the same time, you will hear audio from a different lecture.",
                "When the session is over, you'll be asked a few questions about the reading. Questions about the audio will happen at the end of all the sessions.", 
#                "You will have %.1f seconds to read each page. When the text starts to fade, that time is almost up."%(params['maxPageTime']), 
                "Press the '%s' key to advance to the next page. If you don't advance within %.1f seconds, it will advance automatically. If the text starts to fade, that time is almost up."%(params['pageKey'].upper(),params['maxPageTime']), 
#                "If at any time you notice that your mind has been wandering, press the '%c' key with your left index finger."%params['wanderKey'].upper(),
#                "Sometimes during the reading, a question about your attention may appear. When this happens, answer the question using the number keys.",
                "Between pages, a cross will appear. Look directly at the cross while it's on the screen.",
                "In this session, pay attention to BOTH the reading AND the audio."]
        elif promptType == 'AttendBoth_short':
            topPrompts = ["In this session, pay attention to BOTH the reading AND the audio."]
        elif promptType == 'AttendLeft':
            topPrompts = ["You are about to read the transcript of an academic lecture. At the same time, you will sometimes hear audio from a different lecture.",
                "On some trials, a lecture will play in only your left ear. On other trials, a DIFFERENT lecture will play in only your right ear.",
                "Only the reading and the LEFT ear lecture are important. When the audio is in your LEFT ear, try to absorb as much of BOTH the reading AND audio material as you can.", 
                "When the audio is in your RIGHT ear, IGNORE the audio and just absorb the reading.",
                "When the session is over, you'll be asked a few questions about the reading. Questions about the audio will happen at the end of all the sessions.", 
#                "You will have %.1f seconds to read each page. When the text starts to fade, that time is almost up."%(params['maxPageTime']), 
                "Press the '%s' key to advance to the next page. If you don't advance within %.1f seconds, it will advance automatically. If the text starts to fade, that time is almost up."%(params['pageKey'].upper(),params['maxPageTime']), 
#                "If at any time you notice that your mind has been wandering, press the '%c' key with your left index finger."%params['wanderKey'].upper(),
#                "Sometimes during the reading, a question about your attention may appear. When this happens, answer the question using the number keys.",
                "Between pages, a cross will appear. Look directly at the cross while it's on the screen."]
        elif promptType == 'AttendRight':
            topPrompts = ["You are about to read the transcript of an academic lecture. At the same time, you will sometimes hear audio from a different lecture.",
                "On some trials, a lecture will play in only your right ear. On other trials, a DIFFERENT lecture will play in only your left ear.",
                "Only the reading and the RIGHT ear lecture are important. When the audio is in your RIGHT ear, try to absorb as much of BOTH the reading AND audio material as you can.",
                "When the audio is in your LEFT ear, IGNORE the audio and just absorb the reading.",
                "When the session is over, you'll be asked a few questions about the reading. Questions about the audio will happen at the end of all the sessions.", 
#                "You will have %.1f seconds to read each page. When the text starts to fade, that time is almost up."%(params['maxPageTime']), 
                "Press the '%s' key to advance to the next page. If you don't advance within %.1f seconds, it will advance automatically. If the text starts to fade, that time is almost up."%(params['pageKey'].upper(),params['maxPageTime']), 
#                "If at any time you notice that your mind has been wandering, press the '%c' key with your left index finger."%params['wanderKey'].upper(),
#                "Sometimes during the reading, a question about your attention may appear. When this happens, answer the question using the number keys.",
                "Between pages, a cross will appear. Look directly at the cross while it's on the screen."]
        elif promptType == 'AttendForward':
            topPrompts = ["You are about to read the transcript of an academic lecture. At the same time, you will sometimes hear audio from a different lecture.",
                "On some trials, a lecture will play forward. On other trials, the lecture will play backward.",
                "Only the reading and the forward lecture are important. When the audio playing FORWARD, try to absorb as much of BOTH the reading AND audio material as you can.",
                "When the audio is playing BACKWARD, IGNORE the audio and just absorb the reading.",
                "When the session is over, you'll be asked a few questions about the reading. Questions about the audio will happen at the end of all the sessions.", 
#                "You will have %.1f seconds to read each page. When the text starts to fade, that time is almost up."%(params['maxPageTime']), 
                "Press the '%s' key to advance to the next page. If you don't advance within %.1f seconds, it will advance automatically. If the text starts to fade, that time is almost up."%(params['pageKey'].upper(),params['maxPageTime']), 
#                "If at any time you notice that your mind has been wandering, press the '%c' key with your left index finger."%params['wanderKey'].upper(),
#                "Sometimes during the reading, a question about your attention may appear. When this happens, answer the question using the number keys.",
                "Between pages, a cross will appear. Look directly at the cross while it's on the screen."]
        elif promptType == 'TestReading':
            topPrompts = ["You will now be asked a few questions about the text you just read. Answer using the number keys.",
                "There's no time limit on each question, but try to answer in a reasonable amount of time.",
                "If you don't know the answer, take your best guess."]
        elif promptType == 'TestReading_box':
            topPrompts = ["You will now be asked a few questions about the text you just read. Answer using the button box.",
                "There's no time limit on each question, but try to answer in a reasonable amount of time.",
                "If you don't know the answer, take your best guess."]
        elif promptType == 'TestBoth':
            topPrompts = ["You will now be asked a few questions about the lectures you just read and heard. Answer using the number keys.",
                "Some questions may be on material you were asked to ignore. Please try to answer anyway. If you don't know the answer, take your best guess.",
                "There's no time limit on each question, but try to answer in a reasonable amount of time."]
        elif promptType == 'Practice':
            topPrompts = ["You are about to read the transcript of an academic lecture. Try to absorb as much of the material as you can.",
                "Press the '%s' key to advance to the next page. If you don't advance within %.1f seconds, it will advance automatically. If the text starts to fade, that time is almost up."%(params['pageKey'].upper(),params['maxPageTime']), 
                "This session is just practice. Try to read at your natural speed.", 
                "Between pages, a cross will appear. Look directly at the cross while it's on the screen."]
        elif promptType == 'None':
            topPrompts = []
        else:
            raise Exception('Prompt Type %s not recognized!'%promptType)
                
        # declare bottom prompts
        if promptType == 'None':
            bottomPrompts = []
        else:
            bottomPrompts = ["Press any key to continue."]*len(topPrompts) # initialize
            bottomPrompts[-1] = "WHEN YOU'RE READY TO BEGIN, press any key."
        
    elif experiment.startswith('ReadingTask_questions'):
        if promptType == 'Test':
            # declare default list of prompts
            topPrompts = ["You will now be asked a few questions about the text you just read. Answer using the number keys.",
                "There's no time limit on each question, but try to answer in a reasonable amount of time.",
                "If you don't know the answer, take your best guess."]
        elif promptType == 'TestBoth':
            # declare prompts for questions on both reading and audio.
            topPrompts = ["You will now be asked a few questions about the lectures you just read and heard. Answer using the number keys.",
                "Some questions may be on material you were asked to ignore. Please try to answer anyway. If you don't know the answer, take your best guess.",
                "There's no time limit on each question, but try to answer in a reasonable amount of time."]
        elif promptType == 'TestSound':
            # declare prompts for questions on audio.
            topPrompts = ["You will now be asked a few questions about the lecture you just heard. Answer using the number keys.",
                "Some questions may be on material you didn't hear or were asked to ignore. Please try to answer anyway. If you don't know the answer, take your best guess.",
                "There's no time limit on each question, but try to answer in a reasonable amount of time."]
        elif promptType == 'TestSound_box':
            # declare prompts for questions on audio.
            topPrompts = ["You will now be asked a few questions about the lecture you just heard. Answer using the button box.",
                "Some questions may be on material you didn't hear or were asked to ignore. Please try to answer anyway. If you don't know the answer, take your best guess.",
                "There's no time limit on each question, but try to answer in a reasonable amount of time."]            
        else:
            raise Exception('Prompt Type %s not recognized!'%promptType)
                
        # declare bottom prompts
        bottomPrompts = ["Press any key to continue."]*len(topPrompts) # initialize
        bottomPrompts[-1] = "WHEN YOU'RE READY TO BEGIN, press any key."
        
    else:
        raise Exception('Experiment %s not recognized!'%experiment)    
    
    # return the prompts
    return (topPrompts,bottomPrompts)
