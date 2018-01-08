'''
This module contains methods to generate pseudo-randomly weights for connections 
'''

# Standard imports
import numpy as np

# Local imports
from pyrates.utils.common_methods import *

__all__ = ["generateRandomWeights", "convolutionMask", "winnerTakeAll"]

def generateRandomWeights(nbUnitsIN=1,
                          nbUnitsOUT=None,
                          sparseness=1,
                          mask=None,
                          distribution='uniform',
                          distParams=[0, 1],
                          scaling=1,
                          spectralRadius=None,
                          seed=None):
    '''Generate a weight matrix to connect to unit groups.
    
    Arguments:
    - nbUnitsIN: number of units in the sending group.
    - nbUnitsOUT: number of units in the receiving group. If left to None, the
        default value will be nbUnitsIN (useful for auto-connection).
    - sparseness: a float between 0 and 1 that represent the proportion of
        non-zero elements in the weight matrix.
    - mask: a matrix of boolean values with the shape nbUnitsOUT * nbUnitsIN
        where True elements will be the elements kept in the final matrix.
    - distribution: method used to pseudo randomly generate weights. Takes
        value 'uniform' or 'gaussian'.
    - distParams: a list containing the  distribution parameters:
        if 'uniform': [minimum, maximum]
        if 'normal': [mu, sigma]
    - scaling: a real number that will all the scale matrix elements
    - spectralRadius: a real number to scale the matrix with its spectral radius
    - seed: a integer that is fed to np.random.seed() to enable reproducible
        weight matrix generation.
    '''
    
    # Check parameters:
    optionList = ['uniform', 'gaussian']
    typeAndSize(distParams, list, 2)
    checkIfInOptionList(distribution, optionList)
    if nbUnitsOUT is None:
        nbUnitsOUT = nbUnitsIN
    
    if spectralRadius is not None and nbUnitsIN != nbUnitsOUT:
        raise ValueError, 'spectralRadius can be defined only for square matrices (nbUnitsIN == nbUnitsOUT)'
    
    # Set the seed for the random weight generation
    np.random.seed(seed)
    
    # Uniform random distribution of weights:
    if distribution == 'uniform':
        if distParams is not None:
            minimum, maximum = distParams
        else:
            minimum, maximum = [0, 1]
        weightMatrix = (np.random.random((nbUnitsOUT,nbUnitsIN)) * (maximum - minimum) + minimum)
        
    # Normal (gaussian) random distribution of weights:
    elif distribution == 'gaussian':
        if distParams is not None:
            mu, sigma = distParams
        else:
            mu, sigma = [0, 1]
        weightMatrix = np.random.randn(nbUnitsOUT,nbUnitsIN) * sigma + mu
    
    weightMatrix = weightMatrix * scaling
    weightMatrix = weightMatrix * (np.random.random((nbUnitsOUT,nbUnitsIN)) < sparseness)
    
    if mask is not None:
        weightMatrix = weightMatrix * mask
    
    if spectralRadius is not None:
        weightMatrix *= spectralRadius / get_spectral_radius(weightMatrix)
    
    return weightMatrix


def convolutionMask(layerShape=None, mask=None):
    
    nbUnits = layerShape[0] * layerShape[1]
    weight_matrix = np.zeros((nbUnits,nbUnits))
    if mask.shape[0] % 2 != 1 or mask.shape[1] % 2 != 1:
        raise Exception, 'the mask argument shape must be odd on each dimension'
    
    tmp_matrix = np.zeros((layerShape[0]+mask.shape[0]-1,layerShape[1]+mask.shape[1]-1))
    x_margin = (mask.shape[0] - 1) / 2
    y_margin = (mask.shape[1] - 1) / 2
    
    weight_column = 0
    for x in range(layerShape[0]):
        for y in range(layerShape[1]):
            tmp_matrix[0+x: mask.shape[0] + x, 0 + y: mask.shape[1] + y] = mask
            weight_matrix[:, weight_column] = tmp_matrix[x_margin: tmp_matrix.shape[0] - x_margin,
                                                         y_margin: tmp_matrix.shape[1] - y_margin].flatten()
            tmp_matrix[:] = 0
            weight_column += 1

    return weight_matrix

def winnerTakeAll(nbUnits=None,
                  excitation=1,
                  inhibition=-1):
    '''Generate a weight matrix allowing a winner take all dynamic
    '''
    weight_matrix = (np.ones((nbUnits, nbUnits)) - np.identity(nbUnits)) * inhibition + (np.identity(nbUnits) * excitation)
    return weight_matrix
