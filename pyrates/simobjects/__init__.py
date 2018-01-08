#-*-coding: utf-8-*-
'''
Created on 28 sept. 2012

@author: pierre
'''

from simulation_object import *

from groups import *
from connections import *
from nodes import *

# Make links between simulation object classes:
Connection.nodeLink = Node
Group.singleGrpNodeLink = SingleGrpNode
from pyrates.core.simulation import Simulation
Simulation.simObjClsLink = SimulationObject

del simulation_object