#-*-coding: utf-8-*-
'''
Created on 12 oct. 2012

@author: pierre
'''

import sys, os
from PyQt4 import QtGui

def getpath(filename,
            noPathFileMsg='',
            wrongFolderMsg='',
            selectFolderMsg=''):
        
    try:
        f = open('./'+filename,'r')
    except IOError:
        folder = get_new_path(filename,
                              noPathFileMsg, 
                              selectFolderMsg)
    else:
        folder = f.readline()
        f.close()
        currentDir = os.getcwd()
        try:
            os.chdir(folder)
        except:
            folder = get_new_path(filename,
                                         wrongFolderMsg,
                                         selectFolderMsg)
        else:
            os.chdir(currentDir)
    finally:
        return folder

def get_new_path(filename,
                 infoMsg,
                 selectFolderMsg):
    
    app = QtGui.QApplication(sys.argv)
    QtGui.QMessageBox.about(None, 'No folder', infoMsg)
    folder = str(QtGui.QFileDialog.getExistingDirectory(caption='Select a directory'))
    app.exit()
    if len(folder) == 0:
        return None
    if os.name == 'posix':
        folder += '/'
    elif os.name == 'nt':
        folder += '\\'
    g = open('./'+filename,'w')
    g.write(folder)
    g.close()
    return folder
