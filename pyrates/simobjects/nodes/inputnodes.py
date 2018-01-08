"""
This module contains the input groups classes
"""

import numpy as np
from pyrates.utils.common_methods import checkIfInOptionList, typeAndSize
from pyrates.simobjects.nodes import Node

__all__ = ["StaticInput", "NoiseGenerator", "InputGroup"]

class InputGroup(Node):
    """The role of this class is mainly a way to identify input group as part of
    a branch of the group class.
    """
    
    def __init__(self,
                 groupClass,
                 name=None,
                 groupArgs={},
                 *args, **kwargs):
        
        groupArgs['save'] = False
        groupArgs['parentNode'] = self
        if name is not None:
            groupArgs['name'] = name + 'OutputGroup'
        else:
            groupArgs['name'] = 'outputGroup'
            
        outputGroup = groupClass(**groupArgs)
        
        super(InputGroup, self).__init__(name=name,
                                         outputGroup=outputGroup,
                                         *args, **kwargs)
    
    def _initialize(self):
        """Set parameters before running the simulation.
        This method may need to be overridden by subclasses in some cases. 
        """
        self.outputGroup._initialize()
    
    def _execute(self, timeStep):
        """Set parameters before running the simulation.
        This method may need to be overridden by subclasses in some cases. 
        """
        self.outputGroup._execute(timeStep)
    
    def get_nbtimesteps(self):
        """Return the number of time steps needed for this node
        This method needs to be overridden by subclasses in some cases.
        """
        pass
    
    def _saveddata(self):
        
        savedData = super(InputGroup, self)._saveddata()
        savedData.update({'outputGroup': self.outputGroup._saveddata()})
        return savedData
    
    def _register(self, save=True):
        
        self.simulationRef.inputs.append(self)
        super(InputGroup, self)._register(save=save)

class StaticInput(InputGroup):
    """A static input is a 3D matrix that can be fed to another unit group (e.g.
    a neuron group).
    The first index of the input matrix is the time step. The other indices are
    the indices of the units.
        e.g. -> staticInput[452,10,2] is the state of the unit with indices
                [10,2] at time step 452.
    """
    
    def __init__(self,
                 inputMatrix,
                 groupArgs={},
                 *args, **kwargs):
        
        if not isinstance(inputMatrix, np.ndarray):
            raise Exception, 'The input argument of a Static input must be an' \
                + ' np.ndarray whose first dimension represents the successive'\
                + ' steps'
        
        if 'nbUnits' in kwargs.keys():
            msg = 'The nbUnits argument must not be defined for StaticInput ' \
            + 'class, it is given by the size of the inputMatrix'
            raise Exception, msg
        
        shape = list(inputMatrix.shape[1:])
        if len(shape) == 1:
            shape.append(1)
        
        groupArgs['shape'] = shape
        
        super(StaticInput, self).__init__(groupArgs=groupArgs,
                                          *args, **kwargs)
        
        self.inputMatrix = inputMatrix
        self.nbTimeStepsSim = self.inputMatrix.shape[0]
        
        print 'There are ' + str(self.nbTimeStepsSim) + ' time-steps in the input'\
        + ' \'' + str(self) + '\''
    
    def get_nbtimesteps(self):
        
        return self.nbTimeStepsSim
        
    def _initialize(self):
        """During this initialization, we shape the n-dim input matrix into a 2D
        matrix in order to use it as any other unit group.
        """
        self.flattenedInputMatrix = np.zeros((self.nbTimeStepsSim,
                                              self.outputGroup.nbUnits))
        for i in range(self.nbTimeStepsSim):
            self.flattenedInputMatrix[i,:] = np.ravel(self.inputMatrix[i])
        self.outputGroup.state = self.flattenedInputMatrix[0,:]
        super(StaticInput, self)._initialize()
    
    def _execute(self, timeStep):
        
        try:
            self.outputGroup.state = self.flattenedInputMatrix[timeStep-1]
        except IndexError:
            self.outputGroup.state = np.zeros(self.outputGroup.nbUnits)
        super(StaticInput, self)._execute(timeStep)
        
    def _saveddata(self):
        
        savedData = super(StaticInput, self)._saveddata()
        savedData.update({'inputMatrix': self.inputMatrix})
        return savedData

class NoiseGenerator(InputGroup):
    """NoiseGenerator"""
    
    def __init__(self,
                 distribution='normal',
                 parameters=None,
                 seed=None,
                 *args, **kwargs):
        
        super(NoiseGenerator, self).__init__(*args, **kwargs)
        
        distributionList = ['uniform','normal']
        try:
            self.distribution = checkIfInOptionList(distribution,
                                                    distributionList)
        except TypeError:
            msg = 'argument "distribution" must be one of these options : '
            msg += distributionList
            raise Exception, msg
            
        try:
            self.parameters = typeAndSize(parameters, dict, 2)
        except Exception:
            msg = 'argument "parameters" must be a dictionary with two elements'
            raise Exception, msg
        
        if distribution == 'uniform':
            try:
                self.min = parameters['min']
                self.max = parameters['max']
                self.weightsRange = [self.min, self.max]
            except KeyError:
                msg = 'When using the uniform distribution, you must set '
                msg += 'parameters dictionary with two keys: min and max'
                raise Exception, msg
            self._execute_dist = self._execute_uniform
            
        elif distribution == 'normal':
            try:
                self.mu = parameters['mu']
                self.sigma = parameters['sigma']
            except KeyError:
                msg = 'When using the normal distribution, you must set '
                msg += 'parameters dictionary with two keys: mu and sigma'
                raise Exception, msg
            self._execute_dist = self._execute_normal
            
        self.seed = seed
    
    def get_nbtimesteps(self):
        
        return 0
    
    def _initialize(self):
        
        self._execute_dist()
        super(NoiseGenerator, self)._initialize()
    
    def _setting_seed(self, added_to_seed):
        
        if self.seed is not None:
            np.random.seed(self.seed + added_to_seed)
    
    def _execute(self, timeStep):
        
        self._setting_seed(timeStep)
        self._execute_dist()
        super(NoiseGenerator, self)._execute(timeStep)
    
    def _execute_uniform(self):
        
        self.outputGroup.state = np.random.uniform(self.min,
                                                   self.max,
                                                   self.outputGroup.nbUnits)
        
    def _execute_normal(self, timeStep):
        
        self.outputGroup.state = np.random.normal(self.mean,
                                                  self.std_deviation,
                                                  self.outputGroup.nbUnits)
    
    def __getitem__(self, item):
        # Return the state of the units
        return self.outputGroup.__getitem__(item)
    
    def _saveddata(self):
        
        savedData = super(NoiseGenerator, self)._saveddata()
        savedData.update({'distribution': self.distribution,
                          'parameters': self.parameters,
                          'seed': self.seed})
        return savedData

#class DynamicInput(InputGroup):
#    """DynamicInput is a group whose output depends on another group (argument
#    inputGroup).
#    The dynamic_behavior function must be manually filled to have the expected
#    dynamic behavior.
#    """
#    
#    def __init__(self, inputGroup, *args, **kwargs):
#        
#        self.inputGroup = inputGroup
#        
#        super(DynamicInput,self).__init__(*args, **kwargs)
#        
#    def _initialize(self, deltat=None):
#        
#        self.output = np.zeros(self.shape)
#        
#    def dynamic_behavior(self, timeStep):
#        pass #To be completed for dynamic behavior depending on input group
#    
#    def get_nbtimesteps(self):
#        
#        return None
#    
#    def _execute(self, timeStep):
#        
#        self.dynamic_behavior(timeStep)
#        
#    def _saveddata(self):
#        
#        savedData = super(DynamicInput, self)._saveddata()
#        savedData.update({'inputGroup': self.inputGroup.name})
#        return savedData
