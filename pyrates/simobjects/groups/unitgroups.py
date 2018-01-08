'''
This module contains more elaborated group classes.

Classes:
- IdentityGroup: output is equal to input and group has no input
- ActivatedGroup: with output being the results of the state through an
                  activation function
- LeakyIntegrator: input to the group is integrated over time with a leaky
                   integrator
- OgerLikeLeakyNeurons: leaky neurons as defined in the Oger toolbox
'''

# Standard imports
from __future__ import division
import numpy as np

# Local imports
from pyrates.utils.common_methods import typeAndSize
from groups import Group

__all__ = ["IdentityGroup", "ActivatedGroup",
           "LeakyIntegrator"]#, "OgerLikeLeakyNeurons"]
    
class IdentityGroup(Group):
    """UG where output is equal to state and UG has no input
    
    Methods:
    - usual methods (see Group class for more details)
    """
    
    def __init__(self, *args, **kwargs):
        
        super(IdentityGroup, self).__init__(*args, **kwargs)
        
    def _initialize(self):
        
        self.output = self.state
        super(IdentityGroup, self)._initialize()
        
    def _execute(self, timeStep):
        
        self.output = self.state
    
class ActivatedGroup(Group):
    """UG where the output is the result of the state through an activation
    function
    
    Initial arguments:
    - activationClass: a class containing an activation function
    - activationParams: the parameters of the activation function
    
    Methods:
    - usual group methods (see Group class for more details)
    """
    def __init__(self,
                 activationClass=None,
                 activationParams=None,
                 *args, **kwargs):
        
        super(ActivatedGroup, self).__init__(*args, **kwargs)
        
        self.state = np.zeros(self.nbUnits)
        
        self.activationParams = activationParams
        self.activationFunction = activationClass.get_function(activationParams)
        self.activationFunctionName = activationClass.name
        self.weightsRange = activationClass.get_output_range(activationParams)
    
    def monitorable(self):
        monitorable = super(ActivatedGroup, self).monitorable()
        monitorable.append('state')
        return monitorable
    
    def _initialize(self):
        
        self.output = self.activationFunction(self.state)
        super(ActivatedGroup, self)._initialize()
    
    def _execute(self, timeStep):
        """Compute the output with the integration of the state with the
        activation function.
        """
        self.output = self.activationFunction(self.state)
    
    def _saveddata(self):
        
        savedData = super(ActivatedGroup, self)._saveddata()
        savedData.update({'activationFunction': self.activationFunctionName,
                          'activationParams': self.activationParams})
        
        return savedData


class LeakyIntegrator(ActivatedGroup):
    """Leaky integrator group
    
    See the execute function for more detail of the leaky mechanism implemented
    
    Initial arguments:
    - tau: time constant of the leaky integration in milliseconds
    - tauStep: time constant of the leaky integration in time steps
    - restingState: state of the group when the are no inputs 
    
    Methods
    - usual group methods (see Group class for more details)
    - set_state: overriden: reset the state to resting_state if no value is specified
    """
    
    def __init__(self,
                 tau=None,
                 tauStep=None,
                 restingState=None,
                 *args, **kwargs):
        
        super(LeakyIntegrator, self).__init__(*args, **kwargs)
        
        # Check tau and tauStep arguments
        if tauStep is not None and tau is not None:
            raise Exception, 'You cant define a time constant "tau" in terms of simulated time and at the same time\na time constant "tauStep" in terms of time_steps'
        if tauStep is None and tau is None:
            raise Exception, 'A time constant must be defined for each NeuronGroup!'
        
        if tau is not None:
            if isinstance(tau, np.ndarray):
                if tau.shape != tuple(self.shape):
                    raise Exception, 'If you want to specify a time constant for each neuron, make sure the matrix has the size of the layer'
                else:
                    tau = tau.flatten()
            elif not isinstance(tau, int) and not isinstance(tau, float):
                raise Exception, 'Tau must be a single number or array of numbers'
            self.tau = tau
            self.tauStep = None

        else:
            if isinstance(tauStep, np.ndarray):
                if tauStep.shape != self.shape:
                    raise ValueError, 'If you want to specify a time constant for each neuron, make sure the matrix has the size of the layer'
                else:
                    tauStep = tauStep.flatten()
            elif isinstance(tauStep, int) or isinstance(tauStep, float):
                raise Exception, 'Tau_step must be a single number or array of numbers'
            self.tauStep = tauStep
            self.tau = None
        
        # Check resting state argument
        if restingState == None:
            self.restingState = np.zeros(self.nbUnits)
        elif isinstance(restingState, int) or isinstance(restingState, float):
            self.restingState = np.ones(self.nbUnits) * restingState
        elif isinstance(restingState, np.ndarray):
            try:
                self.restingState = (typeAndSize(restingState, np.ndarray, self.shape)).flatten()
            except:
                raise Exception, 'If the resting state is a matrix (each unit has its resting state), be sure the size of the matrix corresponds to the size of the group'
            
        self.state = self.restingState
        
    def _initialize(self):
        """
        Here is defined the time constant in simulated times or in number of steps,
        as only one of them can be defined when creating the NeuronGroup. 
        """
        
        deltat = self.simulationRef.deltat
        if self.tauStep is None:
            if deltat is None:
                raise Exception, 'If you define a time constant tau (in s or ms), you must define a time step "deltat"'
            else:
                self.tauStep = self.tau / deltat
            if isinstance(self.tauStep, np.ndarray):
                minStep = np.min(self.tauStep)
                maxStep = np.max(self.tauStep)
                print "'" + str(self) + "'" + ' has time constants ranging from ' + str(minStep) + ' to ' + str(maxStep) + ' steps'
            else:
                print "'" + str(self) + "'" + ' has a time constant of ' + str(self.tauStep) + ' steps'
        elif self.tau is None and deltat is not None:
            self.tau = self.tauStep * deltat
        super(LeakyIntegrator, self)._initialize()
    
    def _execute(self, timeStep):
        """
        Here is the leaky integration (read 'D' as 'delta'):
                   1                    where m is the membrane potential ('state' variable here) 
        Dm / Dt = --- * (input - m)     t is the time, T is time constant tau
                   T                    
        This differential equation is solved with the Euler method (discretization of time)
        """
        
        deltaState =  (1. / self.tauStep) * (self.input + self.restingState - self.state)
        
        self.state = self.state + deltaState
        super(LeakyIntegrator, self)._execute(timeStep)
        
    def set_state(self, state = None):
        
        if state is None:
            self.state = self.restingState
        else:
            super(LeakyIntegrator, self).set_state(state = state)
            
    def _saveddata(self):
        savedData = super(LeakyIntegrator, self)._saveddata()
        savedData.update({'tau': self.tau,
                          'tauStep': self.tauStep})
        return savedData

# TODO: class OgerLikeLeakyNeurons must be updated
#class OgerLikeLeakyNeurons(ActivatedGroup):
#    """Leaky neuron group as defined in the Oger toolbox
#    
#    Oger: http://reservoir-computing.org/organic/oger
#    OgerLikeLeakyNeurons merge output and state, and weighted input are passed
#    to the activation function before being integrated.
#    
#    Methods:
#    - usual group methods (see Group class for more details)
#    """
#    
#    def _initialize(self):
#        
#        self.output = self.state
#        super(OgerLikeLeakyNeurons, self)._initialize()
#    
#    def _execute(self, timeStep):
#        
#        activatedState = self.activationFunction(self.input)
#        deltaMembrane =  (1. / self.tauStep) * (activatedState - self.state)
#        self.state = self.state + deltaMembrane
#        self.output = self.state
