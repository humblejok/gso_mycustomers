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

from container.models import Attributes
from container.settings import MONGO_URL, STATICS_PATH


client = MongoClient(MONGO_URL)

setup = client.setup


def get_data(collection_name):
    results = getattr(setup,collection_name).find().sort("_id", -1)
    if results.count()>0:
        return results[0]
    else:
        return {}
    
def set_data(collection_name, data):
    data['_id'] = epoch_time(datetime.datetime.today())
    getattr(setup,collection_name).insert(data)
    if globals().has_key(collection_name + '_callback'):
        globals()[collection_name + '_callback'](data)
        
def object_type_callback(data):
    all_types = Attributes.objects.filter(active=True, type='object_type')
    for a_type in all_types:
        if data.has_key(a_type.identifier):
            context = Context({"selection": data[a_type.identifier]})
            template = loader.get_template('rendition/object_type/lists/object_type_choices.html')
            rendition = template.render(context)
            # TODO Implement multi-langage
            outfile = os.path.join(STATICS_PATH, a_type.identifier + '_en.html')
            with open(outfile,'w') as o:
                o.write(rendition.encode('utf-8'))