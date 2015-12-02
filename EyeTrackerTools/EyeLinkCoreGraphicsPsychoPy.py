# EyeLinkCoreGraphicsPsychoPy.py
#
# Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in
# the documentation and/or other materials provided with the distribution.
#
# Neither name of SR Research Ltd nor the name of contributors may be used
# to endorse or promote products derived from this software without
# specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS ``AS
# IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES LOSS OF USE, DATA, OR
# PROFITS OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# $Date: 2012/07/16 19:16:00 $
# 
# Created 4/8/15 by DJ - adapted from EyelinkCoreGraphicsPyGame.py.
# Updated 4/9/15 by DJ - extreme debugging, borrowing from pylinkwrapper on github
# Updated 4/10/15 by DJ - switched win units to pixels, general cleanup
# Updated 12/1/15 by DJ - added optional bgcolor and fgcolor inputs


from psychopy import visual, sound, event
#import array
# from python
from PIL import Image
import pylink
import os.path
import sys
# copied from pylinkwrapper on github
import tempfile 
import scipy 
import numpy as np

script_home = os.path.dirname(sys.argv[0])
if len(script_home) > 0 : os.chdir(script_home)
    
class EyeLinkCoreGraphicsPsychoPy(pylink.EyeLinkCustomDisplay):
    def __init__(self, w, h, tracker,bgcolor=(255,255,255),fgcolor=(0,0,0)):
        pylink.EyeLinkCustomDisplay.__init__(self)

        # initialize window
        fullScreen=True
        screenToShow=0
        self.win = visual.Window((w,h), fullscr=fullScreen, allowGUI=False, monitor='testMonitor',screen=screenToShow, units='pix', name='win', color=bgcolor, colorSpace='rgb255')
        self.win.flip(clearBuffer=True)
        
        # declare sounds
        self.__target_beep__ = sound.Sound(value="sounds/type.wav",name='targetBeep')
        self.__target_beep__done__ = sound.Sound(value="sounds/qbeep.wav",name='doneBeep')
        self.__target_beep__error__ = sound.Sound(value="sounds/error.wav",name='errorBeep')
        
        # declare font defaults
        self.fntfile="./cour.ttf"
        self.fnt="cour"
        self.fntbold=True   
        self.fntsize=20  
        
        # set up tracker   
        self.setTracker(tracker) 
        self.last_mouse_state = -1
        
        # create temporary image file
        self.tmp_file = os.path.join(tempfile.gettempdir(),'_eleye.png') # from pylinkwrapper on github
        
        # declare variables from pylinkwrapper on github
        self.blankdisplay = visual.Rect(self.win,w,h,units='pix', name='BACKGROUND', fillColor=bgcolor,fillColorSpace='rgb255', lineColor=bgcolor,lineColorSpace='rgb255') # adapted from pylinkwrapper on github
        # declare circle sizes    
        outsz = 10
        insz = 4        
        # create white circle in a black circle    
        self.outercircle = visual.Circle(self.win,pos=(0,0), radius=outsz, fillColor=fgcolor, fillColorSpace='rgb255', lineColor=fgcolor,lineColorSpace='rgb255', units='pix',name='outercircle')
        self.innercircle = visual.Circle(self.win,pos=(0,0), radius=insz, fillColor=bgcolor, fillColorSpace='rgb255', lineColor=bgcolor,lineColorSpace='rgb255', units='pix',name='innercircle')
        self.rgb_index_array = None # rgb index array for line drawings
        self.imgstim_size = None
        self.eye_image = None 
        self.imagetitlestim = None
        self.size = (0, 0)
    
    def setTracker(self, tracker):
        self.tracker = tracker
        self.tracker_version = tracker.getTrackerVersion()
        if(self.tracker_version >= 3):
            self.tracker.sendCommand("enable_search_limits=YES")
            self.tracker.sendCommand("track_search_limits=YES")
            self.tracker.sendCommand("autothreshold_click=YES")
            self.tracker.sendCommand("autothreshold_repeat=YES")
            self.tracker.sendCommand("enable_camera_position_detect=YES")
        
    
    def setup_cal_display (self):
        self.win.flip()
        
    def exit_cal_display(self): 
        self.clear_cal_display()
        
    def record_abort_hide(self):
        pass

    def clear_cal_display(self): 
        self.blankdisplay.draw()
        self.win.flip()
        
    def erase_cal_target(self):
        self.clear_cal_display()
        
    def draw_cal_target(self, x, y): 
        # convert to psychopy pix coords
        x = x-self.win.size[0]/2
        y = -(y-self.win.size[1]/2)
        # move circles
        self.outercircle.pos = (x,y)
        self.innercircle.pos = (x,y)
        # draw circles and update screen
        self.blankdisplay.draw()
        self.outercircle.draw()
        self.innercircle.draw()        
        self.win.flip()
        
    def play_beep(self, beepid):
        # same as pygame
        if beepid == pylink.DC_TARG_BEEP or beepid == pylink.CAL_TARG_BEEP:
            self.__target_beep__.play()
        elif beepid == pylink.CAL_ERR_BEEP or beepid == pylink.DC_ERR_BEEP:
            self.__target_beep__error__.play()
        else:#    CAL_GOOD_BEEP or DC_GOOD_BEEP
            self.__target_beep__done__.play()
        
    
    def getColorFromIndex(self, colorindex):
        # same as pygame, but RGB without opacity
        if colorindex == pylink.CR_HAIR_COLOR:          return (255, 255, 255)
        elif colorindex == pylink.PUPIL_HAIR_COLOR:       return (255, 255, 255)
        elif colorindex == pylink.PUPIL_BOX_COLOR:        return (0, 255, 0)
        elif colorindex == pylink.SEARCH_LIMIT_BOX_COLOR: return (255, 0, 0)
        elif colorindex == pylink.MOUSE_CURSOR_COLOR:     return (255, 0, 0)
        else: return (0, 0, 0)
        
    def draw_line(self, x1, y1, x2, y2, colorindex):
        # get color and window size
        color = self.getColorFromIndex(colorindex)
        # convert positions    to norm units [-1,1]    
        x1 = (float(x1) / float(self.size[0])) * 2 - 1
        x2 = (float(x2) / float(self.size[0])) * 2 - 1
        y1 = (float(y1) / float(self.size[1])) * 2 - 1
        y2 = (float(y2) / float(self.size[1])) * 2 - 1
        # plot line
        line = visual.Line(self.win, start=(x1,y1), end=(x2,y2), color=color, colorSpace='rgb255', units='norm')        
        line.draw()
        # update display
        # self.win.flip()        
                
    
    def draw_lozenge(self, x, y, width, height, colorindex):
        
        ci = 100
        color = self.getColorFromIndex(colorindex)
        
        #guide
        #self.draw_line(x,y,x+width,y,ci) #hor
        #self.draw_line(x,y+height,x+width,y+height,ci) #hor
        #self.draw_line(x,y,x,y+height,ci) #ver
        #self.draw_line(x+width,y,x+width,y+height,ci) #ver
        
        # convert positions to norm units [-1,1]
        x = (float(x) / float(self.win.size[0])) * 2 - 1
        width = (float(width) / float(self.win.size[0])) * 2 - 1
        y = (float(y) / float(self.win.size[1])) * 2 - 1
        height = (float(height) / float(self.win.size[1])) * 2 - 1
        
         
        if width > height:
            rad = height / 2
            
            #draw lines
            line1 = visual.line(self.win, start=(x+rad, y), end=(x+width-rad, y), color=color, colorSpace='rgb255', units='norm')
            line2 = visual.line(self.win, start=(x+rad, y+height), end=(x+width-rad, y+height), color=color, colorSpace='rgb255', units='norm')
            line1.draw()
            line2.draw()
            
            #draw semicircles (circles for now)
            circle1 = visual.circle(self.win, pos=(x+rad,y+rad), radius=rad, fillColor=color, fillColorSpace='rgb255', lineColor=color,lineColorSpace='rgb255')
            circle2 = visual.circle(self.win, pos=(x+width-rad,y+rad), radius=rad, fillColor=color, fillColorSpace='rgb255', lineColor=color,lineColorSpace='rgb255')
            circle1.draw()
            circle2.draw()
            
        else:
            rad = width / 2

            #draw lines
            line1 = visual.line(self.win, start=(x, y+rad), end=(x, y+height-rad), color=color, colorSpace='rgb255', units='norm')
            line2 = visual.line(self.win, start=(x+width, y+rad), end=(x+width, y+height-rad), color=color, colorSpace='rgb255', units='norm')
            line1.draw()
            line2.draw()
            
            #draw semicircles (circles for now)
            circle1 = visual.circle(self.win, pos=(x+rad,y+rad), radius=rad, color=color, colorSpace='rgb255')
            circle2 = visual.circle(self.win, pos=(x+rad,y+height-rad), radius=rad, color=color, colorSpace='rgb255')
            circle1.draw()
            circle2.draw()
            
            
    def get_mouse_state(self):
        pos = event.getPos() #(x,y)
        state = event.getPressed() # outputs list of mouse buttons 0,1,2
        return (pos, state[0]) # return left button only
        
    def get_input_key(self):
        ky = []
        v = event.getKeys() # returns list of keypresses
        for keycode in v:            
            # function keys
            if keycode == 'f1':  keycode = pylink.F1_KEY
            elif keycode == 'f2':  keycode = pylink.F2_KEY
            elif keycode == 'f3':  keycode = pylink.F3_KEY
            elif keycode == 'f4':  keycode = pylink.F4_KEY
            elif keycode == 'f5':  keycode = pylink.F5_KEY
            elif keycode == 'f6':  keycode = pylink.F6_KEY
            elif keycode == 'f7':  keycode = pylink.F7_KEY
            elif keycode == 'f8':  keycode = pylink.F8_KEY
            elif keycode == 'f9':  keycode = pylink.F9_KEY
            elif keycode == 'f10': keycode = pylink.F10_KEY
            # arrow keys
            elif keycode == 'pageup': keycode = pylink.PAGE_UP
            elif keycode == 'pagedown':  keycode = pylink.PAGE_DOWN
            elif keycode == 'up':    keycode = pylink.CURS_UP
            elif keycode == 'down':  keycode = pylink.CURS_DOWN
            elif keycode == 'left':  keycode = pylink.CURS_LEFT
            elif keycode == 'right': keycode = pylink.CURS_RIGHT
            # escape keys
            elif keycode == 'backspace':    keycode = ord('\b')
            elif keycode == 'return':  keycode = pylink.ENTER_KEY
            elif keycode == 'escape':  keycode = pylink.ESC_KEY
            elif keycode == 'tab':     keycode = ord('\t')
            elif(keycode == pylink.JUNK_KEY): keycode = 0
            
            # add to buffer to send to eyelink
            ky.append(pylink.KeyInput(keycode, 0)) # 0 used to be key.mod
        return ky
        
    def exit_image_display(self):
        self.clear_cal_display()
        
    def alert_printf(self, msg): 
        print("alert_printf")
            
    
    def setup_image_display(self, width, height):
        self.size = (width, height)
        self.clear_cal_display()
        self.last_mouse_state = -1
        # initialize rgb_index_array (from pylinkwrapper on github)
        if self.rgb_index_array is None:
            self.rgb_index_array =  np.zeros((height, width), dtype = np.uint8)   
        return 1
        
    def image_title(self, text): 
        """
        Display the current camera, Pupil, and CR thresholds above
        the camera image when in Camera Setup Mode.
        """
        if self.imagetitlestim is None:
           self.imagetitlestim = visual.TextStim(self.win,
                text=text,name='ELImageTitle',
                pos=(0,self.win.size[1]/2-15), height = 28,
                color=(0, 0, 0), colorSpace='rgb255',
                opacity=1.0, contrast=1.0, units='pix',
                ori=0.0, antialias=True,
                bold=False, italic=False, alignHoriz='center',
                alignVert='top', wrapWidth=self.win.size[0]*.8)
        else:
            self.imagetitlestim.setText(text)
        #self.imagetitlestim.draw()
                
        
    def draw_image_line(self, width, line, totlines, buff):    # adapted from pylinkwrapper on github    
        """
        Collects all lines for an eye image, saves the image,
        then creates a psychopy imagestim from it.
        """        
        
        for i in range(width):
            try:
                self.rgb_index_array[line-1, i] = buff[i]
            except Exception, e:
                print("FAILED TO DRAW PIXEL TO IMAGE LINE: %d %d"%(line-1,i))
                # printExceptionDetailsToStdErr()
                # print2err("FAILED TO DRAW PIXEL TO IMAGE LINE: %d %d"%(line-1,i))

        # Once all lines have been collected, go through the hoops needed
        # to display the frame as an image; scaled to fit the display resolution.
        if line == totlines:
            try:
                image = scipy.misc.toimage(self.rgb_index_array,
                                           pal=self.rgb_pallete,
                                           mode='P')
                if self.imgstim_size is None:
                    maxsz = self.win.size[0]/2
                    mx = 1.0
                    while (mx+1) * self.size[0] <= maxsz:
                        mx += 1.0
                    self.imgstim_size = int(self.size[0]*mx), int(self.size[1]*mx)
                image = image.resize(self.imgstim_size)

                #TODO: There must be a way to just hand an ImageStim a nxmx3
                # array for the image data??
                image.save(self.tmp_file, 'PNG')
                if self.eye_image is None:
                    self.eye_image = visual.ImageStim(self.win, self.tmp_file, pos=(0,0), units='pix', name='ELEyeImage')
                else:
                    self.eye_image.setImage(self.tmp_file)

                # Redraw the Camera Setup Mode graphics
                self.blankdisplay.draw()
                self.eye_image.draw()
                if self.imagetitlestim:
                    self.imagetitlestim.draw()
                self.win.flip()

            except Exception, err:
                print ("Error during eye image display: %s"%err)
                # import traceback
                # print2err("Error during eye image display: ", err)
                # printExceptionDetailsToStdErr()
            
                            
    def set_image_palette(self, r, g, b):     # copied from pylinkwrapper on github
        """
        Set color palette ued by host pc when sending images.
        Saves the different r,g,b values provided by the eyelink host palette.
        When building up each eye image frame, eyelink sends the palette
        index for each pixel; so an eyelink eye image frame can be a 2D lookup
        array into this palette.
        """
        self.clear_cal_display()
        sz = len(r)
        self.rgb_pallete = np.zeros((sz, 3), dtype=np.uint8)
        i = 0
        while i < sz:
            self.rgb_pallete[i:] = int(r[i]), int(g[i]), int(b[i])
            i += 1
        