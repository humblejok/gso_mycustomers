'''
Created on Apr 24, 2015

@author: sdejonckheere
'''
from container.models import Attributes
from pymongo.mongo_client import MongoClient
from container.setup.application.settings import MONGO_URL

client = MongoClient(MONGO_URL)

containers = client.additional_content['containers']

def enhance_container_information(custom_data, custom_info):
    enhanced_data = {}
    if custom_data!=None:
        for field in custom_data.keys():
            if custom_info.has_key(field) and custom_info[field]['type'] in ['FIELD_TYPE_CHOICE']:
                enhanced_data[field] = Attributes.objects.get(identifier=custom_data[field], type=custom_info[field]['attribute'], active=True).get_short_json()
            else:
                enhanced_data[field] = custom_data[field] 
    return enhanced_data

def get_container_information(container, clean=True):
    all_data = containers.find_one({'_id': container.id})
    if all_data!=None and clean:
        new_data = {}
        for entry in all_data.keys():
            new_data[entry.replace('%','.')] = all_data[entry]
        all_data = new_data
    return all_data

def get_container_provider_information(container, provider):
    data = get_container_information(container)
    if data!=None:
        return data[provider]
    return data

def set_container_history(container, field, value, provider = None):
    None
    
    
def set_container_information(container, field, value, provider = None):
    valid_field_name = field.replace('.','%')
    data = get_container_information(container, False)
    print data
    if data==None:
        if provider==None:
            data = {'_id': container.id, valid_field_name: value}
        else:
            data = {'_id': container.id, provider:  {valid_field_name: value}}
        containers.insert(data)
    else:
        if provider==None:
            data[valid_field_name] = value
        else:
            data[provider][valid_field_name] = value
        containers.save(data)
        
def reset_container_information(container):
    containers.remove({'_id': container.id})