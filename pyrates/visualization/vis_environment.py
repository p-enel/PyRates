'''
Contains the visualization environments created to interactively go through the
PyRates simulation results data.
'''
# Standard imports
import matplotlib.pyplot as pl

# Local imports
from animated_figure import AnimatedFigure, PyRatesFig
from pyrates.utils.saveload import gzip_load

__all__ = ["VisenvPyRates"]

class VisEnvironment(object):
    
    
    def __init__(self, figClass=AnimatedFigure):
        self.figClass = figClass
        self.ad_fig_list = []
        self.synced_object = []
        self.synced_ref = None
        
    def add_ad_figure(self,
                      synced=False,
                      positions=None,
                      *args, **kwargs):
        
        ad_figure = self.figClass(env=self,
                                  positions=positions,
                                  *args, **kwargs)
        self.ad_fig_list.append(ad_figure)
        if synced == True:
            self.sync_obj(ad_figure)
        return ad_figure
    
    def del_ad_figure(self, ad_figure):
        
        self.ad_fig_list.remove(ad_figure)
        if ad_figure in self.synced_object:
            self.synced_object.remove(ad_figure)
            
    def sync_obj(self, obj):
        
        if self.synced_object != []:
            ref = self.synced_object[0].get_ref()
            if ref != None:
                obj.go_to_ref(ref)
        self.synced_object.append(obj)
        
    def unsync_obj(self, obj):
        
        self.synced_object.remove(obj)
        
    def plot_end_pan(self, newRef, ad_figure):
        
        if ad_figure in self.synced_object:
            for obj in self.synced_object:
                if obj != ad_figure:
                    obj.go_to_ref(newRef)
        
    def go_to_ref(self, newRef):
        
        for obj in self.synced_object:
            obj.go_to_ref(newRef)
            
    def start(self, show=True, ref=0, xAxisSize=1000):
        
        print 'Loading visualization environment...'
        for obj in self.ad_fig_list:
            obj.initialize(ref=ref, xAxisSize=xAxisSize)
        if show:
            print 'Done!'
            pl.show()
        

import pickle as pk
import numpy as np
import os

class VisenvPyRates(VisEnvironment):
    
    
    def __init__(self,
                 folder,
                 simulationName,
                 dataBlocks,
                 *args, **kwargs):
        
#        if folder[-1] != '/':
#            folder += '/'
        dirlist = os.listdir(folder)
        dataList = []
        
        for blockName in dataBlocks:
            
            filename = simulationName + '_' + blockName
            fullPath = folder + filename
            if filename + '.pk' in dirlist:
                f = open(fullPath+'.pk', 'r')
                dataList.append(pk.load(f))
                f.close()
            elif filename + '.gpk' in dirlist:
                dataList.append(gzip_load(fullPath+'.gpk'))
            else:
                msg = 'No file ' + simulationName + '_' + blockName + '.pk/.gpk'
                msg += ' in folder ' + folder
                raise ValueError, msg
            
        if len(dataList) == 1:
            resDic = dataList[0]
        else:
            resDic = self.__concat_data(dataList)
            
        self.resultsDict = resDic
        super(VisenvPyRates, self).__init__(figClass=PyRatesFig,
                                            *args, **kwargs)
        
    
    def __concat_data(self, dataList):
        
        firstBlock = dataList.pop(0)
        for block in dataList:
            for monitoredObj in firstBlock['monitored objects']:
                for var in firstBlock[monitoredObj]['monitored vars']:
                    firstBlock[monitoredObj][var] = np.concatenate([firstBlock[monitoredObj][var], block[monitoredObj][var]], axis=0)
            del block
        
        return firstBlock
        
    def add_ad_figure(self, *args, **kwargs):
        
        return super(VisenvPyRates, self).add_ad_figure(results_dict=self.resultsDict,
                                                        *args, **kwargs)
    
    def start(self, timeStep=0, *args, **kwargs):
        super(VisenvPyRates, self).start(ref=timeStep,
                                         *args, **kwargs)
    
    def __start(self, timeStep=0, *args, **kwargs):
        super(VisenvPyRates, self).start(ref=timeStep,
                                         *args, **kwargs)
        
