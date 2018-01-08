'''
groups subpackage contains the two main types of groups: inputgroups and unitgroups. Another module named reservoir contains
the classes to build reservoirs.
'''

from groups import *
from unitgroups import *

# clean up namespace
del groups
del unitgroups
