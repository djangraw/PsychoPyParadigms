#!/usr/bin/env python2
#
# FetchEyelinkFile.py
# If the EDF file saves but doesn't transfer, you can use this to grab it off the host machine.
#
# Created 5/5/15 by DJ.

from pylink import *


eyelinktracker = EyeLink()
if not eyelinktracker:
    print('=== ERROR: Eyelink() returned None.')
    core.quit()
   
edfHostFileName = 'TEST.EDF'
edfFileName = 'ReadingImage-99-1-Apr_30_1227_TEST.EDF'
getEYELINK().receiveDataFile(edfHostFileName, edfFileName)
getEYELINK().close(); 
print('Success!')