"""Base class of all object processed in the neural simulation

Any simulation object class that inherit from this class will be registered to
be part of the simulation. Objects within the simulation must be registered in
ordered to be part of the simulation.
Furthermore, basic information on the objects are saved for results processing.
"""

# Standard imports
import numpy as np

# Local imports


__all__ = ["SimulationObject", "MonitoredObject"]

class SimulationObject(object):
    """Base class of all object processed in the neural simulation
    
    Initial arguments:
    - name: the name given by the user to the object
    - register: a boolean specifies if the object must be registered or not
    - save: if True, the object is saved when the command 'save' is used at the
            end of the simulation
    
    Methods:
      - _register: _register the object in the simulation
    """
    
    # The following variable specifies the Simulation where all the object must
    # be registered. It is assigned in core.global_methods.
    simulationRef = None
    
    # This variable is a reference for the method add_object method assigned in
    # core.global_methods.
#    add_object = None
    
    def __init__(self, name=None, register=True, save=True):
        """
        Arguments:
          - name: the name given by the user to the object. It is strongly
                  recommended to give name to the objects as the simulator may
                  refer to them in the output terminal! 
          - _register: a boolean that specifies if the object must be registered
                      or not. If you don't know what to do just leave the
                      default option.
          - save: boolean, if True properties of the object are saved after the
                  simulation is done with the command save_data(PATH)
        """
        if name is not None:
            self.name = name
            
        if register:
            self._register(save=save)
    
    def set_name(self, name):
        
        self.name = name
        
    def get_name(self):
        
        self.__repr__()
    
    def _register(self, save=True):
        """Register the object in the simulation"""
        self.simulationRef.allObjects.append(self)
        if save:
            self.simulationRef.savedObjects.append(self)
    
    def _saveddata(self):
        """Save object name and class name"""
        savedData = {'name': str(self),
                     'class': str(type(self))}
        return savedData
    
    def __repr__(self):
        """Display name of object"""
        try:
            return self.name
        except AttributeError:
            return '<%s instance>' % str(type(self))

class MonitoredObject(SimulationObject):
    '''The base class for all objects of the simulation that can be monitored'''
    
    # Number of time steps to increment the monitors when the number of time
    # steps in a simulation is unknown. It can be seen as a buffer extension
    # to the monitors
    tsBlockSize = 10000
    
    def __init__(self, monitored=False, *args, **kwargs):
        
        self.isMonitored = monitored
        self.nbTimeStepUnknow = False
        self.monitoredVars = []
        super(MonitoredObject, self).__init__(*args, **kwargs)
    
    def _initialize_monitor(self, nbTimeSteps):
        
        if self.isMonitored:
            if nbTimeSteps is None:
                self.nbTimeStepUnknow = True
                self.nbTimeSteps = MonitoredObject.tsBlockSize
            else:
                self.nbTimeSteps = nbTimeSteps
            self.monitorData = {}
            
            for var in self.monitoredVars:
                varShape = list(np.shape(self.__getattribute__(var)))
                varShape.insert(0, self.nbTimeSteps + 1)
                self.monitorData[var] = np.zeros(varShape)
                self.monitorData[var][0] = self.__getattribute__(var)
            
            self.ownTimeStep = 1
    
    def monitorVars(self, variables=None):
        '''Method to set the monitored variable of the object'''
        if not hasattr(self, 'name'):
            msg = 'To monitor an object, its name variable must be defined!'
            raise AttributeError, msg
        
        if variables is not None:
            if type(variables) != list:
                msg = "Argument of function monitor must be a list of the"\
                +" monitored variables"
                raise TypeError, msg
            for var in variables:
                if var not in self.monitorable():
                    msg = "Variables that can be monitored for %s are:\n%s"
                    msg = msg%(str(type(self)), str(self.monitorable()))
                    raise ValueError, msg
        else:
            variables = self.default_monitored()
        
        for var in variables:
            if var not in self.monitoredVars:
                self.monitoredVars.append(var)
            
        self.isMonitored = True
        self.simulationRef.monitoredObjects.append(self)
    
    def _close_monitors(self):
        
        for var in self.monitoredVars:
            self.monitorData[var] = self.monitorData[var][0 : self.ownTimeStep]
    
    def monitorable(self):
        '''Return the list of variables monitored by default by the class
        Must be overridden in subclasses
        '''
        raise NotImplementedError
    
    def _monitoring(self, timeStep):
        '''Save successive states of variables in the monitors.
        
        Keeps track of the number of time steps, and check that the monitor
        have enough space to save successive states of variables.
        '''
        if self.isMonitored:
            if self.nbTimeStepUnknow == True and self.ownTimeStep > self.nbTimeSteps:
                addedSteps = MonitoredObject.tsBlockSize
                self._update_nbtimestep(addedSteps)
                self.nbTimeSteps += addedSteps
                
            for var in self.monitoredVars:
                self.monitorData[var][self.ownTimeStep] = self.__getattribute__(var)
            self.ownTimeStep += 1
            
    def _update_nbtimestep(self, addedTimeSteps):
        '''Update the number of time steps in the monitors.
        Must be overridden in subclasses
        '''
        for var in self.monitoredVars:
            varShape = list(np.shape(self.__getattribute__(var)))
            varShape.insert(0, addedTimeSteps)
            self.monitorData[var] = np.concatenate((self.monitorData[var], np.zeros(varShape)), axis=0)
    
    def default_monitored(self):
        '''Specify the variables that are monitored by default.
        Must be overridden in subclass.
        '''
        raise NotImplementedError
    
    def _saveddata(self):
        
        savedData = super(MonitoredObject, self)._saveddata()
        savedData.update({'monitored vars': self.monitoredVars})
        for var in self.monitoredVars:
            savedData.update({var: self.monitorData[var]})
        
        return savedData
