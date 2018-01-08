'''
In this module the base class group is defined. A group is a simulation object
that contains units that have outputs which will change during the course of a
simulation.
Group is the base class of all the different groups.
'''
# Standard import
import numpy as np

# Local import
from pyrates.simobjects.simulation_object import MonitoredObject

__all__ = ["Group"]

class Group(MonitoredObject):
    """Base class of all groups
    
    A group is a simulation object that contains units that have outputs which
    change during the course of a simulation. In this class are defined the
    common arguments and methods that all groups inherit.
    
    Initial arguments:
    - shape: the shape of the group, must be a 'list' or 'tuple' containing
             'int' elements - e.g. (5, 10) will create a group of 50 units
             with shape (5, 10).
    - nbUnits: the number of units in the group, must be an 'int'. It does not
               need to be defined if shape is defined, otherwise must it must
               be consistent with the number of units specified by the shape.
    - weightsRange: a 2-elts list with the lowest and highest values that the
        output can take. Important for visualization purpose only.
    - parentNode: the parent node containing the newly created group. If no
        parent node is created, one will be automatically created.
    """
    
    singleGrpNodeLink = None
    
    def __init__(self,
                 shape=None,
                 nbUnits=None,
                 outputRange=None,
                 parentNode=None,
                 *args, **kwargs):
        
        self.shape, self.nbUnits = check_shape_nbunits(shape, nbUnits)
        
        if parentNode is not None:
            self.parentNode = parentNode
        else:
            parentNodeKwargs = {}
            if 'name' in kwargs:
                parentNodeKwargs['name'] = kwargs['name'] + 'ParentNode'
            if 'register' in kwargs:
                parentNodeKwargs['register'] = kwargs['register']
            if 'save' in kwargs:
                parentNodeKwargs['save'] = kwargs['save']
            sgGrpNode = Group.singleGrpNodeLink(group=self,
                                                **parentNodeKwargs)
            self.parentNode = sgGrpNode
        
        self.output = np.zeros(self.nbUnits)
        
        self.weightsRange = outputRange
        
        self.simulationRef.groups.append(self)
        
        super(Group, self).__init__(*args, **kwargs)
        self.incoming_Cs = []
    
    def default_monitored(self):
        return ['output']
    
    def monitorable(self):
        '''Return the list of variable that can be monitored'''
        return ['output', 'input']
    
    def _initialize(self):
        """ Set parameters before running the simulation.
        
        This method needs to be overridden by subclasses in some cases. 
        """
        self._add_up_inputs()
#        super(Group, self)._initialize()
#        if self.isMonitored:
#            if 'output' in self.monitoredVars:
#                self.monitorData['output'] = np.zeros((self.nbTimeSteps + 1,
#                                                       self.nbUnits))
#                self.monitorData['output'][0] = self.output
#                
#            if 'input' in self.monitoredVars:
#                self.monitorData['input'] = np.zeros((self.nbTimeSteps + 1,
#                                                      self.nbUnits))
#                self.monitorData['input'][0] = np.zeros((1, self.nbUnits))
            
    def _execute(self, timeStep):
        """ Compute the new output of the group
        
        This method has to be overridden by the subclasses of Group. This
        method computes the new output of the group.
        """
        raise NotImplementedError
        
    def _add_connection(self, connection):
        
        self.incoming_Cs.append(connection)
    
    def _add_up_inputs(self):

        self.input = np.zeros(self.nbUnits)
        for connection in self.incoming_Cs:
            self.input += connection.output
    
    def get_incoming_cs_names(self):
        '''Returns the incoming connections of the group'''
        outputList = []
        for element in self.incoming_Cs:
            outputList.append(element.name)
        return outputList
    
    def set_state(self, state=None):
        # The default option without providing an argument will reset the units state to zero
        if state is not None:
            if isinstance(state, int) or isinstance(state, float):
                self.state[:] = state
            elif isinstance(state, np.ndarray):
                if state.shape != self.shape:
                    raise Exception, 'The shape of the new state must have the shape of the group'
                else:
                    self.state = state
            else:
                raise TypeError, 'state argument of function set_state must be either an integer, float or ndarray'
        else:
            self.state = np.zeros(self.nbUnits)
            
    def set_output(self, output = None):
        # The default option without providing an argument will reset the units output to zero
        if output is not None:
            if isinstance(output, int) or isinstance(output, float):
                self.output[:] = output
            elif isinstance(output, np.ndarray):
                if output.shape != self.shape:
                    raise Exception, 'The shape of the new state must have the shape of the group'
                else:
                    self.output = output
            else:
                raise TypeError, 'state argument of function set_state must be either an integer, float or ndarray'
        else:
            self.output = np.zeros(self.nbUnits)
    
    def _saveddata(self):
        """Save name and shape of the group"""
        savedData = super(Group, self)._saveddata()
        savedData.update({'nbUnits': self.nbUnits,
                          'shape': self.shape,
                          'weightsRange': self.weightsRange,
                          'object_type': 'group',
                          'incoming_Cs': self.get_incoming_cs_names()})
        
        return savedData
    
#    def _register(self, save=True):
#        self.simulationRef.groups.append(self)
#        super(Group, self)._register(save=save)
    
    def __getitem__(self, item):
        """Return the state of the units"""
        return self.output.reshape(self.shape)[item]
    
def check_shape_nbunits(shape, nbUnits):
    
    if shape is None and nbUnits is None:
        raise Exception, 'A shape or number of units must be specified'
    elif shape is not None:
        nbUnitsFromShape = 1
        for i in shape:
            nbUnitsFromShape *= i
        if nbUnits is not None and nbUnitsFromShape is not nbUnits:
            raise Exception, 'The number of units specified is not congruent with the shape specified'
        else:
            nbUnits = nbUnitsFromShape
    else:
        shape = [1, nbUnits]
    
    return shape, nbUnits