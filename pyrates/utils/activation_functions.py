'''
These functions are used to get the output of units from their state
'''

from __future__ import division
import numpy as np

__all__ = ["Dominey1995", "Logistic_f", "Identity_f", "Bounded_identity_f",
           "Weight_transfer_function", "Tanh"]

class Dominey1995:
    '''Transfer function used in Dominey et al., Journal of Cognitive
    Neuroscience 1995.
    
    '''
    name = 'Dominey1995'
    # Default parameters
    dftParams = [0, 1, 0, 1]
    
    @staticmethod
    def get_function(params=None):
        '''
        [min_input, max_input, min_output, max_output] = params
        f(x) = (max_output - min_output) * (S^2 * (3 - 2 * S)) + min_output
        with S = (x - min_input) / (max_input - min_input) 
        (max_output - min_output) * ((x-min_input)/(max_input-min_input)**2 * (3 - 2*(x-min_input)/(max_input-min_input)))
        -> see Dominey 1995
        '''
        
        if params is None:
            [min_input, max_input, min_output, max_output] = Dominey1995.dftParams
        else:
            [min_input, max_input, min_output, max_output] = params

        #################### Here is how would look like the following lambda function if it was unfolded        
#        def transfer_function(x, params):
#            lower_bound = (x < min_input) * min_input
#            upper_bound = (x > max_input) * max_input
#            x = x * (x > min_input) * (x < max_input)
#            x = x + lower_bound + upper_bound
#            return (max_output - min_output) * (((x-min_input)/(max_input-min_input))**2 * (3 - 2*(x-min_input)/(max_input-min_input))) + min_output
        
        return lambda x : ((max_output - min_output) * (((x-min_input)/(max_input-min_input))**2 * (3 - 2*(x-min_input)/(max_input-min_input))) + min_output) * (x > min_input) * (x < max_input) + ((x <= min_input) * min_output) + ((x >= max_input) * max_output)
    
    @staticmethod
    def get_output_range(params):
        
        if params is None:
            return Dominey1995.dftParams[2:4]
        else:
            return params[2:4]
        
class Logistic_f:
    
    
    name = 'Logistic_f'
    
    @staticmethod
    def get_function(params=[-10, 0.5]):
        
#        [slope, offset] = params
        return lambda x : 1 / (1 + np.exp(params[0] * (x - params[1])))
    
    @staticmethod
    def get_output_range(params):
        
        return [0, 1]
    
class Identity_f:
    
    
    name = 'Identity_f'
    @staticmethod
    def get_function(params):
        
        return lambda x : x
    
    @staticmethod
    def get_output_range(params):
        
        return None
    
class Bounded_identity_f:
    
    
    name = 'Bounded_identity_f'
    
    @staticmethod
    def get_function(params=[0, 1]):
        
        min_output = params[0]
        max_output = params[1]
        return lambda x : x * (x >= min_output) * (x <= max_output) + (x >= max_output) * max_output + (x <= min_output) * min_output
    
    @staticmethod
    def get_output_range(params):
        
        return params
    
class Weight_transfer_function:
    
    
    name = 'Weight_transfer_function'
    
    @staticmethod
    def get_function(params=None):
        
        return lambda x : np.arcsin((x * (x >= 0) * (x <= 1) - 0.5) * 2) / np.pi + 0.5
    
    @staticmethod
    def get_output_range(params):
        
        return [0, 1]
    
class Tanh:
    """tanh activation function.
    First parameter is the inflection point of the function.
    Second parameter is the scaling of the function.
    """
    
    name = 'tanh'
    
    @staticmethod
    def get_function(params=[0, 1]):
        
        if params is None:
            params = [0, 1] 
        inflection_point = params[0]
        scaling = params[1]
        return lambda x : np.tanh(x/scaling) * scaling + inflection_point
    
    @staticmethod
    def get_output_range(params):
        
        if params is None:
            params = [0, 1]
        return [params[0] - params[1], params[0] + params[1]]
