# scripting_methods module
"""
This module contains all the methods loaded with PyRates that allow the user to script a simulation 
"""
import pickle as pk

import pyrates
from pyrates.pyrates_options import *
from pyrates.core.units import *
from pyrates.simobjects.groups import (Group, ActivatedGroup)
from pyrates.simobjects.nodes import (RealTaskNode, OutputNode, Reservoir, Node,
                                      SingleGrpNode, RecurrentNode, StaticInput)#, TaskNode
#from pyrates.monitors import (Monitor, DAMonitor, ConnectionMonitor,
#                              ActivatedGMonitor, GroupMonitor,
#                              TaskNodeMonitor, InputMonitor)
from pyrates.simobjects.connections import (Connection, DynamicConnection,
                                            DAModulatedConnection)
from pyrates.utils import gzip_save, gzip_load
from pyrates.core.simulation import Simulation, write_data
from pyrates.core.units import Deltat, numericTypes
from pyrates.simobjects.simulation_object import SimulationObject

__all__ = ["reset_states", "reset_states_outputs","monitor_bounds", 
           "save_data", "load_data", "run_sim", "ms", "s", "min"]

###################### Global variables ######################################
# Time variables
ms = 1
s = 1000
min = 60000

###################### Global methods ########################################
def set_deltat(deltat):
    '''Sets the value of deltat directly in the simulation instance.
    deltat is the precision of the simulator and refers to the time elapsed
    between to time steps.
    '''
    if type(deltat) is Deltat:
        sim.set_deltat(deltat)
    elif type(deltat) in numericTypes:
        sim.set_deltat(Deltat(deltat, 1))
    else:
        raise TypeError, 'deltat argument must be a number or a Deltat object'
    
def run_sim(*args, **kwargs):
    """Launch the simulation.
    Arguments:
    - simTime: duration of the simulation
    - deltat: precision of the simulator
    
    Link to method Simulation.run
    """
    sim.run(*args, **kwargs)
    
def reset_states():
    """Reset the state of all groups to zero or their resting state."""
    for group in sim.groups:
        group.set_state()
        
def reset_states_outputs():
    """Reset state and output of all groups to zero (or their resting state)."""
    for group in sim.groups:
        group.set_state()
        group.set_output()

def monitor_bounds(*args, **kwargs):
    '''Set bounds (intervals) within which the monitors will be active and
    record activity from simulation objects.
    For more details, see Simulation.monitor_bounds.__doc__
    '''
    sim.monitor_bounds(*args, **kwargs)

def save_data(folder,
              simulationName,
              compression=True):
    '''Save objects of the simulation on the hard drive with Pickle.
    
    Objects of the simulation are saved in one file inside a dictionary that you
    can retrieve for plotting or compare simulation results, etc...
    
    Arguments:
    - filename: path and name of the file where the data will be saved.
    - objectsList: a list of the objects that should be saved. Does not take
        into account the 'save' argument given when creating objects before
        simulation. To save only the objects that have the 'save' argument to
        True (the default value) leave objectsList to None.
    - compression: if set to True, the data is compressed. This method has
        several advantages: faster and less space on hard drive. Use load_data
        to retrieve compressed data.
        If set to False, the pickle module should be used to load data:
        import pickle as pk
        f = open('path_to_saved_file','r')
        savedData = pk.load(f)
        f.close()
    '''
    sim.set_save_folder(folder, simulationName, compression)
#    write_data(sim.savedData, folder, simulationName, compression)
    
def load_data(filename):
    return gzip_load(filename)

if automatic_object_register:
    global sim
    sim = Simulation(simTime=default_sim_time, deltat=default_delta_t)
    SimulationObject.simulationRef = sim
#    timeInTStep.sim = sim
