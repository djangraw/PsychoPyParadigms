# Copyright (C) 2018 Zhiguo Wang

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or (at
# your option) any later version. 
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details. 
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

# Rev. March, 2018
# 1. added the print_function for Python 3 support
# 2. use the list(zip(x,y)) function to make sure zip returns a list
# 3. Added an image scaling factor to accommodate all versions of the API
# 4. Added the missing CR adjustment keys (-/+=)
# 5. revised the draw_image_line function
# 6. tracker parameters set at initialization

# Rev. July, 2018
# 1. Force drawing in absolute pixel coordinates, switch back to the units
#    set by the user at the end of the calibration routine.
# 2. Updated the draw camera image function
# 3. Updated the draw lozenge function
# 4. camera image and drawing are all properly scaled

# Rev. August 22, 2018
# 1. Misplacement of calibration targets on Macs
# 2. Misalignment of crosshairs/squares and camera image


from __future__ import print_function
from psychopy import visual, event, core, sound
from numpy import linspace
from math import sin, cos, pi
from PIL import Image
import array, string, pylink, os

class EyeLinkCoreGraphicsPsychoPy(pylink.EyeLinkCustomDisplay):
    def __init__(self, tracker, win):
        
        '''Initialize a Custom EyeLinkCoreGraphics  
        
        tracker: an eye-tracker instance
        win: the Psychopy display we plan to use for stimulus presentation  '''
        
        pylink.EyeLinkCustomDisplay.__init__(self)
                
        self.pylinkVer = pylink.__version__
        self.display = win
        self.w, self.h = win.size
        
        # on Macs with HiDPI screens, force the drawing routine to use the size defined
        # in the monitor instance, as win.size will give the wrong size of the screen
        if os.name == 'posix':
            self.w,self.h = win.monitor.getSizePix()
            
        #self.display.autoLog = False
        # check the screen units of Psychopy, forcing the screen to use 'pix'
        self.units = win.units
        if self.units != 'pix': self.display.setUnits('pix')
        
        # Simple warning beeps
        self.__target_beep__ = sound.Sound('A', octave=4, secs=0.1)
        self.__target_beep__done__ = sound.Sound('E', octave=4, secs=0.1)
        self.__target_beep__error__ = sound.Sound('E', octave=6, secs=0.1)
        
        self.imgBuffInitType = 'I'
        self.imagebuffer = array.array(self.imgBuffInitType)
        self.resizeImagebuffer = array.array(self.imgBuffInitType)
        self.pal = None
        self.bg_color = win.color
        self.img_scaling_factor = 3
        self.size = (192*self.img_scaling_factor, 160*self.img_scaling_factor)
        
        # initial setup for the mouse
        self.display.mouseVisible = False
        self.mouse = event.Mouse(visible=False)
        self.last_mouse_state = -1

        # image title & calibration instructions
        self.msgHeight = self.size[1]/20.0
        self.title = visual.TextStim(self.display,'', height=self.msgHeight, color=[1,1,1],
                                     pos = (0,-self.size[1]/2-self.msgHeight), wrapWidth=self.w, units='pix')
        self.calibInst = visual.TextStim(self.display, alignHoriz='left',alignVert ='top', height=self.msgHeight, color=[1,1,1],
                                        pos = (-self.w/2.0, self.h/2.0), units='pix',
                                        text = '''
        Enter: Show/Hide camera image
        Left/Right: Switch camera view
        C: Calibration
        V: Validation
        O: Start Recording
        +=/-: CR threshold
        Up/Down: Pupil threshold
        Alt+arrows: Search limit''')
        
        # lines for drawing cross hair etc.
        self.line = visual.Line(self.display, start=(0, 0), end=(0,0),
                                lineWidth=2.0, lineColor=[0,0,0], units='pix')
        
        # set a few tracker parameters
        self.tracker=tracker
        self.tracker.setOfflineMode()
        self.tracker_version = tracker.getTrackerVersion()
        if self.tracker_version >=3:
            self.tracker.sendCommand("enable_search_limits=YES")
            self.tracker.sendCommand("track_search_limits=YES")
            self.tracker.sendCommand("autothreshold_click=YES")
            self.tracker.sendCommand("autothreshold_repeat=YES")
            self.tracker.sendCommand("enable_camera_position_detect=YES")
        # let the tracker know the correct screen resolution being used
        self.tracker.sendCommand("screen_pixel_coords = 0 0 %d %d" % (self.w-1, self.h-1))
 
    def setup_cal_display(self):
        '''Set up the calibration display before entering the calibration/validation routine'''

        self.display.clearBuffer()
        self.calibInst.autoDraw = True

    def clear_cal_display(self):
        '''Clear the calibration display'''
        
        self.calibInst.autoDraw = False
        self.title.autoDraw = False
        self.display.clearBuffer()
        self.display.color = self.bg_color
        self.display.flip()
        
    def exit_cal_display(self):
        '''Exit the calibration/validation routine, set the screen units to
        the original one used by the user'''
        
        self.display.setUnits(self.units)
        self.clear_cal_display()


    def record_abort_hide(self):
        '''This function is called if aborted'''
        
        pass

    def erase_cal_target(self):
        '''Erase the calibration/validation & drift-check target'''

        self.clear_cal_display()
        self.display.flip()

    def draw_cal_target(self, x, y):
        '''Draw the calibration/validation & drift-check  target'''
        
        self.clear_cal_display()
        xVis = (x -  self.w/2)
        yVis = (self.h/2 - y)
        cal_target_out = visual.GratingStim(self.display, tex='none', mask='circle',
                                            size=2.0/100*self.w, color=[1.0,1.0,1.0], units='pix')
        cal_target_in  = visual.GratingStim(self.display, tex='none', mask='circle',
                                            size=2.0/300*self.w, color=[-1.0,-1.0,-1.0], units='pix')
        cal_target_out.setPos((xVis, yVis))
        cal_target_in.setPos((xVis, yVis))
        cal_target_out.draw()
        cal_target_in.draw()
        self.display.flip()

    def play_beep(self, beepid):
        ''' Play a sound during calibration/drift correct.'''

        if beepid == pylink.CAL_TARG_BEEP or beepid == pylink.DC_TARG_BEEP:
            self.__target_beep__.play()
        if beepid == pylink.CAL_ERR_BEEP or beepid == pylink.DC_ERR_BEEP:
            self.__target_beep__error__.play()
        if beepid in [pylink.CAL_GOOD_BEEP, pylink.DC_GOOD_BEEP]:
            self.__target_beep__done__.play()

    def getColorFromIndex(self, colorindex):
         '''Return psychopy colors for elements in the camera image'''
         
         if colorindex   ==  pylink.CR_HAIR_COLOR:          return (1, 1, 1)
         elif colorindex ==  pylink.PUPIL_HAIR_COLOR:       return (1, 1, 1)
         elif colorindex ==  pylink.PUPIL_BOX_COLOR:        return (-1, 1, -1)
         elif colorindex ==  pylink.SEARCH_LIMIT_BOX_COLOR: return (1, -1, -1)
         elif colorindex ==  pylink.MOUSE_CURSOR_COLOR:     return (1, -1, -1)
         else:                                              return (0,0,0)

    def draw_line(self, x1, y1, x2, y2, colorindex):
        '''Draw a line. This is used for drawing crosshairs/squares'''
        
        if self.pylinkVer[:3] == '1.1':
            x1 = x1/2; y1=y1/2; x2=x2/2;y2=y2/2;
        y1 = (-y1  + self.size[1]/2)* self.img_scaling_factor 
        x1 = (+x1  - self.size[0]/2)* self.img_scaling_factor 
        y2 = (-y2  + self.size[1]/2)* self.img_scaling_factor 
        x2 = (+x2  - self.size[0]/2)* self.img_scaling_factor 
        color = self.getColorFromIndex(colorindex)
        self.line.start     = (x1, y1)
        self.line.end       = (x2, y2)
        self.line.lineColor = color
        self.line.draw()

    def draw_lozenge(self, x, y, width, height, colorindex):
        ''' draw a lozenge to show the defined search limits
        (x,y) is top-left corner of the bounding box
        '''

        if self.pylinkVer[:3] == '1.1':
            x = x/2; y=y/2; width=width/2;height=height/2;
        width = width * self.img_scaling_factor
        height = height* self.img_scaling_factor
        y = (-y + self.size[1]/2)* self.img_scaling_factor 
        x = (+x - self.size[0]/2)* self.img_scaling_factor       
        color = self.getColorFromIndex(colorindex)
        
        if width > height:
            rad = height / 2
            if rad == 0: return #cannot draw the circle with 0 radius
            Xs1 = [rad*cos(t) + x + rad for t in linspace(pi/2, pi/2+pi, 72)]
            Ys1 = [rad*sin(t) + y - rad for t in linspace(pi/2, pi/2+pi, 72)]
            Xs2 = [rad*cos(t) + x - rad + width for t in linspace(pi/2+pi, pi/2+2*pi, 72)]
            Ys2 = [rad*sin(t) + y - rad for t in linspace(pi/2+pi, pi/2+2*pi, 72)]
        else:
            rad = width / 2
            if rad == 0: return #cannot draw sthe circle with 0 radius
            Xs1 = [rad*cos(t) + x + rad for t in linspace(0, pi, 72)]
            Ys1 = [rad*sin(t) + y - rad for t in linspace(0, pi, 72)]
            Xs2 = [rad*cos(t) + x + rad for t in linspace(pi, 2*pi, 72)]
            Ys2 = [rad*sin(t) + y + rad - height for t in linspace(pi, 2*pi, 72)]

        lozenge = visual.ShapeStim(self.display, vertices = list(zip(Xs1+Xs2, Ys1+Ys2)),
                                    lineWidth=2.0, lineColor=color, closeShape=True, units='pix')    
        lozenge.draw()

    def get_mouse_state(self):
        '''Get the current mouse position and status'''
        
        X, Y = self.mouse.getPos()
        mX = self.size[0]/2.0*self.img_scaling_factor + X 
        mY = self.size[1]/2.0*self.img_scaling_factor - Y
        if mX <=0: mX =  0
        if mX > self.size[0]*self.img_scaling_factor:
            mX = self.size[0]*self.img_scaling_factor
        if mY < 0: mY =  0
        if mY > self.size[1]*self.img_scaling_factor:
            mY = self.size[1]*self.img_scaling_factor
        state = self.mouse.getPressed()[0] 
        mX = mX/self.img_scaling_factor
        mY = mY/self.img_scaling_factor
        
        if self.pylinkVer[:3] == '1.1':
            mX = mX *2; mY = mY*2
        return ((mX, mY), state)


    def get_input_key(self):
        ''' this function will be constantly pools, update the stimuli here is you need
        dynamic calibration target '''
        
        ky=[]
        for keycode, modifier in event.getKeys(modifiers=True):
            k= pylink.JUNK_KEY
            if keycode   == 'f1': k = pylink.F1_KEY
            elif keycode == 'f2': k = pylink.F2_KEY
            elif keycode == 'f3': k = pylink.F3_KEY
            elif keycode == 'f4': k = pylink.F4_KEY
            elif keycode == 'f5': k = pylink.F5_KEY
            elif keycode == 'f6': k = pylink.F6_KEY
            elif keycode == 'f7': k = pylink.F7_KEY
            elif keycode == 'f8': k = pylink.F8_KEY
            elif keycode == 'f9': k = pylink.F9_KEY
            elif keycode == 'f10': k = pylink.F10_KEY
            elif keycode == 'pageup': k = pylink.PAGE_UP
            elif keycode == 'pagedown': k = pylink.PAGE_DOWN
            elif keycode == 'up': k = pylink.CURS_UP
            elif keycode == 'down': k = pylink.CURS_DOWN
            elif keycode == 'left': k = pylink.CURS_LEFT
            elif keycode == 'right': k = pylink.CURS_RIGHT
            elif keycode == 'backspace': k = ord('\b')
            elif keycode == 'return': k = pylink.ENTER_KEY
            elif keycode == 'space': k = ord(' ')
            elif keycode == 'escape': k = pylink.ESC_KEY
            elif keycode == 'tab': k = ord('\t')
            elif keycode in string.ascii_letters: k = ord(keycode)
            elif k== pylink.JUNK_KEY: k = 0

            # plus/equal & minux signs for CR adjustment
            if keycode in ['num_add', 'equal']: k = ord('+')
            if keycode in ['num_subtract', 'minus']: k = ord('-')

            if modifier['alt']==True: mod = 256
            else: mod = 0
            
            ky.append(pylink.KeyInput(k, mod))
            #event.clearEvents()
        return ky

    def exit_image_display(self):
        '''Clcear the camera image'''
        
        self.clear_cal_display()
        self.calibInst.autoDraw=True
        self.display.flip()

    def alert_printf(self,msg):
        '''Print error messages.'''
        
        print("Error: " + msg)

    def setup_image_display(self, width, height): 
        ''' set up the camera image, for newer APIs, the size is 384 x 320 pixels'''
        
        self.last_mouse_state = -1
        self.size = (width, height)
        self.title.autoDraw = True
        self.calibInst.autoDraw=True
        
    def image_title(self, text):
        '''Draw title text below the camera image'''
        
        self.title.text = text
        
    def draw_image_line(self, width, line, totlines, buff):
        '''Display image pixel by pixel, line by line'''

        self.size = (width, totlines)        

        i =0
        for i in range(width):
            try: self.imagebuffer.append(self.pal[buff[i]])
            except: pass
            
        if line == totlines:
            bufferv = self.imagebuffer.tostring()
            img = Image.frombytes("RGBX", (width, totlines), bufferv) # Pillow
            imgResize = img.resize((width*self.img_scaling_factor, totlines*self.img_scaling_factor))
            imgResizeVisual = visual.ImageStim(self.display, image=imgResize, units='pix')
            imgResizeVisual.draw()
            self.draw_cross_hair()
            self.display.flip()
            self.imagebuffer = array.array(self.imgBuffInitType)
            
    def set_image_palette(self, r,g,b):
        '''Given a set of RGB colors, create a list of 24bit numbers representing the pallet.
        I.e., RGB of (1,64,127) would be saved as 82047, or the number 00000001 01000000 011111111'''
        
        self.imagebuffer = array.array(self.imgBuffInitType)
        self.resizeImagebuffer = array.array(self.imgBuffInitType)
        #self.clear_cal_display()
        sz = len(r)
        i =0
        self.pal = []
        while i < sz:
            rf = int(b[i])
            gf = int(g[i])
            bf = int(r[i])
            self.pal.append((rf<<16) | (gf<<8) | (bf))
            i = i+1
