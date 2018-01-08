# Package PyRates
"""
------------------------------------------------------------------------------
                                Package PyRates
------------------------------------------------------------------------------
Package PyRates is a Python Firing Rate Neurons Simulation Tool.
Dedicated to firing rate neurons, it may extend in the future to other type of
simulated neurons.

Subpackages:
  - core: core functions and classes of the package
  - groups: groups are made of units (neurons)
  - connections: classes that connect two groups/nodes together
  - nodes: nodes take part in the simulation without units (neurons)
  - monitors: monitors record activity or properties of elements of the
    simulation
  - utils: modules used by pyrates classes and modules for users
  
Classes:
  - SimulationObject: the base class for any object that takes part to the
    simulation
    
Modules:
  - pyrates_options: options variable loaded with the package that can be
    changed to suit specific usage of the package
"""

__version__ = '0.1'
__authors__ = 'Pierre Enel'
__contact__ = 'pierre.enel@gmail.com'

# standard modules import
import numpy as np

# Root modules imports
#from simulation_object import *
from pyrates_options import *

# Subpackages imports
from utils import *
from core import *
from simobjects import *
from scripting import *
from visualization import *

# Cleaning namespace

del pyrates_options
