'''
Module referencing all the units that can be used in the simulation. Still in
development...
'''
#from __future__ import division
from warnings import warn
numericTypes = [int, long, float]

class Unit(object):
    def __init__(self, value=1, factor=1):
        if type(factor) is not int:
            raise TypeError, 'The factor has to be an integer'
        self.value = float(value * factor)
        
    def __mul__(self, other):
        self.checkOtherType(other)
        self.value = self.checkOutputValue(self.value * other)
        return self
    
    def __rmul__(self, other):
        return self.__mul__(other)
    
    def __div__(self, other):
        self.checkOtherType(other)
        self.value = self.checkOutputValue(self.value / other)
        return self
        
    def __rdiv__(self, other):
        self.checkOtherType(other)
        self.value = self.checkOutputValue(other / self.value)
        return self
    
    def __add__(self, other):
        self.checkOtherType(other)
        self.value = self.checkOutputValue(self.value + other)
        return self
    
    def __radd__(self, other):
        return self.__add__(other)
    
    def __sub__(self, other):
        self.checkOtherType(other)
        self.value = self.checkOutputValue(self.value - other)
        return self
    
    def __rsub__(self, other):
        self.checkOtherType(other)
        self.value = self.checkOutputValue(other - self.value)
        
    def __lt__(self, other):
        return self.compare(other, self.value.__lt__)
        
    def __le__(self, other):
        return self.compare(other, self.value.__le__)
        
    def __eq__(self, other):
        return self.compare(other, self.value.__eq__)
        
    def __ne__(self, other):
        return self.compare(other, self.value.__ne__)
    
    def __gt__(self, other):
        return self.compare(other, self.value.__gt__)
        
    def __ge__(self, other):
        return self.compare(other, self.value.__ge__)
    
    def compare(self, other, operatorFunction):
        if isinstance(other, type(self)):
            return operatorFunction(other.value)
        elif type(other) not in numericTypes:
            raise TypeError, "You cannot compare %s with %s"%(str(type(self)),
                                                              type(other))
        else:
            return operatorFunction(other)
        
    def checkOtherType(self, other):
        if type(other) not in numericTypes:
            raise TypeError, 'Basic operations with unit objects can be done '\
                + 'only with numbers or other units in specific cases'
        
    def checkOutputValue(self, value):
        if value < 0:
            raise ValueError, '%s cannot have negative values'%type(self)
        else:
            return value

class Time(Unit):
    '''Class defining the time in PyRates
    Reference unit is the millisecond
    '''
#    def __rdiv__(self, other):
#        if issubclass(type(other), Distance):
#            pass
#        else:
#            return super(Time, self).__rdiv__(other)
    
    def __div__(self, other):
        if issubclass(type(other), TimeStep):
            return Deltat(self.value / other.value, 1)
        elif issubclass(type(other), Deltat):
            tmp = self.value / other.value
            outputValue = int(round(tmp))
            if outputValue - round(outputValue) != 0:
                print 'TimeStep value of %f rounded to %d'%(tmp, outputValue)
            return TimeStep(outputValue, 1)
        else:
            return super(Time, self).__div__(other)
    
    def __repr__(self):
        return str(self.value) + ' ms'

class MS(Time):
    def __rmul__(self, other):
        return Time(1, 1) * other

class S(Time):
    def __rmul__(self, other):
        return Time(1, 1000) * other
    
class MIN(Time):
    def __rmul__(self, other):
        return Time(1, 60000) * other
   
ms = MS(1, 1)
s = S(1, 1000)
min = MIN(1, 60000)

class Distance(Unit):
    '''Class defining distance in PyRates
    Reference unit is the millimeter
    '''
    def __div__(self, other):
        if issubclass(type(other), Time):
            return Speed(self.value / other.value, 1)
        elif issubclass(type(other), Speed):
            return Time(self.value / other.value, 1)
        elif type(other) in (int, float):
            return super(Distance, self).__div__(other)
    
    def __repr__(self):
        return str(self.value) + ' mm'
    
class MM(Distance):
    def __rmul__(self, other):
        return Distance(1, 1) * other

class M(Distance):
    def __rmul__(self, other):
        return Distance(1, 1000) * other

mm = MM(1, 1)
m = M(1, 1000)

class Speed(Unit):
    '''Class defining speed in PyRates.
    Reference unit is the millimeter per millisecond.
    '''
    def __div__(self, other):
        if issubclass(type(other), Time):
            raise TypeError, "We don't do accelerations yet ;)"
        else:
            return super(Speed, self).__div__(other)
    
    def __repr__(self):
        return str(self.value) + ' mm/ms'
    
class MMperMS(Speed):
    def __rmul__(self, other):
        return Speed(1, 1) * other
    
mmPms = MMperMS(1, 1)

class TimeStep(Unit):
    '''Class defining time step in PyRates'''
    def __init__(self, value=1, factor=1):
        if type(value) is not int:
            raise TypeError, '"value" argument of class TimeStep has to be an'+\
            ' integer'
        self.value = value * factor
    
    def __repr__(self):
        return str(self.value) + ' ts'
    
class TS(TimeStep):
    def __rmul__(self, other):
        if type(other) is not int:
            raise TypeError, 'TimeSteps units have integer values'
        return TimeStep(1, 1) * other

class KTS(TimeStep):
    '''Class for 1000 ts'''
    def __rmul__(self, other):
        if type(other) is not int:
            raise TypeError, 'TimeSteps units have integer values'
        return TimeStep(1, 1000) * other

ts = TS(1, 1)
kts = TS(1, 1000)

class Deltat(Unit):
    '''The class defining the precision of the simulator, i.e. the simulated
    time between two time steps.
    '''
    def __repr__(self):
        return str(self.value) + ' ms/ts'

def time2tstep(time, whoAsk=None):
    '''Convert time into time steps with deltat.
    WARNING:
    Make sure delta_t is set before using the function, otherwise the conversion
    will be done with the default delta_t value if set.
    Argument whoAsk allows to precise which object asked for the conversion if
    the division is not round.
    '''
    if time2tstep.deltat == None:
        msg = 'You must specify value for deltat before trying to do a conversion.'
        msg += 'Use function set_deltat()'
        raise ValueError, msg
    if not issubclass(type(time), Time):
        raise TypeError, "Type of argument time must be a subclass of Time"
    
    tmp = time / time2tstep.deltat.value
    outputValue = int(round(tmp))
    if outputValue - round(outputValue) != 0:
        if whoAsk is not None:
            warnMsg = "Conversion from Time to TimeStep in object %s"%(whoAsk)
            warnMsg += " had value %f. It was rounded to %d"%(tmp, outputValue)
        else:
            warnMsg = 'TimeStep value of %f rounded to %d'%(tmp, outputValue)
        warn(warnMsg)
    
    return TimeStep(outputValue, 1)

def tstep2time(timeSteps):
    '''Convert time steps into time with deltat.
    WARNING:
    Make sure delta_t is set before using the function, otherwise the conversion
    will be done with the default delta_t value if set.
    '''
    if tstep2time.deltat == None:
        msg = 'You must specify value for deltat before trying to do a conversion.'
        msg += 'Use function set_deltat()'
        raise ValueError, msg
    if not issubclass(type(timeSteps), TimeStep):
        raise TypeError, "Type of argument time must be a subclass of TimeStep"
    
    return timeSteps * time2tstep.deltat

time2tstep.deltat = None
tstep2time.deltat = None

################################################################################
############################# Testing area!! ###################################
################################################################################

#dis = 50 * mm
#s = dis / s
#print s
#d = 100 * mm
#e = 1 * m
#print d / s
#print d < e
