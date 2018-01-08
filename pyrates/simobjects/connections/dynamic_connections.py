"""Dynamic connection classes

Dynamic connections are connections whose weights are susceptible to change
during the course of the simulation.
  - DynamicConnection: the base class for dynamic connections
  - DAModulatedConnection: .............................

"""
import numpy as np
from connection import Connection

__all__ = ["DynamicConnection", "DAModulatedConnection"]

class DynamicConnection(Connection):
    """Base class for dynamic connections"""
    
    def __init__(self, plasticityFunction=None,
                 dependentObjects=[],
                 *args, **kwargs):

        super(DynamicConnection, self).__init__(*args, **kwargs)
            
        if not isinstance(dependentObjects,list):
            raise TypeError, 'dependentObjects must be a list'
        
        self.dependentObjects = dependentObjects
        self.plasticityFunction = plasticityFunction
    
    def _execute(self, timeStep):
        
        self.plasticityFunction()
        super(DynamicConnection, self)._execute(timeStep)
        
    def _saveddata(self):
        
        saved_object = super(DynamicConnection, self)._saveddata()
        saved_object.update({'dependentObjects': self.dependentObjects})
        return saved_object
    
class DAModulatedConnection(DynamicConnection):
    """Dopamine modulated connection
    
    Weights between sending and receiving layers are modified depending on the
    reward contingency and the activity of the sending and receiving layers
    neurons.
    
    Several parameters can be changed, the class cannot be used just as is
    
    Arguments:
    - taskNode: the object of the simulation that contain the reward
        contingency information
    """
    def __init__(self,
                 C1=0.00001,
                 inputThreshold=None,
                 taskNode=None,
                 posReinforcement=0.5,
                 negReinforcement=-0.5,
                 *args, **kwargs):
        
        super(DAModulatedConnection, self).__init__(plasticityFunction=self._da_function,
                                                    *args, **kwargs)
        self.taskNode = taskNode
        self.weightsSum = np.sum(self.weights)
        self.inputThreshold = inputThreshold
        self.C1 = C1
        self.sendGrpActivity = np.zeros(self.sendingGroup.shape).flatten()
        self.recGrpActivity = np.zeros(self.receivingGroup.shape).flatten()
        self.posReinforcement = posReinforcement
        self.negReinforcement = negReinforcement
        
    def _initialize(self, deltat=None):
        
        super(DAModulatedConnection, self)._initialize(deltat=deltat)
        self.sendGrpActivity = self.sendingGroup.output
        self.recGrpActivity = self.receivingGroup.output
        self.DAModulation = 1
    
    def _execute(self, timeStep):
        
        super(DAModulatedConnection, self)._execute(timeStep)
        
        '''Here is applied a normalization mechanism to avoid an over
        stimulation of caudate neurons. DAModulation will be inferior to 1 if
        the input the caudate receives are to high, thus decreasing the weights.
        Otherwise DAModulation is 1 and the weights are kept as they are.
        '''
        if np.max(self.output) > self.inputThreshold:
            self.DAModulation = self.inputThreshold / np.max(self.output)
        else:
            self.DAModulation = 1
        
        self.output = self.output * self.DAModulation
    
    def _da_function(self):
        
        self.sendGrpActivity = self.sendGrpActivity * 0.9 + self.sendingGroup.output * 0.1
        self.recGrpActivity = self.recGrpActivity * 0.9 + self.receivingGroup.output * 0.1
        if self.taskNode.changeWeightCondition:
            self._update_weights(self.taskNode.reward)
    
    def _update_weights(self, reward):
        '''Function called after a trial to modify connections depending on the
        reward contingency.
        '''
        
        '''Depending on reward contingency, dopamine activity is either lowered
        or strengthened'''
        if reward:
            dopamineActivity = self.posReinforcement
        else:
            dopamineActivity = self.negReinforcement
        
        SGShape = [self.sendingGroup.nbUnits]
        SGShape.insert(0, 1)
        RGShape = [self.receivingGroup.nbUnits]
        RGShape.append(1)
        
        '''FiFjProduct represents the product of the activities of IT neurons and
        caudate neurons'''
        FiFjProduct = np.dot(self.recGrpActivity.reshape(RGShape), self.sendGrpActivity.reshape(SGShape)) * (self.weights != 0)
        
        '''New weigths are computed based on:
            - FiFjProduct: the recent activity of IT and caudate neurons, the
                neurons that supposedly participated to make the choice
            - DAModulation: that avoid too high activity in caudate
            - dopamineActivity: the brief change in dopamine activity that
                depends on the reward contingency
            - C1: a constant that defines how much the weights should be
                modified, this constant is adapted to this particular task
        '''
        self.newWeights = self.weights + self.DAModulation * dopamineActivity * self.C1 * FiFjProduct
        
        '''Here the weights are kept between the bounds of 0 and 1. So if a
        weight is lower than zero after modification, it is set to zero and if
        higher than one, set to one.
        '''
        self.newWeights = self.newWeights * (self.newWeights > 0) * (self.newWeights < 1) + (self.newWeights >= 1) * 1
        
        '''Normalization of the weights for each neuron: one neuron should have
        the same weights so when a weight is strengthened other weights should
        be weakened. Conversely, if some weights are weakened, other weights are
        strengthened.'''
        for j in range(self.newWeights.shape[0]):
            self.newWeights[:,j] = self.newWeights[:,j] * np.sum(self.newWeights[:,j])/ np.sum(self.weights[:,j])
        
    def _saveddata(self):
        
        savedData = super(DAModulatedConnection, self)._saveddata()
        savedData.update({'plasticityFunction': 'DAFunction'})
        return savedData
        

