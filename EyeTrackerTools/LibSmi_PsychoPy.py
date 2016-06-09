#!/usr/bin/env python2
"""
LibSmi_PsychoPy.py
Handles the display, sound, and logic for running calibration and tracking with an SMI tracker.
Communicates with the tracker via serial port. 
Adapted from libsmi.py (https://github.com/smathot/libsmi) to use PsychoPy instead of OpenSesame.
Added validation and manual validation options and custom display and calibration options.

Coded by David Jangraw as part of the PsychoPyParadigms GitHub repository (https://github.com/djangraw/PsychoPyParadigms).
See https://github.com/djangraw/PsychoPyParadigms/blob/master/README.md for license information.
"""
# Created 8/19/15 by DJ from libsmi.py (https://github.com/smathot/libsmi)
#   Added psychopy commands, validate, text, MaxReadTime and abort keys, pause and continue recording
# Updated 8/20/15 by DJ - debugged, fixed PsychoPy/SMI coordinate mismatch, tested with SMI comp connection
# Updated 8/26/15 by DJ - added run_calibration function
# Updated 11/5/15 by DJ - added nr_of_pts input to run_calibration function
# Updated 11/11/15 by DJ - added additional calibration parameters to calibration and run_calibration functions
# Updated 11/13/15 by DJ - added validation_manual function
# Updated 11/17/15 by DJ - changed default calibration params to most conservative ones. Updated comments.
# Updated 1/11/16 by DJ - added start_movie and end_movie functions, added save_eye_movie input to calibrate and run_calibration fns
# Updated 1/29/16 by DJ - switched from save_eye_movie to eye_movie_filename and eye_movie_format inputs in claibration functions

# import libraries
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
            self.beep1 = sound.Sound(value=220, secs=0.200, volume=0.1)
            self.beep2 = sound.Sound(value=440, secs=0.200, volume=0.1)
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
                
    def calibrate(self, nr_of_pts=13, auto_accept=False, go_fast=False, calib_level=3, eye_movie_filename=None, eye_movie_format='XMP4'):
        
        """<DOC>
        Performs calibration procedure
        
        Keyword arguments:
        nr_of_pts: The number of points to be used for the validation (default=13)
        auto_accept: Let SMI pick when to accept a point (True) or accept manually on the eye tracker computer (False [default]).
        go_fast: Go quickly from point to point (True) or slower and more precise (False [default]).
        calib_level: calibration check level (0=none,1=weak,2=medium,3=strong [default])
        eye_movie_filename: a string indicating the filename where the output should be saved. None means no movie will be saved. [default: None]
        eye_movie_format: a string indicating what type of file should be saved. Acceptable: ['JPG','BMP','XVID','HUFFYUV','ALPARY','XMP4' [default]]
                
        Exceptions:
        Throws a runtime_error if the calibration fails        
        </DOC>"""
        
        if eye_movie_filename is not None:
            self.start_movie(format=eye_movie_format, filename=eye_movie_filename)
        
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
        
        # set recording status
#        if save_eye_movie:
#            self.send('ET_EQE 1')
#        else:
#            self.send('ET_EQE 0')
        
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
                    # end and save the eye movie
                    if eye_movie_filename is not None:
                        self.end_movie()
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
        
        # end and save the eye movie
        if eye_movie_filename is not None:
            self.end_movie()
        
        # Initially recording is off
        self.stop_recording()
        # play beep
        if self.useSound:
            self.beep2.play()
            
        # refresh screen
        self.win.flip()
        
        
    def validate(self): # ADDED 8/19/15 by DJ!
        
        """<DOC>
        Performs calibration procedure
        
        Keyword arguments:
        None
        
        Exceptions:
        Throws a runtime_error if the validation fails.
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
                    raise exceptions.runtime_error('Something went wrong during the validation. Please try again.')
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
        
    def validate_manual(self,nr_of_pts=13): # ADDED 11/13/15 by DJ!
        
        """<DOC>
        Performs validation procedure manually: use space to move through points, or numbers + wert keys to pick points manually:
        2   7   3
          w   e  
        6   1   8
          r   t  
        4   9   5
        
        Keyword arguments:
        The number of points to be used for the validation (default=13)
                
        Exceptions:
        None
        </DOC>"""
        
        # inform user
        self.text.text = 'Running validation.'
        self.text.draw()
        self.win.flip()
        
        # get screen size
        w = self.win.size[0]
        h = self.win.size[1]
        
        # declare 13 points in SMI coordinates
        pts = [(w*0.5,h*0.5), (w*0.05,h*0.05),(w*0.95,h*0.05), (w*0.05,h*0.95),(w*0.95,h*0.95), (w*0.05,h*0.5), (w*0.5,h*0.05), (w*0.95,h*0.5), (w*0.5,h*0.95), (w*0.275,h*0.275),(w*0.725,h*0.275), (w*0.275,h*0.725),(w*0.725,h*0.725)]
        ptKeys = ['1','2','3','4','5','6','7','8','9','w','e','r','t']
        iKey = -1
        
        while True:
            
            # Poll the keyboard to capture escape pressed
            key = event.getKeys()
            if len(key) > 0 and key[0] in ['q','Escape']:
                self.text.text = 'Validation aborted.'
                self.text.draw()
                break
            elif len(key) > 0 and key[0] == 'space':
                iKey = iKey + 1
                if iKey>=len(pts):
                    iKey=0
                x,y = pts[iKey]
                
                # Redraw dot and refresh window
                self.innercircle.pos = (x-0.5*w,0.5*h-y) # SMI considers (0,0) to be top left
                self.outercircle.pos = (x-0.5*w,0.5*h-y) # SMI considers (0,0) to be top left
                self.outercircle.draw()
                self.innercircle.draw()
                self.win.flip()
                
                if self.useSound:
                    self.beep1.play()
                    
            elif len(key) > 0 and key[0] in ptKeys:
                iKey = ptKeys.index(key[0])
                x,y = pts[iKey]            
                
                # Redraw dot and refresh window
                self.innercircle.pos = (x-0.5*w,0.5*h-y) # SMI considers (0,0) to be top left
                self.outercircle.pos = (x-0.5*w,0.5*h-y) # SMI considers (0,0) to be top left
                self.outercircle.draw()
                self.innercircle.draw()
                self.win.flip()
                
                if self.useSound:
                    self.beep1.play()
        
        if self.useSound:
            self.beep2.play()
            
        # refresh screen
        self.win.flip()
        
        
    def run_calibration(self, nr_of_pts=13, auto_accept=False, go_fast=False, calib_level=3, eye_movie_filename=None, eye_movie_format='XMP4'): # ADDED 8/27/15 BY DJ
        
        """<DOC>
        Allows user to select calibration, validation, or proceed to experiment using a keypress.
        
        Keyword arguments:
        nr_of_pts: The number of points to be used for the validation (default=13)
        auto_accept: Let SMI pick when to accept a point (True) or accept manually on the eye tracker computer (False [default]).
        go_fast: Go quickly from point to point (True) or slower and more precise (False [default]).
        calib_level: calibration check level (0=none,1=weak,2=medium,3=strong [default])
        eye_movie_filename: a string indicating the filename where the output should be saved. None means no movie will be saved. [default: None]
        eye_movie_format: a string indicating what type of file should be saved. Acceptable: ['JPG','BMP','XVID','HUFFYUV','ALPARY','XMP4' [default]]
        Calls calibrate, validate.
        
        </DOC>"""
        
        # Display instructions
        instructionStr = "Press c to calibrate, v to validate, m for manual check, and q to exit setup."
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
                self.calibrate(nr_of_pts=nr_of_pts, auto_accept=auto_accept, go_fast=go_fast, calib_level=calib_level,eye_movie_filename=eye_movie_filename,eye_movie_format=eye_movie_format)
            elif key[0] == 'v':
                # Validate calibration
                print("start validation: %.3f sec"%self.clock.getTime())
                self.validate()
            elif key[0] == 'm':
                # Validate calibration
                print("start manual check: %.3f sec"%self.clock.getTime())
                self.validate_manual()
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
        
        """<DOC>
        Neatly close the tracker
        </DOC>"""
        
        self.tracker.close()
        
    def start_movie(self, format='XMP4',filename='movie', path='', duration_ms=None):
        
        """<DOC>
        Start recording a movie of the eye.
        
        Arguments:
        format -- a string indicating what type of file should be saved. Acceptable: ['JPG','BMP','XVID','HUFFYUV','ALPARY','XMP4' [default]]
        filename -- a string indicating the filename where the output should be saved. [default: 'movie']
        path -- a string indicating where the file should be saved on the iViewX computer. If empty [default], it will be saved in the eyeImages subfolder of the iViewX directory.
        duration_ms -- an integer indicating how long (in ms) the movie should be. If None [default], keep going until the end_movie function is called.
        </DOC>"""
        
        # get number for format specifier
        formats=['JPG','BMP','XVID','HUFFYUV','ALPARY','XMP4']
        try:
            formatNum=formats.index(format)
        except ValueError:
            print 'Format %s not recognized... Recording will not be saved!'%format
            raise # show exception
            
        # send command differently depending on # inputs provided
        if not path:
            self.send('ET_EVB %d "%s"' % (formatNum,filename))
        elif duration_ms is None:
            self.send('ET_EVB %d "%s" "%s"' % (formatNum,filename,path))
        else:
            self.send('ET_EVB %d "%s" "%s" %d' % (formatNum,filename,path,duration_ms))
        
    def end_movie(self):
        
        """<DOC>
        Stop recording a movie of the eye started with start_movie and save the file (with name/options specified in start_movie).
        </DOC>"""
        
        # send command to tracker
        self.send('ET_EVE')
    
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