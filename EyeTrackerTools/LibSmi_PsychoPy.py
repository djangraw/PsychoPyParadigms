#!/usr/bin/env python2
"""
LibSmi_PsychoPy.py
Handles the display, sound, and logic for running calibration and tracking with the SMI tracker.
Communicates with the tracker via serial port.

===ORIGINAL CODE (LibSmi.py) INCLUDED THIS TEXT ====
This file is part of OpenSesame.

OpenSesame is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

OpenSesame is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with OpenSesame.  If not, see <http://www.gnu.org/licenses/>.
"""
# Created 8/19/15 by DJ from libsmi.py (https://github.com/smathot/libsmi)
#   Added psychopy commands, validate, text, MaxReadTime and abort keys, pause and continue recording
# Updated 8/20/15 by DJ - debugged, fixed PsychoPy/SMI coordinate mismatch, tested with SMI comp connection
# Updated 8/26/15 by DJ - added run_calibration function
# Updated 11/5/15 by DJ - added nr_of_pts input to run_calibration function
# Updated 11/11/15 by DJ - added additional calibration parameters to calibration and run_calibration functions

import os.path
import time
import serial
from psychopy import visual, sound, event, core
"""
from libopensesame import exceptions
from openexp.canvas import canvas
from openexp.keyboard import keyboard
from openexp.synth import synth
"""

class LibSmi_PsychoPy:

    """
    Provides simplified communication with the SMI Red Eye tracker through the
    serial port. Originally for use with the OpenSesame experiment builder - now adapted to PsychoPy.
    
    Tested with:
    SMI MRI-SV eye tracker
    PC 1 running iViewX (Windows XP)
    PC 2 running PsychoPy 1.82.01 (Mac OSX 10.9.5)   
    """
    
    version = 0.10

    def __init__(self, experiment, port='COM1', baudrate=115200, useSound=True, w=1024, h=768, bgcolor=(255,255,255), fgcolor=(0,0,0), fullScreen=True, screenToShow=0):
    
        """<DOC>
        Initializes the SMI tracker class
        
        Keyword arguments:
        experiment: the name of the experiment (this used to be an OpenSesame struct.)
        port -- the name of the serial port to which the tracker is attached (default = 'COM1')
        baudrate -- the baudrate of the serial port communications (default = 115200)
        useSound -- indicates if sounds should be played to inidicate success or failure
        w,h -- the width and height, in pixels, of the desired window.
        bgcolor -- background (rgb255) of 
        </DOC>"""
        
        # set parameters
        outsz = 10
        insz = 4
        
        self.experiment = experiment # for filename later
        self.tracker = serial.Serial(port=port, baudrate=baudrate, bytesize=serial.EIGHTBITS, stopbits=serial.STOPBITS_ONE, parity=serial.PARITY_NONE, timeout=0.5)      
        # initialize window
        self.win = visual.Window((w,h), fullscr=fullScreen, allowGUI=False, screen=screenToShow, units='pix', name='win', color=bgcolor, colorSpace='rgb255')
        self.win.flip(clearBuffer=True)
        # initialize dot
        self.outercircle = visual.Circle(self.win,pos=(0,0), radius=outsz, fillColor=fgcolor, fillColorSpace='rgb255', lineColor=fgcolor,lineColorSpace='rgb255', units='pix',name='outercircle')
        self.innercircle = visual.Circle(self.win,pos=(0,0), radius=insz, fillColor=bgcolor, fillColorSpace='rgb255', lineColor=bgcolor,lineColorSpace='rgb255', units='pix',name='innercircle')
        # initialize text
        self.text = visual.TextStim(self.win,pos=(0,0), color=fgcolor,colorSpace='rgb255',text="Setting up...")
        self.text.draw()
        self.win.flip()
        # set recording parameters
        self.streaming = False
        # initialize sounds
        self.useSound = useSound
        if self.useSound:
            self.beep1 = sound.Sound(value=220, secs=0.200, volume=0.5)
            self.beep2 = sound.Sound(value=440, secs=0.200, volume=0.5)
        # create clock (for debugging)
        self.clock = core.Clock()
        # make sure recording is stopped
        self.stop_recording()
        
    def send(self, msg, sleep=10):
    
        """<DOC>
        Send a message to the tracker
        
        Arguments:
        msg -- a string containing the message
        
        Keyword arguments:
        sleep -- a value in milliseconds to sleep after the command has been
                 sent to avoid overflowing (default=10)
        </DOC>"""
        
        # The message needs to be end with a tab-linefeed
        nBytes = self.tracker.write('%s\t\n' % msg)
        core.wait(0.001*sleep)
        print("sent %d bytes: %s"%(nBytes,msg))
        
    def recv(self, MaxReadTime=float('inf')):
    
        """<DOC>
        Receive a message from the tracker
        
        Returns:
        A message (the tab-linefeed is stripped off)
        </DOC>"""
        
        # Keep track of read start time
        startReadTime = self.clock.getTime()
        # Receive a line from the tracker
        s = ''
        while True:
            c = self.tracker.read(size=1)      
            if c == None:
                raise exceptions.runtime_error('The tracker said "%s"' % s)
            if c == '\n':
                if len(s) > 1:
                    break
                else:
                    s = ''
                    continue
            s += c
            # check for escape keys
            key = event.getKeys()
            if (len(key) > 0 and key[0] in ['q','Escape']):
                s = 'ABORT\n'
                break
            if (self.clock.getTime()-startReadTime > MaxReadTime):
                s += '\n'
                break
        print('received %s'%s)
        return s[:-1] # Strip off the tab and return
                
    def calibrate(self, nr_of_pts=9, auto_accept=True, go_fast=False, calib_level=2):
        
        """<DOC>
        Performs calibration procedure
        
        Keyword arguments:
        nr_of_pts: The number of points to be used for the validation (default=9)
        auto_accept: Let SMI pick when to accept a point (True [default]) or accept manually (False).
        go_fast: Go quickly from point to point (True) or slower and more precise (False [default]).
        calib_level: calibration check level (0=none,1=weak,2=medium [default],3=strong)
                
        Exceptions:
        Throws a runtime_error if the calibration fails        
        </DOC>"""
        
        # inform user
        self.text.text = 'Performing %d-point calibration.'%(nr_of_pts)
        self.text.draw()
        self.win.flip()
                
        # get screen size
        w = self.win.size[0]
        h = self.win.size[1]
        
        # set calibration parameters
        # ET_CPA [command] [enable]
        self.send('ET_CPA 0 1') # Enable wait for valid data
        self.send('ET_CPA 1 1') # Enable randomize point order
        if auto_accept:
            self.send('ET_CPA 2 1') # Ensable auto accept
        else:
            self.send('ET_CPA 2 0') # Disable auto accept
        if go_fast:
            self.send('ET_CPA 3 1') # Set speed to fast
        else:
            self.send('ET_CPA 3 0') # Set speed to slow
        # ET_LEV [calibration level]
        self.send('ET_LEV %d'%calib_level) # Set calibration check level to medium
        # ET_CSZ [xres] [yres]
        self.send('ET_CSZ %d %d' % (w, h)) # Set the screen resolution
        
        # Start the calibration with default calibration points
        self.send('ET_DEF')
        self.send('ET_CAL %d' % nr_of_pts)
        pts = {}
        while True:
            
            # Poll the keyboard to capture escape pressed
            key = event.getKeys()
            if len(key) > 0 and key[0] in ['q','Escape']:
                self.text.text = 'Calibration aborted.'
                self.text.draw()
                self.win.flip()
                break
            
            # Receive a line from the tracker
            s = self.recv()
            # check for abort command
            if s == 'ABORT':
                self.text.text = 'Calibration aborted.'
                self.text.draw()
                break
            # split line
            cmd = s.split()
            
            # Ignore empty commands    
            if len(cmd) == 0:
                continue
            
            # Change the coordinates of the calibration points
            if cmd[0] == 'ET_PNT':
                pt_nr = int(cmd[1])
                x = int(cmd[2])
                y = int(cmd[3])
                pts[pt_nr-1] = x, y
            
            # Indicates that the calibration point has been changed
            elif cmd[0] == 'ET_CHG':                
                pt_nr = int(cmd[1])
                if pt_nr-1 not in pts:
                    raise exceptions.runtime_error('Something went wrong during the calibration. Please try again.')
                x, y = pts[pt_nr-1]
                # Redraw dot and refresh window
                self.innercircle.pos = (x-0.5*w,0.5*h-y) # SMI considers (0,0) to be top left
                self.outercircle.pos = (x-0.5*w,0.5*h-y) # SMI considers (0,0) to be top left
                self.outercircle.draw()
                self.innercircle.draw()
                self.win.flip()
                
                if self.useSound:
                    self.beep1.play()
            
            # Indicates that the calibration was successful
            elif cmd[0] == 'ET_FIN':
                # Display results
                self.text.text = 'Calibration complete!'
                self.text.draw()
                break
        
        # Initially recording is off
        self.stop_recording()
        
        if self.useSound:
            self.beep2.play()
            
        # refresh screen
        self.win.flip()
        
        
    def validate(self): # ADDED 8/19/15 by DJ!
        
        """<DOC>
        Performs calibration procedure
        
        Keyword arguments:
        The number of points to be used for the validation (default=9)
                
        Exceptions:
        Throws a runtime_error if the calibration fails        
        </DOC>"""
        
        # inform user
        self.text.text = 'Running validation.'
        self.text.draw()
        self.win.flip()
        
        # get screen size
        w = self.win.size[0]
        h = self.win.size[1]
        
        # ET_CPA [command] [enable]
        self.send('ET_VLS') # Start validation and get results
        
        pts = {}
        while True:
            
            # Poll the keyboard to capture escape pressed
            key = event.getKeys()
            if len(key) > 0 and key[0] in ['q','Escape']:
                self.text.text = 'Validation aborted.'
                self.text.draw()
                break
            
            # Receive a line from the tracker
            s = self.recv()
            # check for abort command
            if s == 'ABORT':
                self.text.text = 'Validation aborted.'
                self.text.draw()
                break
            # split line
            cmd = s.split()
            
            # Ignore empty commands    
            if len(cmd) == 0:
                continue
            
            # Change the coordinates of the calibration points
            if cmd[0] == 'ET_PNT':
                pt_nr = int(cmd[1])
                x = int(cmd[2])
                y = int(cmd[3])
                pts[pt_nr-1] = x, y
            
            # Indicates that the calibration point has been changed
            elif cmd[0] == 'ET_CHG':                
                pt_nr = int(cmd[1])
                if pt_nr-1 not in pts:
                    raise exceptions.runtime_error('Something went wrong during the calibration. Please try again.')
                x, y = pts[pt_nr-1]
                # Redraw dot and refresh window
                self.innercircle.pos = (x-0.5*w,0.5*h-y) # SMI considers (0,0) to be top left
                self.outercircle.pos = (x-0.5*w,0.5*h-y) # SMI considers (0,0) to be top left
                self.outercircle.draw()
                self.innercircle.draw()
                self.win.flip()
                
                if self.useSound:
                    self.beep1.play()
            
            # Indicates that the validation was successful
            elif cmd[0] == 'ET_VLS':
                eye = cmd[1]
                x = float(cmd[2])
                y = float(cmd[3])
                d = float(cmd[4])
                xd = float(cmd[5][:-1])
                yd = float(cmd[6][:-1])
                # draw results on screen
                self.text.text = 'Validation results:\nx = %f, y = %f, d = %f, xd = %f, yd = %f'%(x,y,d,xd,yd)
                self.text.draw()
                break
        
        # Initially recording is off
        self.stop_recording()
        
        if self.useSound:
            self.beep2.play()
            
        # refresh screen
        self.win.flip()
        
        
    def run_calibration(self, nr_of_pts=9, auto_accept=True, go_fast=False, calib_level=2): # ADDED 8/27/15 BY DJ
        
        """<DOC>
        Allows user to select calibration, validation, or proceed to experiment using a keypress.
        
        Keyword arguments:
        nr_of_pts: The number of points to be used for the validation (default=9)
        auto_accept: Let SMI pick when to accept a point (True [default]) or accept manually (False).
        go_fast: Go quickly from point to point (True) or slower and more precise (False [default]).
        calib_level: calibration check level (0=none,1=weak,2=medium [default],3=strong)
        Calls calibrate, validate.
        
        </DOC>"""
        
        # Display instructions
        instructionStr = "Press c to calibrate, v to validate, and q to exit setup."
        # print instructions
        self.text.text=instructionStr
        self.text.draw()
        self.win.flip()
        # Run calibration and validation
        isDone = False
        while not isDone:
            
            # Calibrate
            key = event.getKeys()
            if len(key)==0:
                continue
            elif key[0] == 'c':
                # Calibrate
                print("start calibration: %.3f sec"%self.clock.getTime())
                self.calibrate(nr_of_pts=nr_of_pts, auto_accept=auto_accept, go_fast=go_fast, calib_level=calib_level)
            elif key[0] == 'v':
                # Validate calibration
                print("start validation: %.3f sec"%self.clock.getTime())
                self.validate()
            elif key[0] in ['q','escape']:
                print("quit setup: %.3f sec"%self.clock.getTime())
                isDone = True
            else: 
                # print instructions
                self.text.text=instructionStr
                self.text.draw()
                self.win.flip()
                print("pressed %s: %.3f sec"%(key[0], self.clock.getTime()))
        
        
    def save_data(self, path=None):
        
        """<DOC>
        Save the SMI datafile to disk
        
        Keyword arguments:
        path -- the name of the datafile or None for a default name (default=None)        
        </DOC>"""
        
        if path == None:
#            path = os.path.splitext(os.path.basename(self.experiment.logfile))[0] + time.strftime('_%m_%d_%Y_%H_%M') + '.idf'
            path = self.experiment + time.strftime('_%m_%d_%Y_%H_%M') + '.idf'
        self.send('ET_SAV "%s"' % path)
                
    def start_recording(self, stream=True):
        
        """<DOC>
        Start recording
        
        Keyword arguments:
        stream -- determines if samples should be streamed so they can be
                  accessed using the sample() function
        </DOC>"""
        
        # Clear the tracker buffer and start recording
        #self.send('ET_CLR')
        self.send('ET_REC')
        
        if stream:
            self.streaming = True
            self.send('ET_FRM "%SX %SY"')
            self.send('ET_STR')
        else:
            self.streaming = False
            
    def pause_recording(self):
        
        """<DOC>
        Pause recording
        </DOC>"""
        self.send('ET_PSE')
        
    def continue_recording(self, text=""):
        
        """<DOC>
        Continue recording after pause.
        </DOC>"""
        if text=="":
            self.send('ET_CNT')
        else:
            self.send('ET_CNT %s'%text)
        
    def stop_recording(self):
        
        """<DOC>
        Stop recording
        </DOC>"""
        
        if self.streaming:
            self.send('ET_EST')
        self.send('ET_STP')
        self.streaming = False
        
    def clear(self):
        
        """<DOC>
        Clear the input buffer
        </DOC>"""
        
        self.tracker.flushInput()
        
    def sample(self, clear=False):
        
        """<DOC>
        Retrieve the current gaze position from the tracker. If binocular
        recording is enabled, return the left eye.
        
        Keyword arguments:
        clear -- indicates if the input buffer should be flushed so that an
                 up-to-date sample is returned (default=False)
        
        Returns:
        An (x,y) tuple
        </DOC>"""
        
        if not self.streaming:
            raise exceptions.runtime_error("Please set stream=True in start_recording() before using sample()")
            
        if clear:
            self.tracker.flushInput()
        
        while True:
            s = self.recv()
            l = s.split()
            if len(l) > 0 and l[0] == 'ET_SPL':
                try:
                    x = int(l[1])
                    if len(l) == 5:
                        y = int(l[3]) # Binocular
                    else:
                        y = int(l[2]) # One eye
                    break
                except:
                    pass
                
        return x, y
        
    def log(self, msg):
        
        """<DOC>
        Write message (or remark) to the SMI logfile
        
        Arguments:
        msg -- a string containing the message
        </DOC>"""
        
        self.send('ET_REM "%s"' % msg)
        
    def cleanup(self):
        
        """Neatly close the tracker"""
        
        self.tracker.close()
        
        
def prepare(item):
    
    """
    Initialize the tracker
    
    Arguments:
    item -- the external_script item that has called the script
    """
    
    item.tracker = LibSmi_PsychoPy(item.experiment)
#    item.experiment.tracker = libsmi(item.experiment)
#    item.experiment.cleanup_functions.append(item.experiment.tracker.cleanup)


def run(item):
    
    """
    Not used in this case
    
    Arguments:
    item -- the external_script item that has called the script
    """
    
    pass