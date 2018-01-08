'''
This module contains functions to save and load objects on disk with the pickle
package.
'''

import gzip
import cPickle as pk

__all__ = ["regular_pickle", "gzip_save", "gzip_load"]

def regular_pickle(obj, filename):
    f = open(filename, 'w')
    pk.dump(obj, f)
    f.close()

def gzip_save(obj, filename, bin_ = 1, verbose=True):
    """Saves a compressed object to disk
    """
    if verbose:
        print 'Gzip_save : started...'
        print 'Gzip_save : gzipping file...'
    try:
        f = gzip.GzipFile(filename, 'wb')
    except IOError:
        msg = 'Check that the path to your result folder is correctly set.\n'
        msg += 'The folder path should end on a slash or anti-slash depending '
        msg += 'on your operating system.\n'
        msg += 'On windows, the path should look like this:\n'
        msg += '\'c:\\path\\to\\the\\folder\\\\\' '
        msg += 'i.e. a double anti-slash at the end of the folder path'
        raise IOError, msg
        
    if verbose:
        print 'Gzip_save : writing file ' + filename + ' ...'
    f.write(pk.dumps(obj, bin_))
    if verbose:
        print 'Gzip_save : done!'
    f.close()

def gzip_load(filename):
    """Loads a compressed object from disk
    """
    
    print 'Gzip_load : loading file ' + filename
    try:
        f = gzip.GzipFile(filename, 'rb')
    except IOError:
        msg = 'Check that the path to your result folder is correctly set.\n'
        msg += 'The path should end on a slash or anti-slash depending on your'
        msg += ' operating system.\n'
        msg += 'On windows, the path should look like this:\n'
        msg += '\'c:\\path\\to\\the\\folder\\\\\' '
        msg += 'i.e. a double anti-slash at the end of the folder path'
        raise IOError, msg
    buffer_ = ""
    while 1:
        data = f.read()
        if data == "":
            break
        buffer_ += data
    obj = pk.loads(buffer_)
    f.close()
    print 'Gzip_load : file loaded'
    return obj