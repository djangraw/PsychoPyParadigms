#!/usr/bin/env python2
"""Wrapper for RatingScale objects.."""
# RatingScales.py
#
# Created 7/19/18 by DJ based on PromptTools.py
# Updated 8/16/18 by DJ - textColor input
# Updated 8/22/18 by DJ - added pos and stepSize inputs to ShowVAS
# Updated 8/28/18 by DJ - added hideMouse and repeatDelay inputs to ShowVAS

from psychopy import core, event, logging#, visual # visual and gui conflict, so don't import it here
import time
import string

def ShowVAS(questions_list,options_list, win,name='Question', questionDur=float('inf'), isEndedByKeypress=True, upKey='up', downKey='down', selectKey='enter',textColor='black',pos=(0.,0.),stepSize=1.,hideMouse=True,repeatDelay=0.5):
    # make visuals
    from psychopy import visual
    import numpy as np
    from pyglet.window import key
    
    # set up
    nQuestions = len(questions_list)
    rating = [None]*nQuestions
    decisionTime = [None]*nQuestions
    choiceHistory = [[0]]*nQuestions
    # Set up pyglet key handler
    keyState=key.KeyStateHandler()
    win.winHandle.push_handlers(keyState)
    # Get attributes for key handler (put _ in front of numbers)
    if downKey[0].isdigit():
        downKey_attr = '_%s'%downKey        
    else:
        downKey_attr = downKey
    if upKey[0].isdigit():
        upKey_attr = '_%s'%upKey
    else:
        upKey_attr = upKey
        
    # Rating Scale Loop
    for iQ in range(nQuestions):
        tickLocs = np.linspace(0,100,len(options_list[iQ])).tolist()
        tickWidth = (tickLocs[1]-tickLocs[0])*0.9/100 # *.9 for extra space, /100 for norm units
        ratingScale = visual.RatingScale(win, scale=questions_list[iQ], \
            low=0., high=100., markerStart=50., precision=1., labels=options_list[iQ], tickMarks=tickLocs, tickHeight=0.0, \
            marker='triangle', markerColor=textColor, markerExpansion=1, singleClick=False, disappear=False, \
            textSize=0.8, textColor=textColor, textFont='Helvetica Bold', showValue=False, \
            showAccept=False, acceptKeys=selectKey, acceptPreText='key, click', acceptText='accept?', acceptSize=1.0, \
            leftKeys=downKey, rightKeys=upKey, respKeys=(), lineColor=textColor, skipKeys=['q','escape'], \
            mouseOnly=False, noMouse=hideMouse, size=2.0, stretch=1.0, pos=pos, minTime=0.4, maxTime=questionDur, \
            flipVert=False, depth=0, name='%s%d'%(name,iQ), autoLog=True)
        # Fix text wrapWidth
        for iLabel in range(len(ratingScale.labels)):
            ratingScale.labels[iLabel].wrapWidth = tickWidth
            ratingScale.labels[iLabel].alignHoriz = 'center'
            
        # Display until time runs out (or key is pressed, if specified)
        win.logOnFlip(level=logging.EXP, msg='Display %s%d'%(name,iQ))
        tStart = time.time()
        while (time.time()-tStart)<questionDur:
            # Look for keypresses
            if keyState[getattr(key,downKey_attr)]: #returns True if left key is pressed
                tPress = time.time()
                valPress = ratingScale.markerPlacedAt
                keyPressed = downKey_attr
                step = -stepSize
            elif keyState[getattr(key,upKey_attr)]: #returns True if the right key is pressed
                tPress = time.time()
                valPress = ratingScale.markerPlacedAt
                keyPressed = upKey_attr
                step = stepSize
            else:
                keyPressed = None
            
            # Handle sliding for held keys
            while (keyPressed is not None) and ((time.time()-tStart)<questionDur):
                # update time
                durPress = time.time()-tPress
                # update display
                ratingScale.draw()
                win.flip()
                # check for key release
                if keyState[getattr(key,keyPressed)]==False:
                    break
                # Update marker
                if durPress>repeatDelay:
                    ratingScale.markerPlacedAt = valPress + (durPress-repeatDelay)*step*60 # *60 for refresh rate
                    ratingScale.markerPlacedAt = max(ratingScale.markerPlacedAt,ratingScale.low)
                    ratingScale.markerPlacedAt = min(ratingScale.markerPlacedAt,ratingScale.high)
            # Check for response
            if isEndedByKeypress and not ratingScale.noResponse:
                break
            # Redraw
            ratingScale.draw()
            win.flip()
            
        # Log outputs
        rating[iQ] = ratingScale.getRating()
        decisionTime[iQ] = ratingScale.getRT()
        choiceHistory[iQ] = ratingScale.getHistory()
    
    return rating,decisionTime,choiceHistory

