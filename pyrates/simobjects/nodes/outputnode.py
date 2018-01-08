'''
Created on 9 nov. 2011

@author: pier
'''

from pyrates.simobjects.nodes.node import Node

__all__ = ["OutputNode"]

class OutputNode(Node):
    
    
    def __init__(self, inputGroup=None, *args, **kwargs):
        
        super(OutputNode, self).__init__(inputGroup=inputGroup,
                                         *args, **kwargs)
        self.output = None
        self.checkInputStatus = True
    
    def set_check_input_status(self, b):
        
        self.checkInputStatus = b
    
    def _initialize(self):
        
        self.deltat = self.simulationRef.deltat
        self.outputHistory = []
    
    def _execute(self, timeStep):
        
        if self.checkInputStatus:
            self.check_input(timeStep)
            if self.output != None:
                outputTime = timeStep * self.deltat
                self.outputHistory.append([self.output, timeStep, outputTime])
        else:
            self.output = None
    
    def check_input(self, timeStep):
        # This function must be overridden in order to check if the input group state allows to generate an output
        pass
    
    def _saveddata(self):
        
        savedData = super(OutputNode, self)._saveddata()
        savedData.update({'inputGroup': self.inputGroup.name,
                          'output': self.outputHistory})
        return savedData
