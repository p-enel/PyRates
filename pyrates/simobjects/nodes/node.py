# -*- coding: utf-8 -*-
"""
The Node is the base class for simulation objects. A Node has a maximum of one
input group and one output group. It may have incoming and/or outgoing
connections made with the input/output groups.
"""

# Local imports
from pyrates.simobjects.simulation_object import SimulationObject

__all__ = ["Node", "SingleGrpNode"]

class Node(SimulationObject):
    '''Basic class for nodes, must be overridden'''
    
    def __init__(self,
                 inputGroup=None,
                 outputGroup=None,
                 *args, **kwargs):
        
        self.inputGroup = inputGroup
        self.outputGroup = outputGroup
        
        if 'groups' not in dir(self):
            self.groups = []
        if inputGroup is not None and inputGroup not in self.groups:
            self.groups.append(inputGroup)
        if outputGroup is not None and outputGroup not in self.groups:
            self.groups.append(outputGroup)
        
        super(Node, self).__init__(*args, **kwargs)
    
    def _initialize(self):
        '''Must be overridden'''
        raise NotImplementedError
    
    def _saveddata(self):
        
        savedData = super(Node, self)._saveddata()
        if self.outputGroup is not None:
            savedData.update({'outputGroup': str(self.outputGroup)})
        elif self.inputGroup is not None:
            savedData.update({'inputGroup': str(self.inputGroup)})
        
        return savedData
    
    def _register(self, save=True):
        
        self.simulationRef.nodes.append(self)
        super(Node, self)._register(save=save)
    
class SingleGrpNode(Node):
    '''This type of Node was developed to encapsulate single groups in a Node. 
    '''
    def __init__(self, group=None, *args, **kwargs):
        
        self.singleGroup = group
        super(SingleGrpNode, self).__init__(inputGroup=group,
                                            outputGroup=group,
                                            *args, **kwargs)

    def _initialize(self):
        self.singleGroup._initialize()
        
    def _execute(self, timeStep):
        
        self.singleGroup._execute(timeStep=timeStep)

