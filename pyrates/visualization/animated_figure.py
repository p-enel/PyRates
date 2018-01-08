'''
Contains the classes of figure that can for synchronize axes (subplots). 
'''
# Standard imports
import matplotlib.pyplot as pl
import numpy as np
from warnings import warn

# Local imports
from pyrates.utils.common_methods import get_units_to_plot, flatten_layer
from animated import AnimatedHinton, AnimatedPlot

__all__ = ["AnimatedFigure", "PyRatesFig"]

class AnimatedFigure(object):
    def __init__(self,
                 env=None,
                 title='',
                 windowTitle=None,
                 positions=None,
                 *args, **kwargs):
        '''A figure that contains animated plots
        
        Arguments:
        - env: the VisEnvironment instance linked to this AnimatedFigure. If the
            figure is created with VisEnvironment.add_ad_figure, you do not need
            to specify this argument.
        - title: title of the figure. It will appear at the top of the figure
        - windowTitle: title of the window which appears in the top bar of the
            figure window.
        - positions: the number and positions of the subplots. If you set this
            argument, if must be an integer between 11 and 99. The first figure
            digit is the row of rows in the subplot grid and the second digit
            the number of columns. Then when adding subplots to the figure with
            add_plot and add_hinton, no position for the subplot must be
            specified, subplots will automatically be placed starting from the
            first row, filling all the columns from the first row, then the
            second row and so on...
        '''
        
        self.figure = pl.figure(*args, **kwargs)
        if windowTitle is not None:
            self.figure.canvas.set_window_title(windowTitle) 
        self.figure.suptitle(title)
        self.canvas = self.figure.canvas
        self.env = env
        self.animated_axes = []
        self.animated_plots = []
        self.positions = positions
        if self.positions != None:
            self.next_position_to_fill = self.positions[0] * 100 + self.positions[1] * 10 + 1
        self.animated_hintons = []
#        self.figure.canvas.mpl_connect('resize_event', self.on_resize)
#        self.figure.canvas.mpl_connect('key_press_event', self.on_key_event)
        self.figure.canvas.mpl_connect('close_event', self.on_close_figure)
        self.ref = None
#        self.figure.canvas.mpl_disconnect
    
    def __add_subplot(self,
                      axes_class,
                      title,
                      titlePosition=None,
                      position=None):
        
        if position != None:
            if self.positions != None:
                msg = '\nYou cannot specify a position for a subplot if you '
                msg += 'specified positions for the figure. Position of figure '
                msg += 'is ignored.'
                warn(msg)
                position = None
                
        if position == None:
            if self.positions != None:
                if self.next_position_to_fill <= (self.positions[0] * 100 + self.positions[1] * 10 + self.positions[0] * self.positions[1]):
                    position = self.next_position_to_fill
                    self.next_position_to_fill += 1
                else:
                    if title != '':
                        msg = 'subplots cannot be added without specifying a position, the figure entitled "%s" is full' %title
                    else:
                        msg = 'subplots cannot be added without specifying a position, this figure is full'
                    raise Warning, msg
            else:
                raise ValueError, 'A position must be specified to add a subplot (plot, hinton or any other kind of subplot)'
        
            
        sharex = None
        if axes_class == AnimatedPlot:
            for ad_axes in self.animated_axes:
                if ad_axes.__class__ == AnimatedPlot:
                    sharex = ad_axes.ax
        
        ax = self.figure.add_subplot(position,
                                     sharex=sharex)
        
        ax.set_title(label=title,
                     position=titlePosition)
        return ax
        
    def add_plot(self,
                 data,
                 position=None,
                 title='',
                 ref_line=True,
                 *args, **kwargs):
        '''Add a plot type subplot
        
        Arguments:
        - data: plotted data
        - position: position of the subplot
        - title: title of the subplot, will appear on top
        - ref_line: show or not the reference line at the center of the plot
        '''
        ax = self.__add_subplot(AnimatedPlot,
                                title,
                                titlePosition=(0.5,1),
                                position=position)
        
        animated_ax = AnimatedPlot(data=data,
                                   axes=ax,
                                   ref_lineON=ref_line,
                                   *args, **kwargs)
        self.animated_axes.append(animated_ax)
        self.animated_plots.append(animated_ax)
        animated_ax.ad_figure = self
        return animated_ax
    
    def add_hinton(self,
                   data,
                   position=None,
                   title='',
                   minValue=None,
                   maxValue=None,
                   *args, **kwargs):
        '''Add a hinton diagram subplot
        
        Arguments:
        - data: plotted data
        - position: position of the subplot
        - title: title of the subplot, will appear at the bottom of the plot
        '''        
        ax = self.__add_subplot(AnimatedHinton,
                                title,
                                titlePosition=(0.5,-0.13),
                                position=position)
        
        animated_ax = AnimatedHinton(data=data,
                                     axes=ax,
                                     minValue=minValue,
                                     maxValue=maxValue,
                                     *args, **kwargs)
        
        self.animated_axes.append(animated_ax)
        self.animated_hintons.append(animated_ax)
        animated_ax.ad_figure = self
        return animated_ax
        
    def initialize(self, ref=0, xAxisSize=None):
        
        for ad_axes in self.animated_axes:
            ad_axes.initialize()
        if self.animated_plots != []:
            if xAxisSize is not None:
                self.animated_plots[0].ax.set_xlim(0,xAxisSize)
            self.animated_plots[0].get_ref_from_middle()
        self.go_to_ref(ref)
        self.ref = ref
        self.redraw()
        self.figure.canvas.manager.toolbar.pan()
        
    def plot_end_pan(self, ref):
        
        for ad_plot in self.animated_plots:
            ad_plot.ref = ref
        for ad_hinton in self.animated_hintons:
            ad_hinton.go_to_ref(ref)
        self.ref = ref
        self.redraw()
        if self.env != None:
            self.env.plot_end_pan(ref, self)
    
    def go_to_ref(self, newRef):
        
        if self.animated_plots != []:
            # Moving the ref for one animated plot should be enough to move all
            # of them if they are synced?
            self.animated_plots[0].go_to_ref(newRef)
        for ad_hinton in self.animated_hintons:
            ad_hinton.go_to_ref(newRef)
        self.ref = newRef
        self.redraw()
    
    def get_ref(self):
        
        return self.ref
    
    def draw_hintons(self):
        
        for ad_hinton in self.animated_hintons:
            ad_hinton._draw_squares()
    
    def on_resize(self, event):
        
        for hinton in self.animated_hintons:
            hinton._save_background()
            hinton._draw_squares()
    
    def redraw(self, *args):
        self.figure.canvas.draw()

    def next_step(self):
        
        self.go_to_ref(self.ref + 1)
        
    def previous_step(self):
        
        self.go_to_ref(self.ref - 1)
    
    def set_title(self, title):
        
        self.figure.suptitle(title)
    
#    def on_key_event(self, event):
#        if event.key == 'h':
#            self.figure.canvas.toolbar.home()
#        elif event.key == 'p':
#            self.figure.canvas.toolbar.pan()
#        elif event.key == 'z':
#            self.figure.canvas.toolbar.zoom()
#        elif event.key == 'c':
#            self.figure.canvas.toolbar.configure_subplot(None)
        
    def on_close_figure(self, event):
        
        if self.env != None:
            self.env.del_ad_figure(self)

# Local imports
from pyrates.utils.common_methods import reshape_matrices

class PyRatesFig(AnimatedFigure):
    
    def __init__(self,
                 results_dict,
                 *args, **kwargs):
    
        self.resultsDict = results_dict
        super(PyRatesFig, self).__init__(*args, **kwargs)
        
    def add_plot(self,
                 simObjName=None,
                 dataType=None,
                 unitsToPlot=None,
                 ylim='auto',
                 *args, **kwargs):
        
        if simObjName == None:
            raise ValueError, 'a simObjName argument must be given'
        
        if dataType == None:
            dataType = self._default_data_type(simObjName)
        
        if unitsToPlot is not None:
            data = get_units_to_plot(self.resultsDict[simObjName][dataType], unitsToPlot)
        else:
            data = self.resultsDict[simObjName][dataType]
        
        if ylim == 'auto':
            valLims = self.get_valuelim(simObjName, dataType)
            ylim = self.get_ylim_(valLims)
            
        super(PyRatesFig, self).add_plot(data = data, ylim = ylim, *args, **kwargs)
    
    def get_valuelim(self, simObjName, dataType):
        
        def min_max_vals(data):
            minimum = np.floor(np.min(data))
            maximum = np.ceil(np.max(data))
            return [minimum, maximum]
        
        if self.resultsDict[simObjName]['object_type'] == 'connection':
            if dataType == 'weights':
                return self.resultsDict[simObjName]['weightsRange']
            if dataType == 'output':
                return min_max_vals(self.resultsDict[simObjName]['output'])
            
        elif self.resultsDict[simObjName]['object_type'] == 'group':
            if dataType == 'output':
                if 'outputRange' in self.resultsDict[simObjName].keys():
                    return self.resultsDict[simObjName]['outputRange']
                else:
                    return min_max_vals(self.resultsDict[simObjName][dataType])
            else:
                return min_max_vals(self.resultsDict[simObjName][dataType])
            
    def get_ylim_(self, limits):
        range_ = limits[1] - limits[0]
        return [limits[0] - range_ / 20, limits[1] + range_ / 20]
            
    def add_hinton(self,
                   simObjName,
                   dataType=None,
                   unitsToPlot=None,
                   *args, **kwargs):
        
        if simObjName == None:
            raise ValueError, 'a simObjName argument must be given'

        if dataType == None:
            dataType = self._default_data_type(simObjName)
        
        # Reshape data depending on the nature of this data:
        if self.resultsDict[simObjName]['object_type'] == 'group':
            data = reshape_matrices(self.resultsDict[simObjName][dataType], self.resultsDict[simObjName]['shape'])
        elif self.resultsDict[simObjName]['object_type'] == 'connection':
            if dataType == 'output':
                receivingGroup = self.resultsDict[simObjName]['receivingGroup']
                data = reshape_matrices(self.resultsDict[simObjName][dataType], self.resultsDict[receivingGroup]['shape'])
            else:
                data = self.resultsDict[simObjName][dataType]
        
        if unitsToPlot is not None:
            data = data[unitsToPlot[0]:unitsToPlot[1],unitsToPlot[2]:unitsToPlot[3]]
        
        valueLims = self.get_valuelim(simObjName, dataType)
        
        if 'minValue' not in kwargs.keys():
            minValue = valueLims[0]
        if 'maxValue' not in kwargs.keys():
            maxValue = valueLims[1]
        
        super(PyRatesFig, self).add_hinton(data = data, minValue = minValue, maxValue = maxValue, *args, **kwargs)
        
    def _default_data_type(self, simObjName):
        object_type = self.resultsDict[simObjName]['object_type']
        if object_type == 'group':
            data_type = 'output'
        elif object_type == 'connection':
            data_type = 'weights'
        else:
            msg = 'Type of data to plot for %s must be specified in the '\
            + 'dataType argument!'
            raise TypeError, msg
        return data_type