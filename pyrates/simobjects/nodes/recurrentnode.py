# -*- coding: utf-8 -*-
"""
Created on 12 janv. 2012

@author: pier
"""

import numpy as np
from pyrates.simobjects.connections.connection import Connection
from pyrates.simobjects.nodes.node import Node

__all__ = ['RecurrentNode']

class RecurrentNode(Node):
    
    
    def __init__(self,
                 groupClass,
                 name=None,
                 groupArgs={},
                 connectionClass=Connection,
                 connectionArgs={},
                 weightMatrix=None,
                 *args, **kwargs):
        
        groupArgs['save'] = False
        groupArgs['parentNode'] = self
        
        if 'name' not in groupArgs:
            if name is not None:
                groupArgs['name'] = name + 'RecurrentGroup'
            else:
                groupArgs['name'] = 'recurrentGroup'
            
        self.recGroup = groupClass(**groupArgs)
        
        if 'name' not in connectionArgs:
            if name is not None:
                connectionArgs['name'] = name + 'RecurrentConnection'
            else:
                connectionArgs['name'] = 'recurrentConnection'
        
        connectionArgs['save'] = False
        connectionArgs['sendingObj'] = self.recGroup
        connectionArgs['receivingObj'] = self.recGroup
        connectionArgs['weightMatrix'] = weightMatrix
        
        self.weightMatrix = weightMatrix
        
        self.recConnection = connectionClass(**connectionArgs)
        
        super(RecurrentNode, self).__init__(name=name,
                                            inputGroup=self.recGroup,
                                            outputGroup=self.recGroup,
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
    
    def _saveddata(self):
        
        savedData = super(RecurrentNode, self)._saveddata()
        savedData.update({'recGroup': self.recGroup._saveddata(),
                          'connection': self.recConnection._saveddata()})
        return savedData