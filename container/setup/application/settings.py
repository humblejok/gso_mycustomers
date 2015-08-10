from seq_common.utils.classes import my_class_import
import os

SETTINGS_PATH = os.path.realpath(__file__)

APPLICATION_NAME = 'MyCustomers'
MONGO_URL = "mongodb://127.0.0.1:27018/"
RESOURCES_MAIN_PATH = "c:\\DEV\\Sources\\gso_mycustomers\\resources"
MAIN_PATH = "c:\\DEV\\Sources\\gso_mycustomersesources"
STATICS_PATH = "c:\\DEV\\Sources\\gso_mycustomers\\resources\\statics\\templates"
TEMPLATES_STATICS_PATH = "c:\\DEV\\Sources\\gso_mycustomers\\resources\\templates\\statics"
WORKING_PATH = "c:\\DEV\\Tests\\MyC"
STORAGE_ENGINE = "gso"

STORER = my_class_import('container.storage.' + STORAGE_ENGINE + '.Storer')()