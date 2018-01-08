'''
Methods used used in several subpackages
'''

# Standard imports
from __future__ import division
import numpy as np

__all__ = ["typeAndSize", "get_units_to_plot",
           "reshape_matrices", "flatten_layer",
           "checkIfInOptionList", "get_spectral_radius"]

def typeAndSize(object_, type_, size=None):
    
    if not isinstance(object_, type_):
        raise TypeError
    if size is not None:
        if type_ == list or type_ == tuple or dict:
            if len(object_) != size:
                raise ValueError
        elif type_ == np.ndarray:
            if object_.shape != size:
                raise ValueError
    else:
        return object_

def check_argument_type(object_, type_, argName):
    '''Check if object_ is a subclass instance of the class listed in type_
    Raise a TypeError if not
    '''
    wrongType = True
    for t in type_:
        if issubclass(type(object_), t):
            wrongType = False
    if wrongType:
        erMsg = "Arg %s must be a subclass instance of %s"%(argName, str(type_))
        raise TypeError, erMsg        
    else:
        return object_
    
def get_units_to_plot(unitsActivity, unitsList):
    '''Returns a matrix of the activity of specific units from a group activity
    matrix.
    '''
    try:
        np.array(unitsList)
    except ValueError:
        msg = 'The unitsList argument must either be a list of integers, or a '\
        + 'list of 2 elts lists'
        raise ValueError, msg
    output = np.zeros((unitsActivity.shape[0], len(unitsList)))
    one_dim = False
    if len(np.array(unitsList).shape) == 1:
        one_dim = True
    for i in range(len(unitsList)):
        if one_dim:
            output[:,i] = unitsActivity[:,unitsList[i]]
        else:
            output[:,i] = unitsActivity[:,unitsList[i][0],unitsList[i][1]]
    return output

def reshape_matrices(matrix, shape):
    
    groupShape = list(shape)
    nbSteps = matrix.shape[0]
    groupShape.insert(0, nbSteps)
    return matrix.reshape(groupShape)

def flatten_layer(units_activity):
    
    nbSteps, height, width = units_activity.shape
    newMatrix = np.zeros((nbSteps, height*width))
    i = 0
    for row in range(height):
        for column in range(width):
            newMatrix[:,i] = units_activity[:, row, column]
            i += 1
    return newMatrix

def checkIfInOptionList(object_, list_):
    '''
    This function check if the "object_" argument is a string and if it is
    included in the list_ provided as second argument
    '''
    
    if not isinstance(object_, str):
        raise TypeError
    if not object_ in list_:
        raise ValueError
    else:
        return object_

def get_spectral_radius(W):
    
    return np.amax(np.absolute(np.linalg.eigvals(W)))
