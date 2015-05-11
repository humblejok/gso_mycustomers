'''
Created on Jun 18, 2014

@author: sdejonckheere
'''

import datetime
import os

from django.template import loader
from django.template.context import Context
from pymongo.mongo_client import MongoClient
from seq_common.utils.dates import epoch_time

from container.settings import MONGO_URL, STATICS_PATH
from seq_common.utils import classes


client = MongoClient(MONGO_URL)

setup = client.setup


def get_data(collection_name, searched_id=None):
    if searched_id==None:
        results = getattr(setup,collection_name).find().sort("_id", -1)
    else:
        results = getattr(setup,collection_name).find({'_id':searched_id})
    
    if results.count()>0:
        return results[0]
    else:
        return {}
    
def set_data(collection_name, data, historize=True):
    if historize:
        data['_id'] = epoch_time(datetime.datetime.today())
        getattr(setup,collection_name).insert(data)
    else:
        if not data.has_key('_id'):
            data['_id'] = epoch_time(datetime.datetime.today())
        getattr(setup,collection_name).update({'_id': data['_id']}, data, True)
    if globals().has_key(collection_name + '_callback'):
        globals()[collection_name + '_callback'](data)
        
def object_type_callback(data):
    all_types = classes.my_import('containet.models.Attributes').objects.filter(active=True, type='object_type')
    for a_type in all_types:
        if data.has_key(a_type.identifier):
            context = Context({"selection": data[a_type.identifier]})
            template = loader.get_template('rendition/object_type/lists/object_type_choices.html')
            rendition = template.render(context)
            # TODO Implement multi-langage
            outfile = os.path.join(STATICS_PATH, a_type.identifier + '_en.html')
            with open(outfile,'w') as o:
                o.write(rendition.encode('utf-8'))