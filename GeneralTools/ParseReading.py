#!/usr/bin/env python2
"""Display a video lecture with interspersed thought probes.
Then ask the subject comprehension questions at the end."""
# ReadingTask.py
# Created 3/16/15 by DJ based on VidLecTask.py
# Updated 1/24/17 by DJ - debugged (removed visual import)
# Updated 12/17/18 by DJ - removed import PromptTools

from psychopy import core, gui, data, event, sound, logging, visual # visual causes a bug in the guis, so we may want to move it down.
from psychopy.tools.filetools import fromFile, toFile
import time, numpy as np
import AppKit, os # for monitor size detection, files

#linesPerPage = 7
#lineSpacing = 2
#topLinePos = (linesPerPage-1)/2*lineSpacing
#textFont = 'Courier'
#textWidth = 30
screenRes = [1200,700]


longText = "I'm going to talk to you today about the beginnings of the Greek experience as far as we know it, and I should warn you at once that the further back in history you go the less secure is your knowledge, especially at the beginning of our talk today when you are in a truly prehistoric period. That is before there is any written evidence from the period in which you are interested. So what we think we know derives chiefly from archeological evidence, which is before writing - mute evidence that has to be interpreted and is very complicated, and is far from secure. Even a question such as a date which is so critical for historians, is really quite approximate, and subject to controversy, as is just about every single thing I will tell you for the next few days. These will be even more than usual subject to controversy even the most fundamental things. So what you'll be hearing are approximations as best we can make them of what's going on."
#longText = ('a'*50 + ' ' + 'b'*50)

def ParseText(longText, lineLength=50, iLineStart=0, maxLines=100):
    textLength = len(longText)
    lines = []
    while iLineStart < textLength and len(lines) < maxLines:
        iLineEnd = iLineStart+lineLength
        if iLineEnd>textLength:
            thisLine = longText[iLineStart:]
        else:
            thisLine = longText[iLineStart:iLineEnd].rsplit(" ",1)[0]
        iLineStart += len(thisLine)+1
        lines.append(thisLine)
    return(lines)

def GetTextStims(win,linesPerPage=9,lineSpacing=2,textWidth=30,textFont='Courier'):
    topLinePos = (linesPerPage-1)/2*lineSpacing
    messages = []
    for i in range(0,linesPerPage):
        messages.append(visual.TextStim(win, pos=[-textWidth/2,(topLinePos-i*lineSpacing)], wrapWidth=textWidth, font=textFont, color='#000000', alignHoriz='left', name='msg%d'%i, text=""))
    return messages
    
# ====== SET UP STIMULI ===== # 

#win = visual.Window(screenRes, fullscr=0, allowGUI=False, monitor='testMonitor', screen=0, units='deg', name='win')
#messages = GetTextStims(win)
#
# ====== MAIN CODE ===== #
#
#lines = ParseText(longText)
#print(lines)
#linesPerPage = len(messages)
#nPages = int(np.ceil(len(lines)/float(linesPerPage)))
#for iPage in range(0,nPages):
#    for i in range(0,len(messages)):
#        iLine = iPage*linesPerPage+i
#        if iLine<len(lines):
#            messages[i].setText(lines[iLine])
#            messages[i].draw()
#    win.flip()
#    core.wait(2,2)
#    
#
# exit
#core.quit
