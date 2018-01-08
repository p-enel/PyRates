'''
Module containing the Simulaiton class, the core object running the simulation.
'''
# Standard imports
from __future__ import division
#from warnings import warn
import numpy as np
import multiprocessing, traceback, sys

# Local imports
from units import *
import pyrates
from pyrates.utils import gzip_save, regular_pickle
import atexit

__all__ = ["Simulation"]

class Simulation(object):
    '''Simulation is the main class that takes care of the simulation.
    It initializes and executes the different objects in the simulaiton.
    Args:
        - simTime : is the maximum time of the simulation. This argument is not
            mandatory and can be useful for simulation where the simulation time
            is not specified in the inputs
        - deltat : it is the precision of the simulator and refers to the time
            elapsed between two time steps. It must be defines when time units
            are used to parameter the simulation.
    '''
    
    simObjClsLink = None
    
    def __init__(self,
                 simTime=None,
                 deltat=None):
        
        self.simTime = simTime
        self.deltat = deltat
        self.__monitoringBounds = None
        self.__isMonitoring = False
        self.__monitorManager = None
        self.__startMonitorSignal = False
        self.__stopMonitorSignal = False
        # Initialize the simulation-objects lists
        self.groups = []
        self.connections = []
        self.dynamicConnections = []
        self.monitoredObjects = []
        self.allObjects = []
        self.savedObjects = []
        self.nodes = []
        self.inputs = []
        self.savedData = {}
        self.unnamedDataCount = 0
        
    def set_deltat(self, value):
        self.deltat = value
        time2tstep.deltat = value
        
    def monitor_bounds(self, bounds=None, keepRunning=False):
        '''Set time step bounds to monitor_bounds object within these time step
        intervals
        
        Arguments:
        - bounds: it is list of 2 integers lists, each being the interval when
            the monitors should be triggered to record activity in simulation
            objects.
        - keepRunning: with its default value, the simulator stops after the
            upper bound of the last interval. If you don't want this to happen
            set it to True.
            
        Bounds example: [[500,2000],[5000,5500]] will trigger the monitors for
        the periods when the simulation time steps are within the [500, 2000]
        and the [5000,5500] intervals.
        Make sure that in all the lists, the first element is lower than the
        second and that the intervals are not overlapping which won't be allowed
        by the simulator.
        The last interval can have None as upper bound, which will record the
        activity of objects until the end of the simulation
        '''
        if bounds is not None:
            msg = 'The "bounds" argument must either be a list of 2 elts lists'\
                + '. See Simulation.monitor_bounds.__doc__'
            try:
                assert len(np.array(bounds).shape) == 2
            except Exception:
                raise ValueError, msg
            
            for lowerBd, upperBd in bounds:
                try:
                    assert type(lowerBd) == int and type(upperBd) == int
                except Exception:
                    raise ValueError, msg
                if lowerBd >= upperBd:
                    msg = 'Check that lower bounds is inferior to upper bounds'\
                    + 'in "bounds" argument.'
                    raise ValueError, msg
        else:
            bounds = [[0, None]]
        
        self.__monitoringBounds = bounds
        self.set_monitor_manager(self)
        self.keepRunning = keepRunning
    
    def run(self,
            simTime=None,
            deltat=None,
            monitoringBounds=None):
        '''Main functions that runs the simulation.
        Note that simTime and deltat can be set in this function rather than in
        the __init__ function.
        '''
        if self.__monitorManager is None:
            if self.monitoredObjects != []:
                self.monitor_bounds()
            else:
                msg ="\nNothing is monitored! You won't be able to save "\
                + "activity from the simulated objects (group, connections, "\
                + "nodes...)" 
                warn(msg)
        
        # Check parameters in order to avoid conflicts/inconsistency between them 
        self.check_and_set_params(simTime, deltat)
        
        ######## Initialization #######
        self.initialize_nodes()
        # connections initialization must happen after initialization of nodes!
        self.initialize_connections()
        
        if self.__monitorManager is not None:
            self.writingDataQueue = multiprocessing.Queue()
            self.writing_process = WriteProcess(self.writingDataQueue)
            self.writing_process.start()
        
        try:
            self.__core_loop()
        except Exception:
            if self.__monitorManager is not None:
                self.writingDataQueue.put(None)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print 'Traceback of exception: %s of %s'%(exc_value, str(exc_type))
            traceback.print_tb(exc_traceback, limit=10, file=sys.stdout)
            print '\n'
            raise exc_type, exc_value
            
        if self.__monitorManager is not None:
            self.writingDataQueue.put(None)
            
        print 'simulation done!'
    
    def __core_loop(self):
        
        if self.__monitorManager is self:
            currentBounds = self.__monitoringBounds.pop(0)
            if currentBounds[0] == 0:
                if currentBounds[1] != None:
                    nbTimeSteps = currentBounds[1] + 1
                else:
                    nbTimeSteps = None
                self.start_monitoring(nbTimeSteps)
            
        self.simulationOngoing = True
        
        if self.nbTimeStepsSim is not None:
            nbTimeSteps = str(self.nbTimeStepsSim)
        else:
            nbTimeSteps = 'Unknown'
        print 'Number of time-steps : %s'%nbTimeSteps
        print 'Running!!!'
        
        self.timeStep = 1
        ########## THE execution loop! #########################################
        while self.simulationOngoing:
            
            # Update the connections
            for connection in self.connections:
                connection._execute(self.timeStep)
            
            # Compute the input vector of each group with the output of the
            # previous time step
            for group in self.groups:
                group._add_up_inputs()
            
            # Execute all the nodes and the groups inside the nodes
            for node in self.nodes:
                node._execute(self.timeStep)
            
            # Do the actual monitoring work!
            if self.__isMonitoring:
                self.__monitoring()
                if self.__stopMonitorSignal:
                    self.__stop_monitoring()
            elif self.__startMonitorSignal:
                self.__start_monitoring()
            
            # Manage the start and stop of monitors if it is monitored by the
            # simulation with predefined bounds
            if self.__monitorManager is self:
                if self.__isMonitoring:
                    if self.timeStep == currentBounds[1]:
                        self.__stop_monitoring()
                        if self.__monitoringBounds != []:
                            currentBounds = self.__monitoringBounds.pop(0)
                        # To be removed to keep the simulation going without
                        # monitoring
                        elif not self.keepRunning:
                            self.simulationOngoing = False
                            print 'No more monitors, simulation stops'
                else:
                    if self.timeStep == currentBounds[0]:
                        if currentBounds[1] != None:
                            nbTimeSteps = currentBounds[1] - currentBounds[0] + 1
                        else:
                            nbTimeSteps = None
                        self.start_monitoring(nbTimeSteps)
                        
            self.timeStep += 1
            
            if self.nbTimeStepsSim is not None and self.timeStep >= self.nbTimeStepsSim + 1:
                self.simulationOngoing = False
        ###################################################################
        if self.__isMonitoring:
            if self.__monitorManager is self:
                if currentBounds[1] is not None:
                    msg = 'Simulation stopped before the end of the last '\
                        + 'monitor bound!'
                    warn(msg)
            else:
                msg = 'Simulation stopped before the end of the last monitor '\
                    + 'bound!'
                warn(msg)
            self.__stop_monitoring()
            self.save_data()
    
    def get_monitoring_bounds(self):
        return self.__monitoringBounds
    
    def set_monitor_manager(self, monitorManager):
        '''Set the manager of the monitors (when to start or stop monitoring'''
        if self.__monitorManager is not None:
            msg = "Object %s wants to be monitor manager "%str(monitorManager)
            msg += "but simulation already has a manager: %s"
            msg = msg%str(self.__monitorManager)
            raise ValueError, msg
        else:
            self.__monitorManager = monitorManager
    
    def get_monitor_manager(self):
        return self.__monitorManager
    
    def __monitoring(self):
        '''Save the successive states of different objects of the simulation'''
        for obj in self.monitoredObjects:
            obj._monitoring(self.timeStep)
    
    def start_monitoring(self, nbTimeSteps=None, blockName=None):
        self.__newBlockName = blockName
        self.__monitorNbTimeSteps = nbTimeSteps
        self.__startMonitorSignal = True
        
    def __start_monitoring(self):
        if self.__isMonitoring:
            raise Exception
        self.__startMonitorSignal = False
        self.__isMonitoring = True
        self.__currentBlockName = self.__newBlockName
        del self.__newBlockName
        self.initialize_monitors(self.__monitorNbTimeSteps)
    
    def stop_monitoring(self):
        if not self.__isMonitoring:
            msg ='Trying to stop monitoring while simulation was not monitoring'
            raise Exception, msg
        self.__stopMonitorSignal = True
    
    def close_monitors(self):
        for obj in self.monitoredObjects:
            obj._close_monitors()
    
    def __stop_monitoring(self):
        self.__stopMonitorSignal = False
        self.__isMonitoring = False
        self.close_monitors()
        self.save_data(dataName=self.__currentBlockName)
        del self.__currentBlockName
    
    def isMonitoring(self):
        return self.__isMonitoring
    
    def set_save_folder(self,
                        folder=None,
                        simulationName=None,
                        compression=True):
        
        self.saveFolder = folder
        self.simulationName = simulationName
        self.compression = compression
    
    def save_data(self, dataName=None, objectsList=None):
        
        if objectsList is None:
            objectsList = self.savedObjects
        
        savedData = {}
        counter = 1
        for obj in objectsList:
            if isinstance(obj, self.simObjClsLink):
                obj = obj._saveddata()
            if isinstance(obj, dict):
                if 'name' in obj.keys():
                    savedData.update({obj['name'] : obj})
                else:
                    savedData.update({'object ' + str(counter) : obj})
                    counter += 1
            elif 'name' in dir(obj):
                savedData.update({obj.name : obj})
            else:
                savedData.update({'object ' + str(counter) : obj})
                counter += 1
        
        savedData['monitored objects'] = []
        for obj in self.monitoredObjects:
            savedData['monitored objects'].append(obj.name)
        
        savedData['data origin'] = 'PyRates %s'%pyrates.__version__
        savedData['monitor manager'] = str(self.__monitorManager)
        
        if dataName is None:
            dataName = "unnamed_%d"%self.unnamedDataCount
            self.unnamedDataCount += 1
        
        d = DataWriter(savedData, self.saveFolder, dataName, self.simulationName, self.compression)
        self.writingDataQueue.put(d)
        
    def post_run(self):
        '''Operations done after the execution of the main function "run"'''
        for obj in self.monitoredObjects:
            obj._close_monitors(self.timeStep - 1)
    
    def initialize_nodes(self):
        '''Initializing all the nodes of the simulation with their respective
        _initialize function.
        '''
        for connection in self.connections:
            connection._initialize()
            
        for node in self.nodes:
            node._initialize()
    
    def initialize_monitors(self, nbTimeSteps=None):
        '''Initializing all the monitors of the simulation with their respective
        _initialize function.
        ''' 
        for obj in self.monitoredObjects:
            obj._initialize_monitor(nbTimeSteps)
            
    def initialize_connections(self):
        '''Initializing all the connections of the simulation with their
        respective _initialize function.
        '''
        for connection in self.connections:
            connection._initialize()
    
    def check_and_set_params(self, simTime, deltat):
        '''Check simTime and deltat when set with the run function'''
        self.nbNG = len(self.groups)

        if self.nbNG == 0:
            raise Exception, 'no NeuronGroup has been instantiated'
        
        if simTime is not None:
            if self.simTime is not None:
                warn('Simulation time simTime has been defined several times\nsim_time used is the one passed as argument of method run(): ' + str(simTime))
            if deltat is None and self.deltat is None:
                raise Exception, 'If a simulation time is specified, a time step deltat must be specified as well' 
            self.simTime = simTime
        
        if deltat is not None:
            if self.deltat is not None:
                warn('deltat has been defined several times\ndelta_t used is the one passed as argument of method run(): ' + str(deltat))
#            if self.simTime is None:
#                raise Exception, 'If a time step deltat is specified, a simulation time must be specified as well'
            self.deltat = deltat
        
        if self.simTime is not None:
            self.nbTimeStepsSim = int(simTime / deltat)
            if self.inputs != []:
                for inputGroup in self.inputs:
                    if inputGroup.get_nbtimesteps() > self.nbTimeStepsSim:
                        warn('The number of time steps in the input is bigger than the number of time steps given by the specified'+\
                        '\nsimulation time. Only the first ' + str(self.nbTimeStepsSim) + ' of the input will be used')
        elif self.inputs == []:
            raise Exception, 'No simulation time or input group has been specified, the simulation cannot run'
        else :
            tempList = []
            for inputGroup in self.inputs:
                
                tempList.append(inputGroup.get_nbtimesteps())
            if None in tempList:
                self.nbTimeStepsSim = None
            else:
                self.nbTimeStepsSim = max(tempList)

def write_data(savedData,
               folder,
               simulationName,
               dataName,
               compression=True):
    
    filenameTmp = folder + simulationName + '_' + dataName
    if compression == True:
        filenameTmp += '.gpk'
        gzip_save(savedData, filenameTmp, verbose=False)
    else:
        filenameTmp += '.pk'
        regular_pickle(savedData, filenameTmp)
        
    print '%s saved to file %s'%(dataName, filenameTmp)    

class DataWriter(object):
    '''Object passed to the WriteProcess, calls the method to write data on disk
    '''
    def __init__(self, savedData, folder, dataName, simulationName, compression):
        self.savedData = savedData
        self.folder = folder
        self.dataName = dataName
        self.simulationName = simulationName
        self.compression = compression
    
    def write(self):
        write_data(self.savedData,
                   self.folder,
                   self.simulationName,
                   self.dataName,
                   self.compression)
        return 0

class WriteProcess(multiprocessing.Process):
    '''An additional process to save data on disk, especially useful to compress
    data while the simulation is running.
    '''
    def __init__(self, dataQueue):
        multiprocessing.Process.__init__(self)
        self.dataQueue = dataQueue
        
    def run(self):
        while True:
            writeData = self.dataQueue.get()
            if writeData is None:
                # Poison pill means we should exit
                print 'Write process: safely closed'
                break
            writeData.write()
            del writeData
        return