
from __future__ import division
from pyrates.simobjects.connections.connection import StaticConnection
from pyrates.simobjects.groups.unitgroups import LeakyIntegrator
from pyrates.simobjects.simulation_object import SimulationObject
from pyrates.utils.activation_functions import Tanh

__all__ = ["Reservoir", "LeakyNeuronsReservoir"]

class Reservoir(SimulationObject):
    
    
    def __init__(self,
                 unitGroup,
                 connection,
                 weightMatrix=None,
                 *args, **kwargs):
        
        self.unitGroup = unitGroup
        self.connection = connection
        self.weightMatrix = weightMatrix
        self.nbUnits = unitGroup.nbUnits
        self.shape = unitGroup.shape
        super(Reservoir, self).__init__(*args, **kwargs)
    
    def _saveddata(self):
        
        savedData = super(Reservoir, self)._saveddata()
        savedData.update({'unitGroup': self.unitGroup._saveddata(),
                          'connection': self.connection._saveddata(),
                          'weightMatrix': self.weightMatrix})
        return savedData
    
class LeakyNeuronsReservoir(Reservoir):
    
    
    def __init__(self,
                 name=None,
                 shape=None,
                 nbUnits=None,
                 tau=None,
                 tauStep=None,
                 activationClass=Tanh,
                 activationParams=None,
                 weightMatrix=None,
                 **kwargs):
        
        if name is not None:
            unitgroupName = name + '_unitgroup'
            connectionName = name + '_connection'
        else:
            unitgroupName = None
            connectionName = None
        
        self.reservoirGroup = LeakyIntegrator(name=unitgroupName,
                                              shape=shape,
                                              nbUnits=nbUnits,
                                              tau=tau,
                                              tauStep=tauStep,
                                              activationClass=activationClass,
                                              activationParams=activationParams,
                                              save=False,
                                              **kwargs)
        
        self.recurrentConnections = StaticConnection(self.reservoirGroup,
                                                      self.reservoirGroup,
                                                      name=connectionName,
                                                      weightMatrix=weightMatrix,
                                                      save=False)
        
        super(LeakyNeuronsReservoir,self).__init__(self.reservoirGroup,
                                                   self.recurrentConnections,
                                                   name=name,
                                                   weightMatrix=weightMatrix)
