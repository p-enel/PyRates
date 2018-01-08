'''
Created on 17 fevr. 2011

@author: pier
'''

from __future__ import division
#from pyrates.groups.inputgroups import DynamicInput
from pyrates.simobjects.nodes.node import Node
import numpy as np

#__all__ = ["TaskNode", "TaskNode2targets", "TaskNode4targets", "RealTaskNode"]
__all__ = ["RealTaskNode"]

def generateBlocks(nbTrialsPerBlock=0, blockList=[]):
    
    session = []
    for block in blockList:
        session.append(block*nbTrialsPerBlock)
    return session

#class TaskNode(DynamicInput):
#    pass
#
#class TaskNode2targets(TaskNode):
#    '''
#        nbTSFPT = number of time steps during fixation point presentation
#        nbTST = number of time steps during targets presentation
#        nbTSDelay = number of time steps during during delay
#        sessionBlocks = a list containing the rewarded target number        
#    '''
#    
#    
#    def __init__(self,
#                 inputGroup=None,
#                 nbTSFPT=0,
#                 nbTST=0,
#                 nbTSDelay=0,
#                 shape=(7,7),
#                 sessionBlocks=None,
#                 *args, **kwargs):
#        
#        super(TaskNode2targets, self).__init__(inputGroup=inputGroup,
#                                               shape=shape,
#                                               *args, **kwargs)
#        
#        # Initializing parameters of the task
#        self.nbTSFPT = nbTSFPT
#        self.nbTST = nbTST
#        self.nbTSDelay = nbTSDelay
#        self.shape = shape
#        self.sessionBlocks = sessionBlocks
#        self.nbSteps = len(sessionBlocks) * (nbTSFPT + nbTST + nbTSDelay)
#        
#        # the changeWeightCondition attribute is a boolean that is checked at every timestep to know if the DAweights must be changed or not
#        self.changeWeightCondition = False
#        
#        # Initializing targets output
#        self.targetsOut = np.zeros(self.shape)
#        self.targetsOut[1,1] = 1
#        self.targetsOut[1,3] = 1
#        self.targetsOut = self.targetsOut.flatten()
#        
#        # Initializing delay output
#        self.delayOutput = np.zeros(self.shape)
#        self.delayOutput = self.delayOutput.flatten()
#    
#    def _initialize(self, deltat=None):
#        
#        self.state = 'T'
#        self.iteration = 0
#        self.choice = None
#        self.done = False
#        self.rewardedT = self.sessionBlocks.pop(0)
#        self.output = self.targetsOut
##        self.FPT = np.zeros(self.shape)
##        self.FPT[3,3] = 1
##        self.FPT[3,1] = 1
##        self.FPT[3,5] = 1
#        
#    def _execute(self):
##        if self.state == 'FPT':
##            if self.iteration < self.nbTSFPT:
##                self.output = self.FPT
##            else:
##                self.state = 'T'
##                self.iteration = 0
##                self.output = self.T
#        '''
#        Target period: targets are presented, at the end of the presentation
#        the highest unit in the input to the task node (e.g. Str) is considered
#        to be the choice
#        '''        
#        if self.state == 'T':
#            if self.iteration < self.nbTST and not self.choice:
#                self.output = self.targetsOut
#            else:
#                self.choice = self.get_choice_from_str()
#                if self.choice == self.rewardedT:
#                    self.reward = True
#                else:
#                    self.reward = False
#                self.state = 'delay'
#                self.iteration = 0
#                self.output = self.delayOutput
#        ## Delay period        
#        else:
#            if self.iteration < self.nbTSDelay:
#                self.output = self.delayOutput
#                self.choice = None
#            else:
#                if self.sessionBlocks == []:
#                    self.done = True
#                else:
#                    self.rewardedT = self.sessionBlocks.pop(0)
#                    self.state = 'T'
#                    self.iteration = 0
#                    self.output = self.targetsOut
#        
#        if self.choice is not None:
#            self.changeWeightCondition = True
#        else:
#            self.changeWeightCondition = False
#        
#        self.iteration += 1
#    
#    def get_choice_from_str(self):
##        left -> 22
##        right -> 26
#        return np.argmax(self.inputGroup.output)
##    _saveddata for this class should be only to retrieve informations from the node but not save evolution of the node...  
##    def _saveddata(self):
##        saved_object = super(TaskNode2targets, self)._saveddata()
##        saved_object.update({'rewardedTarget' : self.rewardedT})
##        return saved_object
#    
#class TaskNode4targets(TaskNode):
#    
#    
#    def __init__(self, inputGroup=None,
#                 nbTSFPT=0,
#                 nbTST=0,
#                 nbTSDelay=0,
#                 shape=(5, 5),
#                 sessionBlocks=None,
#                 *args, **kwargs):
#        
#        super(TaskNode4targets, self).__init__(inputGroup=inputGroup, shape=shape, *args, **kwargs)
#        
#        # Initializing parameters of the task
#        self.nbTSFPT = nbTSFPT
#        self.nbTST = nbTST
#        self.nbTSDelay = nbTSDelay
#        self.shape = shape
#        self.sessionBlocks = sessionBlocks
#        self.nbSteps = len(sessionBlocks) * (nbTSFPT + nbTST + nbTSDelay)
#        
#        # the changeWeightCondition attribute is a boolean that is checked at every timestep to know if the DAweights must be changed or not
#        self.changeWeightCondition = False
#        
#        # Initializing targets output
#        self.targetsOut = np.zeros(self.shape)
#        self.targetsOut[1, 1] = 1
#        self.targetsOut[1, 3] = 1
#        self.targetsOut[3, 1] = 1
#        self.targetsOut[3, 3] = 1
#        
#        self.targetsOut = self.targetsOut.flatten()
#        
#        # Initializing delay output
#        self.delayOutput = np.zeros(self.shape)
#        self.delayOutput = self.delayOutput.flatten()
#    
#    def _initialize(self, deltat=None):
#        
#        self.state = 'T'
#        self.iteration = 0
#        self.choice = None
#        self.done = False
#        self.rewardedT = self.sessionBlocks.pop(0)
#        self.output = self.targetsOut
##        self.FPT = np.zeros(self.shape)
##        self.FPT[3,3] = 1
##        self.FPT[3,1] = 1
##        self.FPT[3,5] = 1
#        
#    def _execute(self):
##        if self.state == 'FPT':
##            if self.iteration < self.nbTSFPT:
##                self.output = self.FPT
##            else:
##                self.state = 'T'
##                self.iteration = 0
##                self.output = self.T
#
#        ## Target period: targets are presented, at the end of the presentation, the highest unit in the input to the task node (e.g. Str) is
#        ## considered as the choice
#        if self.state == 'T':
#            if self.iteration < self.nbTST and not self.choice:
#                self.output = self.targetsOut
#            else:
#                self.choice = self.get_choice_from_str()
#                if self.choice == self.rewardedT:
#                    self.reward = True
#                else:
#                    self.reward = False
#                self.state = 'delay'
#                self.iteration = 0
#                self.output = self.delayOutput
#        ## Delay period        
#        else:
#            if self.iteration < self.nbTSDelay:
#                self.output = self.delayOutput
#                self.choice = None
#            else:
#                if self.sessionBlocks == []:
#                    self.done = True
#                else:
#                    self.rewardedT = self.sessionBlocks.pop(0)
#                    self.state = 'T'
#                    self.iteration = 0
#                    self.output = self.targetsOut
#        
#        if self.choice is not None:
#            self.changeWeightCondition = True
#        else:
#            self.changeWeightCondition = False
#        
#        self.iteration += 1
#    
#    def get_choice_from_str(self):
#        
##        left -> 22
##        right -> 26
#        return np.argmax(self.inputGroup.output)
##    _saveddata for this class should be only to retrieve informations from the node but not save evolution of the node...  
##    def _saveddata(self):
##        saved_object = super(TaskNode2targets, self)._saveddata()
##        saved_object.update({'rewardedTarget' : self.rewardedT})
##        return saved_object

class RealTaskNode(Node):
    
    
    def __init__(self,
                 outputNode=None,
                 inputNode=None,
                 *args, **kwargs):
        
        super(RealTaskNode, self).__init__(*args, **kwargs)
        self.outputNode = outputNode
        self.inputNode = inputNode
        
    def _execute(self, timeStep):
        pass

    def _initialize(self):
        pass
    
    def get_nbtimesteps(self):
        return None
        
    def _saveddata(self):
        
        savedData = super(RealTaskNode, self)._saveddata()
        savedData.update({'outputNode': self.outputNode.name,
                          'inputNode': self.inputNode.name})
        return savedData
    
    def _register(self, save=True):
        
        self.simulationRef.inputs.append(self)
        super(RealTaskNode, self)._register(save=save)