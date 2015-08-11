'''
Created on Apr 24, 2015

@author: sdejonckheere
'''
from container.models import Attributes
from pymongo.mongo_client import MongoClient
from container.setup.application.settings import MONGO_URL
from container.utilities.utils import complete_custom_historical_fields_information,\
    get_custom_historical_key
from seq_common.utils.dates import epoch_time
import datetime
from container.utilities import setup_content

client = MongoClient(MONGO_URL)

containers = client.additional_content['containers']
historical = client.additional_content['historical']

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
    print field
    print value
    # TODO Handle Intraday
    collection_id = field + '_' + str(container.id)
    key_field = get_custom_historical_key(container.type.identifier, field)
    fields_info = setup_content.get_data('container_type_fields')[container.type.identifier]
    for info in fields_info:
        if info['name']==field and info['type']=='OBJECT_TYPE_HISTORICAL':
            break
    
    if key_field!=None:
        wrk_id = epoch_time(datetime.datetime.strptime(value[key_field], '%Y-%m-%d'))
    else:
        wrk_id = None
    if info['instanceType']=='FIELD_ASSIGNMENT_SINGLE' or (info['instanceType']=='FIELD_ASSIGNMENT_LIMITED' and int(info['repeat'])==1):
        value['_id'] = wrk_id
        historical[collection_id].update({'_id':wrk_id}, value, True)
    else:
        content = historical[collection_id].find_one({'_id':wrk_id})
        if content==None:
            content = []
        else:
            content = content['content']
        if info['instanceType']=='FIELD_ASSIGNMENT_MULTIPLE' or ((info['instanceType']=='FIELD_ASSIGNMENT_LIMITED' and len(content)<int(info['repeat'])) or value.has_key['index']):
            if value.has_key['index']:
                new_content = []
                for element in content:
                    if element['index']==value['index']:
                        new_content.append(value)
                    else:
                        new_content.append(element)
                content = new_content
            else:
                content.append(value)
        else:
            None
        historical[collection_id].update({'_id':wrk_id}, {'_id': wrk_id, 'content': content}, True)

def get_container_history(container, field, ascending=True):
    collection_id = field + '_' + str(container.id)
    content = historical[collection_id].find().sort('_id',1 if ascending else -1)
    return content
    
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