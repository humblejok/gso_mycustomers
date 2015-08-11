'''
Created on 10 mars 2014

@author: humble_jok
'''
from django import template
from json import dumps
from django.forms.models import model_to_dict
from container.models import CoreModel, Attributes, FieldLabel, Container
from container.utilities.utils import dict_to_json_compliance,\
    get_effective_class
import logging
from django.contrib.auth.models import User
from container.utilities import setup_content

LOGGER = logging.getLogger(__name__)

register = template.Library()

@register.filter()
def get_custom_root(field_name):
    return field_name.split('.')[0]

@register.filter()
def get_custom_field(field_name):
    return field_name.split('.')[1]

@register.filter()
def get_wizard_fields(container_type, target):
    clazz = get_effective_class(container_type)
    clazz = clazz._meta.get_field(target).rel.to
    return clazz.get_wizard_fields()  

@register.filter()
def get_edition_fields(container_type, target):
    clazz = get_effective_class(container_type)
    clazz = clazz._meta.get_field(target).rel.to
    return [clazz.get_filtering_field()] + clazz.get_wizard_fields()

@register.filter()
def get_translated_text(text_id, language):
    try:
        return FieldLabel.objects.get(identifier=text_id, language=language).field_label
    except:
        LOGGER.error('Could not find ' + str(text_id) + ' with language set to ' + str(language))
        return "NO TRANSLATION"
    
@register.filter()
def try_translated_text(text_id, language):
    try:
        return FieldLabel.objects.get(identifier=text_id, language=language).field_label
    except:
        return text_id

@register.filter()
def as_identifier(name):
    return name.lower().replace(' ','_')

@register.filter()
def get_dict_key(d, key):
    if type(d) is dict:
        if d.has_key(key):
            return d[key]
        elif d.has_key(str(key)):
            return d[str(key)]
        elif d.has_key(unicode(key)):
            return d[unicode(key)]
    return None

@register.filter()
def get_as_json_string(data):
    if isinstance(data, CoreModel):
        return dumps(dict_to_json_compliance(model_to_dict(data), data.__class__))
    else:
        return dumps(data)

@register.filter()
def get_field_value(data, field_chain):
    all_fields = field_chain.split('.')
    for field in all_fields:
        if data==None:
            break
        data = getattr(data, field)
    return data if data!=None else 'N/A'

@register.filter()
def get_value(data, field_chain):
    all_fields = field_chain.split('.')
    if data!=None:
        data = getattr(data, all_fields[0])
    if isinstance(data, Attributes):
        return data.identifier
    return data if data!=None else ''

@register.filter()
def get_escaped_strings(string_value):
    return string_value.replace('\\', '\\\\')

@register.filter()
def get_jquery_id(identity):
    return identity.replace('.', '\\\\.')

@register.filter()
def is_container(entity):
    return isinstance(entity, Container)

@register.filter()
def has_container_type(universe, container_type):
    return universe.members.filter(type__identifier=container_type).exists()

@register.filter()
def log_me(text):
    LOGGER.debug(str(text))
    return ""


@register.inclusion_tag('statics/objects_lists.html')
def get_objects_lists(language_code):
    objects_lists = setup_content.get_data('object_type_fields')
    del objects_lists['_id']
    print objects_lists
    return {'objects_lists': objects_lists, 'language_code': language_code}


@register.inclusion_tag('statics/application_users.html')
def get_users(user_id, value):
    users = User.objects.all()
    return {'users': users, 'value': value}
