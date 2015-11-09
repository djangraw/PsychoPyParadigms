#!/usr/bin/env python2
"""Display a video lecture with interspersed thought probes.
Then ask the subject comprehension questions at the end."""
# PrintPickle.py
# Created 2/7/15 by DJ based on VidLecTask_dict.py

# declare packages
from psychopy import core, gui
from psychopy.tools.filetools import fromFile#, toFile
import os


# Print a loaded dictionary in a format that could be used to recreate it in a script
def PrintDict(dict, dictName='pickle'):
    # print header
    print '%s = {'%dictName
    # print keys
    for key in sorted(dict.keys()):
        if isinstance(dict[key], basestring): # if it's a string...
            print "   '%s': '%s'"%(key,dict[key]) # put quotes around the value
        else: # if it's not a string
            print "   '%s': %s"%(key,dict[key]) # print the value as-is
    print '}'


# ===================== #
# === MAIN FUNCTION === #
# ===================== #

# get pickle filename
dlgResult = gui.fileOpenDlg(prompt='Select parameters file',tryFilePath=os.getcwd(),
        allowed="PICKLE files (.pickle)|.pickle|All files (.*)|")

# load and print pickle file
if dlgResult is not None: # if they didn't hit cancel
    filename = dlgResult[0] # extract just the filename
    pickle = fromFile(filename) # load it
    print '=== Data extracted from %s: ==='%filename
    PrintDict(pickle)
    