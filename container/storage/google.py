'''
Created on Aug 4, 2015

@author: sdejonckheere
'''
from container.storage import StorageClass
import mimetypes
import os
class Storer(StorageClass):
    
    @classmethod
    def store_file(self, document, source_file_path):
        physical_id = str(document.document_uid) + str(document.document_version_high) + str(document.document_version_low)
        document.document_phid = long(physical_id)
        document.document_mime = mimetypes.guess_type(source_file_path)
        root = str(document.document_phid / 1000)
        file_name = str(document.document_phid % 1000)
        os.rename(source_file_path, None)       
        document.save()
        return document
    
    @classmethod
    def retrieve_file(self, document):
        None