# connection subpackage
'''Define the different connection class

Modules:
  - connection: contains the basic Connection class
  - dynamic_connections: contains the different dynamic connections
'''

from connection import *
from dynamic_connections import *

del connection
del dynamic_connections

#__all__ = ["Connection", "StaticConnection", "DynamicConnection",
#           "DAModulatedConnection", "DAconnectionCVDtask"]