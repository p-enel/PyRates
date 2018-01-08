# Visualization subpackage
'''
The visualization subpackage contains an visualization environment that makes it
easier to go through results data of PyRates simulations.

The modules in this subpackage have no documentation yet, please excuse me for
the inconvenience!
'''
import matplotlib
matplotlib.use('Qt4Agg')

from animated_figure import *
from vis_environment import *

del animated_figure
del vis_environment