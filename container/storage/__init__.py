'''
Created on Aug 4, 2015

@author: sdejonckheere
'''
from abc import ABCMeta
import threading
import os
from container.setup.application.settings import WORKING_PATH

UUID_FILENAME = os.path.join(WORKING_PATH, 'uuid')

class abstractclassmethod(classmethod):

    __isabstractmethod__ = True

    def __init__(self, callable_method):
        callable_method.__isabstractmethod__ = True
        super(abstractclassmethod, self).__init__(callable_method)
        
class StorageClass:
    __metaclass__=  ABCMeta
    
    @abstractclassmethod
    def store_file(self, document, source_file):
        return self()
    
    @abstractclassmethod
    def retrieve_file(self, document):
        return self()
    
    @abstractclassmethod
    def delete_file(self, document):
        return self()
    
    @abstractclassmethod
    def trash_file(self, document):
        return self()

def get_uuid():
    with threading.Lock():
        value = 100000
        try:
            with open(UUID_FILENAME, "r") as fd:
                value = long(fd.readline().strip()) + 1
        except:
            None
        with open(UUID_FILENAME, "w") as fd:
            fd.write(str(value) + "\n")
        return value