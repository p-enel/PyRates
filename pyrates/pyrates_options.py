""" Define options of package PyRates.

You will find her the default options you may change to suit your usage of the
package. You may create your own options!
"""
# If you don't want to register manually every object you create for the
# simulation, leave it to True. Automatic registration also create a simulation
# when importing the MyFRNs package, see documentation to register yourself the
# objects.
automatic_object_register = True

# Here you can specify the default 'delta t' (time between two time steps)
# Change the value only if you are going to use the same value for all your si-
# -mulations
default_delta_t = None

# If you wish to have the same simulation time you can specify it here (it not
# recommended...)
default_sim_time = None

if automatic_object_register is False:
    print "PyRates options: object will not be saved automatically"
if default_delta_t is not None:
    print "PyRates options: deltat is set to value %s by default"%str(default_delta_t)
if default_sim_time is not None:
    print "PyRates options: simulation time is set to value %s by default"%str(default_sim_time)