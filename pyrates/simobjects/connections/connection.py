"""Base class and static connection.

A Connection can be made between to groups only. To connect other types of
simulation objects, you must passed the objects as attributes or arguments
between objects.

This module defines the classes:
  - Connection: the base class for all the connections.
  - StaticConnection: a type of connection whose weight matrix won't change
    during the course of the simulation.
"""

# Standard imports
from __future__ import division
import numpy as np

# Local imports
from pyrates.simobjects.simulation_object import MonitoredObject
from pyrates.simobjects.groups.groups import Group
from pyrates.core.units import Distance, Speed, Time, TimeStep, time2tstep, mm
from pyrates.utils.common_methods import check_argument_type

__all__ = ["Connection", "StaticConnection"]

class Connection(MonitoredObject):
    """Base class for all connection classes.
    A connection connects two groups together with a weight matrix.
    
    Arguments:
    - sendingObj: connections are one-way, this argument is for the object that
        contain an output group of neurons
    - receivingObj: the object that contains the receiving group of neuron
    - weights: the weight matrix between these two groups
    - distance: the distance in meters (m) or timeStep
    - speed: if the distance is given in meters, the speed is in m/s
    - delay: is expressed in number of time steps for the information to travel
        down the connection
    """
    
    nodeLink = None
    
    def __init__(self,
                 sendingObj,
                 receivingObj,
                 weightMatrix=None,
                 distance=0*mm,
                 speed=None, # 10 m/s for cortico-cortical connections?
                 delay=None,
                 *args, **kwargs):
        
        (self.sendingGroup,
         self.receivingGroup) = self.check_connection_args(sendingObj,
                                                           receivingObj)

        self.sendingNode = self.sendingGroup.parentNode
        self.receivingNode = self.receivingGroup.parentNode
        
        check_argument_type(distance, [Distance], "distance")
        if speed is not None:
            check_argument_type(speed, [Speed], "speed")
        if delay is not None:
            check_argument_type(delay, [Time, TimeStep], "delay")
        
        if distance > 0 and speed is None:
            raise Exception, 'If you specify a distance make sure to specify '+\
                'a speed as well!'
        elif speed is not None and delay is not None:
            raise Exception, 'You cannot specify a speed AND a delay!'
        
        self.distance = distance
        self.speed = speed
        self.delay = delay
        
        self.shape = [self.receivingGroup.shape[0] * \
                      self.receivingGroup.shape[1],
                      self.sendingGroup.shape[0] * self.sendingGroup.shape[1]]
        
        if weightMatrix is None:
            self.weights = np.zeros((self.receivingGroup.nbUnits,
                                          self.sendingGroup.nbUnits))
        else:
            if not isinstance(weightMatrix, np.ndarray):
                raise Exception, 'argument weights argument for '\
                + 'constructor Connection() must be a numpy array'
            elif weightMatrix.shape != (self.receivingGroup.nbUnits,
                                        self.sendingGroup.nbUnits):
                raise Exception, 'size of weights argument for '\
                + 'constructor Connection() must agree with the dimensions of '\
                + 'the NeuronGroup passed as argument'
            else:
                self.weights = weightMatrix
        
        super(Connection, self).__init__(*args, **kwargs)
    
    def get_weights_range(self):
        """Should be overridden if these default values are not true anymore"""
        return [0, 1]
    
    def check_connection_args(self, sendingObj, receivingObj):
        """Check if the two main arguments of Connection can actually make a
        connection: do the nodes have the groups required to make connection.
        """
        msg = 'sendingObj %s of a connection must be a group ' % str(sendingObj)
        msg += 'or a Node with a group as output' 
        if issubclass(type(sendingObj), self.nodeLink):
            try:
                sendingGrp = sendingObj.outputGroup
            except AttributeError:
                raise TypeError, msg
        elif not issubclass(type(sendingObj), Group):
            raise TypeError, msg
        else:
            sendingGrp = sendingObj
        
        msg = 'receivingObj %s of a connection must be a group ' % str(receivingObj)
        msg += 'or a Node with a group as output'
        if issubclass(type(receivingObj), self.nodeLink):
            try:
                receivingGrp = receivingObj.outputGroup
            except AttributeError:
                raise TypeError, msg
        elif not issubclass(type(receivingObj), Group):
            raise TypeError, msg
        else:
            receivingGrp = receivingObj
        
        return sendingGrp, receivingGrp
    
    def default_monitored(self):
        # The default monitored variable is the output of the connection which
        # correspond to the weighted inputs of the sending group
        return ['weights']
    
    def monitorable(self):
        '''Return the list of variable that can be monitored'''
        return ['weights','output']
    
    def __getitem__(self, item):
        
        return self.weights[item]
    
    def _initialize(self, deltat=None):
        
        if self.speed is not None:
            if deltat is None:
                errMsg = "If you want to use speed of connection a deltat must"
                errMsg +="be specified with set_deltat() or with run()"
                raise ValueError, errMsg
            else:
                self.delay = self.distance / self.speed
        
        if issubclass(type(self.delay), Time):
            self.delay = time2tstep(self.delay, whoAsk=self.name)
        
        if self.delay is not None:
            self.buffer = [np.zeros(self.sendingGroup.nbUnits) \
                           for i in range(self.delay )]
        else:
            self.buffer = []
        
        self.buffer.append(self.sendingGroup.output)
        self.output = np.dot(self.weights, self.buffer.pop(0))
    
    def _execute(self, timeStep):
        '''Basic execution of a connection.
        Store the last output of the sending group in the delay queue and 
        compute the output of the connection as the dot product of the first
        element in the delay queue and the weight matrix of the connection.
        '''
        self.buffer.append(self.sendingGroup.output)
        self.output = np.dot(self.weights, self.buffer.pop(0))
    
    def _saveddata(self):

        savedData = super(Connection, self)._saveddata()
        savedData.update({'sendingGroup': str(self.sendingGroup),
                          'receivingGroup': str(self.receivingGroup),
                          'initialWeights': self.weights,
                          'weightsRange': self.get_weights_range(),
                          'object_type': 'connection'})
        
        return savedData
    
    def _register(self, save=True):
        self.simulationRef.connections.append(self)
        self.receivingGroup._add_connection(self)
        super(Connection, self)._register(save=save)

class StaticConnection(Connection):
    '''Static connection class that must be inherited by subclasses whose weight
    matrix will not be modified during a simulation run.
    '''
    def __init__(self, *args, **kwargs):
        
        super(StaticConnection, self).__init__(*args, **kwargs)
