"""
Setup script to install PyRates
"""

from distutils.core import setup

# Check that necessary python packages are installed before installing PyRates
try:
    import matplotlib
    import numpy
except:
    msg = 'PyRates could not install, PyRates needs matplotlib and numpy to be'
    msg += 'installed!'
    raise Exception

setup(name='PyRates',
      version='0.1',
      description='Python Firing Rate Neurons Simulator',
      author='Pierre Enel',
      author_email='pierre.enel@inserm.fr',
      packages=['pyrates',
                'pyrates.simobjects',
                'pyrates.simobjects.connections',
                'pyrates.simobjects.groups',
                'pyrates.simobjects.nodes',
                'pyrates.core',
                'pyrates.scripting',
                'pyrates.visualization',
                'pyrates.utils']
      )

print 'PyRates installation seems to be successful!'
