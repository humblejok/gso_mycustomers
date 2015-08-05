from seq_common.utils.classes import my_class_import
import os

SETTINGS_PATH = os.path.realpath(__file__)

MONGO_URL = "{{application_settings.MONGO_URL}}"
RESOURCES_MAIN_PATH = "{{application_settings.RESOURCES_MAIN_PATH}}"
MAIN_PATH = "{{application_settings.MAIN_PATH}}"
STATICS_PATH = "{{application_settings.STATICS_PATH}}"
TEMPLATES_STATICS_PATH = "{{application_settings.TEMPLATES_STATICS_PATH}}"
WORKING_PATH = "{{application_settings.WORKING_PATH}}"
STORAGE_ENGINE = "{{application_settings.STORAGE_ENGINE}}"

STORER = my_class_import('container.storage.' + STORAGE_ENGINE + '.Storer')()