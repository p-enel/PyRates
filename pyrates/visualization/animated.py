'''
Contains the matplotlib axes developed to suit the interaction visualization of
PyRates data.
'''
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.backends.backend_agg import FigureCanvasAgg

class AnimatedAxes(object):
    
    def __init__(self, data, axes):
        self.data = data
        self.ax = axes
        self.figure = self.ax.figure
        self.canvas = self.figure.canvas
    
    def initialize(self, ref = None):
        if ref == None:
            ref = 0
        self.ref = ref
        FigureCanvasAgg.draw(self.canvas)
        self._save_background()
    
    def _save_background(self):
        self.background = self.canvas.copy_from_bbox(self.ax.bbox)
    
    def _blit(self):
        self.canvas.blit(self.ax.bbox)
    
    def _clear_axes(self):
        self.canvas.restore_region(self.background)
        self._blit()
    
    def go_to_ref(self, ref):
        # This method must be overriden in each class that inherit from this one
        pass
    
class AnimatedHinton(AnimatedAxes):
    
    def __init__(self, minValue = 0, maxValue = None, *args, **kwargs):
        """
        Draws a Hinton diagram for visualizing a weight matrix. 
        Temporarily disables matplotlib interactive mode if it is on, 
        otherwise this takes forever.
        """
#        print 'minValue ' + str(minValue)
        super(AnimatedHinton, self).__init__(*args, **kwargs)
        
        if len(self.data.shape) != 3:
            raise ValueError, 'The data argument for AnimatedHinton objectToRegister must be a 3D array'
        
        self.shape = self.data[0].shape
        self.height, self.width = self.shape
        if minValue == None:
            self.minValue = 0
        else:
            if minValue < 0:
                self.minValue = 0
            else:
                self.minValue = minValue
        if maxValue == None:
            max_tmp = -999
            for i in range(self.data.shape[0]):
                if np.max(self.data[i]) > max_tmp:
                    max_tmp = np.max(self.data[i])
            self.maxValue = max_tmp
        else:
            self.maxValue = maxValue
        ########### Setting background and grid #######################################
        self.ax.fill(np.array([0,self.width,self.width,0]),np.array([0,0,self.height,self.height]),'white')
        for x in range(1,self.width,1):
            self.ax.plot([x,x],[0,self.height], color='black')
        for y in range(1,self.height,1):
            self.ax.plot([0,self.width],[y,y], color='black')
        ###############################################################################
    
        self.ax.invert_yaxis()
#        self.ax.axis('equal')
        self.ax.xaxis.tick_top()
        self.ax.xaxis.set_ticks(np.arange(0.5,self.width,1))
        self.ax.xaxis.set_ticklabels(range(self.width))
        self.ax.yaxis.set_ticks(np.arange(0.5,self.height,1))
        self.ax.yaxis.set_ticklabels(range(self.height))
    
    def _create_square(self, i, j, value, color):
        """
        Draws a square-shaped blob with the given area (< 1) at
        the given coordinates.
        """
        value = max(min(1, value / self.maxValue), self.minValue) - self.minValue
        x = j + 0.5
        y = i + 0.5
        hs = np.sqrt(value) / 2
        xcorners = np.array([x - hs, x + hs, x + hs, x - hs])
        ycorners = np.array([y - hs, y - hs, y + hs, y + hs])
        self.polygons[i][j] = self.ax.fill(xcorners, ycorners, color = color, edgecolor='none', animated=False)[0]
    
    def initialize(self, *args, **kwargs):
        super(AnimatedHinton, self).initialize(*args, **kwargs)
        
        if not self.maxValue:
            maximum = np.max(np.abs(self.data[self.ref]))
            if maximum == 0:
                self.maxValue = 1
            else:
                self.maxValue = 2**np.ceil(np.log(np.max(np.abs(self.data[self.ref])))/np.log(2))
        
        self.polygons = [[0] * self.width]
        for i in xrange(1, self.height):
            self.polygons.append([0] * self.width)
        
#        pl.axis('off')
        for i in xrange(self.height):
            for j in xrange(self.width):
                value = self.data[self.ref, i, j]
                self._create_square(i, j, value, 'black')
        self._draw_squares()
        
#    def _draw_squares_not_ad(self):
#        for lines in self.polygons:
#            for polygon in lines:
#                polygon.setp(animated)
#                self.ax.draw_artist(polygon)
    
    def _draw_squares(self):
        for line in self.polygons:
            for polygon in line:
                self.ax.draw_artist(polygon)
        self._blit()
                
    def _update(self, newMatrix):
#        bool_updateMatrix = self.matrix != newMatrix
        
        self.canvas.restore_region(self.background)
        
        for i in xrange(self.height):
            for j in xrange(self.width):
#                if bool_updateMatrix[x][y]:
                newValue = newMatrix[i,j]
                self.__set_ploygon_new_corners(i, j, newValue)
        
#        self._draw_squares()
    
    def get_ref(self):
        return self.ref
    
    def go_to_ref(self, newRef):
        try:
            if newRef < 0:
                raise IndexError
            else:
                self._update(self.data[newRef])
        except IndexError:
            print 'Index out of range for hinton diagram'
            self._update(np.zeros(self.shape))

    def __set_ploygon_new_corners(self, i, j, newValue):
        area = max(min(1, newValue/self.maxValue), 0)
        hs = np.sqrt(area) / 2
        x = j + 0.5
        y = i + 0.5
        self.polygons[i][j].set_xy(np.array([[x - hs, y - hs],
                                 [x + hs, y - hs],
                                 [x + hs, y + hs],
                                 [x - hs, y + hs],
                                 [x - hs, y - hs]]))

class AnimatedPlot(AnimatedAxes):
    # see animation_blit_gtk2.py in testing stuff/visualization/Animated plots Matplotlib for accelerated display (wihtout draw canvas again)
    def __init__(self, ref_lineON = True, sliding_effect = 'plot', ylim = None, *args, **kwargs):
        super(AnimatedPlot, self).__init__(*args, **kwargs)
        self.sliding_effect = sliding_effect
        self.ref_lineON = ref_lineON
        self.ax.end_pan = self.end_pan
        self.ylim = ylim
        self.canvas.mpl_connect('button_release_event', self.on_click_inaxes)
    
    def initialize(self, ref = None):
#        super(AnimatedPlot, self).initialize(*args, **kwargs)
        if self.ref_lineON:
            self.add_refLine()
        if self.sliding_effect == 'ref_line':
            animated = True
        elif self.sliding_effect == 'plot':
            animated = False
        self.ax.plot(self.data, animated = animated)
        if self.ylim != None:
            self.ax.set_ylim(self.ylim)
        
    def add_refLine(self):
        if self.sliding_effect == 'ref_line':
            animated = True
        elif self.sliding_effect == 'plot':
            animated = False
        self.ref_line = self.ax.add_line(Line2D([0.5, 0.5], [0, 1], transform=self.ax.transAxes, linewidth=1, color='k', ls = '-.', animated = animated))
    
    def set_xlim(self, bounds):
        self.ax.set_xlim(bounds)
        
    def end_pan(self):
        self.get_ref_from_middle()
        try:
            self.ad_figure.plot_end_pan(self.ref)
        except AttributeError:
            pass
        print 'Move to x value: %d'%self.ref
    
    def get_ref(self):
        return self.ref
    
    def get_ref_from_middle(self):
        xl = self.ax.get_xlim()
        self.ref = int(round(abs(xl[1]-xl[0])/2. + xl[0]))
    
    def go_to_ref(self, newRef):
        current_ref = self.get_ref()
        current_xlim = self.ax.get_xlim()
        nbSteps_toMove = newRef - current_ref
        xlim = []
        xlim.append(current_xlim[0] + nbSteps_toMove)
        xlim.append(current_xlim[1] + nbSteps_toMove)
        self.ax.set_xlim(xlim)
        self.ref = newRef
        
    def go_to_ref_REF_MOVE(self, newRef):
        pass

    def resize_xlim(self):
        current_ref = self.get_ref()
        current_xlim = self.ax.get_xlim()
        x_span = current_xlim[1] - current_xlim[0]
        self.go_to_ref(current_ref + x_span / 2)

    def on_click_inaxes(self, event):
        if event.inaxes == self.ax and event.inaxes.get_navigate_mode() == 'ZOOM':
            self.end_pan()

    
