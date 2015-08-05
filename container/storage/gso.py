'''
Created on Aug 4, 2015

@author: sdejonckheere
'''
from container.storage import StorageClass
import os
import mimetypes
from container.setup.application.settings import WORKING_PATH
from shutil import copyfile

STORAGE_PATH = "u:\\DEV\\Tests\\MyC\\Documents"

class Storer(StorageClass):
    
    @classmethod
    def store_file(self, document, source_file_path):
        physical_id = str(document.document_uid) + str(document.document_version_high) + str(document.document_version_low)
        document.document_phid = long(physical_id)
        document.document_mime = mimetypes.guess_type(source_file_path)
        file_name = str(document.document_phid)
        target_file_folder = self.get_target_folder(document.document_phid)
        target_file_path = os.path.join(target_file_folder, file_name)
        os.makedirs(target_file_folder)
        os.rename(source_file_path, target_file_path)       
        document.save()
        return document
    
    @classmethod
    def retrieve_file(self, document):
        file_name = str(document.document_phid)
        target_file_folder = self.get_target_folder(document.document_phid)
        source_file_path = os.path.join(target_file_folder, file_name)
        target_file_path = os.path.join(WORKING_PATH, document.name)
        copyfile(source_file_path, target_file_path)
        return target_file_path
    
    @classmethod
    def delete_file(self, document):
        file_name = str(document.document_phid)
        target_file_folder = self.get_target_folder(document.document_phid)
        source_file_path = os.path.join(target_file_folder, file_name)
        os.remove(source_file_path)
        return True
    
    @classmethod
    def trash_file(self, document):
        return False
    
    @staticmethod
    def get_target_folder(phid):
        last = phid % 10000
        mid = (phid / 10000) % 10000
        root = str(phid / 10000000)
        mid = '%04d' % mid
        last = '%04d' % last
        return os.path.join(STORAGE_PATH, root, mid, last)