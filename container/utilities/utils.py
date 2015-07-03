import datetime
import logging
from django.db.models.fields import FieldDoesNotExist
from django.forms.models import model_to_dict
from seq_common.utils import classes

from container.utilities import setup_content
import re
from django.contrib.auth.models import User
from seq_common.utils.classes import my_class_import

LOGGER = logging.getLogger(__name__)


# FROM https://code.djangoproject.com/wiki/StripWhitespaceMiddleware
class StripWhitespaceMiddleware(object):
    """
    Strips leading and trailing whitespace from response content.
    """

    def __init__(self):
        self.whitespace = re.compile('^\s*\n', re.MULTILINE)
        # self.whitespace_lead = re.compile('^\s+', re.MULTILINE)
        # self.whitespace_trail = re.compile('\s+$', re.MULTILINE)


    def process_response(self, request, response):
        if "text" in response['Content-Type']:
            if hasattr(self, 'whitespace_lead'):
                response.content = self.whitespace_lead.sub('', response.content)
            if hasattr(self, 'whitespace_trail'):
                response.content = self.whitespace_trail.sub('\n', response.content)
            # Uncomment the next line to remove empty lines
            if hasattr(self, 'whitespace'):
                response.content = self.whitespace.sub('', response.content)
            return response
        else:
            return response    

def recurse_company_structure(container):
    print "->" + str(container)
    company = get_effective_container(container.id)
    structure = [{'third_id':company.id, 'third_name': company.name, 'third_short_name': company.short_name}]
    if len(company.subsidiary.all())>0:
        for sub_company in company.subsidiary.all():
            print company.members
            structure += recurse_company_structure(sub_company)
    else:
        return structure
    

def get_or_create_user_profile(user_id):
    profile = setup_content.get_data('user_profiles', user_id)
    current_user = User.objects.get(id=user_id)
    universe_class = my_class_import('container.models.Universe')
    attributes_class = my_class_import('container.models.Attributes')
    mapping_class = my_class_import('container.models.UserMapping')
    administrator = User.objects.filter(is_active=True, is_superuser=True).order_by('id')[0]
    if profile==None or not profile:
        language_attribute = classes.my_class_import('container.models.Attributes').objects.get(active=True, identifier='AVAIL_LANGUAGE_EN')
        profile = {'_id': user_id, 'user_name': current_user.username, 'language':language_attribute.identifier, 'base_template': 'gso_' + language_attribute.short_name + '.html', 'language_code': language_attribute.short_name}
    if not profile.has_key('user_name') or profile['user_name']!=current_user.username:
        profile['user_name'] = current_user.username
    profile['is_staff'] = current_user.is_staff or current_user.is_superuser
    if not universe_class.objects.filter(public=False, owner=administrator, short_name=profile['user_name']).exists():
        profile_universe = universe_class()
        profile_universe.owner = administrator
        profile_universe.public = False
        profile_universe.description = 'Technical universe that allows the management of the global permissions for user:' + profile['user_name'] + '.'
        profile_universe.name = 'Ownership - ' + profile['user_name']
        profile_universe.short_name = profile['user_name']
        profile_universe.type = attributes_class.objects.get(active=True, type='container_type', identifier='CONT_UNIVERSE')
        profile_universe.inception_date = datetime.date.today()
        profile_universe.closed_date = None
        profile_universe.status = attributes_class.objects.get(active=True, type='status', identifier='STATUS_ACTIVE')
        profile_universe.save()
        profile['universe_id'] = profile_universe.id
    # TODO Cache that
    mappings = mapping_class.objects.filter(related_user__id=user_id)
    profile['available_work_places'] = []
    for mapping in mappings:
        if mapping.third_container.type.identifier=='CONT_COMPANY':
            profile['available_work_places'] += recurse_company_structure(mapping.third_container)
        else:
            profile['available_work_places'].append({'third_id':mapping.third_container.id, 'third_name': mapping.third_container.name, 'third_short_name': mapping.third_container.short_name})
    print profile['available_work_places']
    setup_content.set_data('user_profiles', profile, False)
    return profile

def filter_custom_fields(field_type, field_name):
    values = setup_content.get_data('object_type_fields')
    if values.has_key(field_type):
        values = values[field_type]
        for value in values:
            if value['name']==field_name:
                return value
    return None

def clean_post_value(value):
    if isinstance(value, list) and len(value)==1:
        return value[0]
    else:
        return value

def get_effective_class(container_type):
    effective_class_name = classes.my_class_import('container.models.Attributes').objects.get(identifier=container_type + '_CLASS', active=True).name
    effective_class = classes.my_class_import(effective_class_name)
    return effective_class

def get_effective_container(container_id):
    return get_effective_instance(classes.my_class_import('container.models.Container').objects.get(id=container_id))

def get_effective_instance(container):
    if container!=None:
        effective_class_name = classes.my_class_import('container.models.Attributes').objects.get(identifier=container.type.identifier + '_CLASS', active=True).name
        effective_class = classes.my_class_import(effective_class_name)
        effective_container = effective_class.objects.get(id=container.id)
        return effective_container
    else:
        return None

def batch(iterable, n = 1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx+n, l)]

def get_model_foreign_field_class(model_class, field):
    all_fields = get_static_fields(model_class)
    if all_fields[field].has_key('target_class'):
        return classes.my_class_import(all_fields[field]['target_class']), all_fields
    else:
        return None, None
    
def complete_custom_fields_information(container_type, filtering_fields=None):
    all_data = {}
   
    all_custom_fields = setup_content.get_data('container_type_fields')
    if all_custom_fields.has_key(container_type):
        all_fields_information = setup_content.get_data('object_type_fields')
        for field in all_custom_fields[container_type]:
            if all_fields_information.has_key(field['type']):
                for group in all_fields_information[field['type']]:
                    if group['name']==field['name']:
                        group_name = group['name'].replace(' ','-')
                        for field_info in group['fields']:
                            field_name = field_info['name'].replace(' ','-')
                            full_name = group_name + '.' + field_name
                            if field_info['type']=='FIELD_TYPE_CHOICE':
                                field_info['template'] = 'statics/' + field_info['attribute'] + '_en.html'
                            if filtering_fields==None or full_name in filtering_fields:
                                all_data[full_name] = field_info
    return all_data

def complete_fields_information(model_class, information, language_code='en'):
    all_fields = get_static_fields(model_class)
    attributes_class = classes.my_class_import('container.models.Attributes')
    for field in information:
        field_effective = field
        if '.' in field:
            fields_chain = field.split('.')
            field_effective = fields_chain[0]
        if all_fields.has_key(field_effective):
            information[field].update(all_fields[field_effective])
            if information[field]['type'] in ['ForeignKey', 'ManyToManyField']:
                #current_class = classes.my_class_import(information[field]['target_class'])
                #if hasattr(current_class, 'get_fields'):
                #    information[field]['options'] = getattr(current_class,'get_fields')()
                if information[field]['target_class']=='container.models.Attributes':
                    information[field]['template'] = 'statics/' + information[field]['link']['type'] + '_' + language_code + '.html'
                    information[field]['is_container'] = False
                elif information[field]['target_class']=='django.contrib.auth.models.User':
                    # TODO Find a way to automatize
                    information[field]['template'] = 'statics/application_users.html'
                    information[field]['is_container'] = False
                else:
                    information[field]['is_container'] = issubclass(classes.my_class_import(information[field]['target_class']), classes.my_class_import('container.models.Container'))
                    information[field]['is_container']
                    information[field]['target_class']
                    if information[field]['is_container']:
                        information[field]['container_type'] = attributes_class.objects.get(active=True, type='container_type_class', name=information[field]['target_class']).identifier.replace('_CLASS','')
#                    if information[field]['type']!='ForeignKey':
                    information[field]['template'] = 'statics/' + information[field]['fields'][information[field]['filter']]['link']['type'] + '_' + language_code + '.html'
                    information[field]['template_m2m'] = 'statics/' + attributes_class.objects.get(type='element_wizard', name=information[field]['target_class'], active=True).short_name + '_' + language_code + '.html'
                    information[field]['template_m2m_complete'] = 'statics/complete_' + attributes_class.objects.get(type='element_wizard', name=information[field]['target_class'], active=True).short_name + '_' + language_code + '.html'
                    information[field]['datasource'] = '/container_filter.html?container_class=' + information[field]['target_class']
    return information

def get_static_fields(clazz, trail = []):
    object_static_fields = {}
    #LOGGER.debug("Parsing ->" + str(clazz))
    for field_name in clazz._meta.get_all_field_names():
        try:
            if not field_name.endswith('_rel') and not field_name.endswith('_ptr'):
                #LOGGER.debug("\tField ->" + str(field_name))
                if clazz._meta.get_field(field_name).get_internal_type()=='ForeignKey' or clazz._meta.get_field(field_name).get_internal_type()=='ManyToManyField':
                    foreign_class = clazz._meta.get_field(field_name).rel.to
                    if clazz._meta.get_field(field_name).get_internal_type()=='ForeignKey':
                        linked_to = clazz._meta.get_field(field_name).rel.limit_choices_to
                        linked_to = dict(linked_to)
                    else:
                        linked_to = {}
                    if foreign_class.__name__!=clazz.__name__ and foreign_class.__name__ not in trail:
                        object_static_fields[field_name] = {'type': clazz._meta.get_field(field_name).get_internal_type(),
                                                            'fields': get_static_fields(foreign_class, trail + [foreign_class.__name__]),
                                                            'link': linked_to,
                                                            'filter': foreign_class.get_filtering_field() if getattr(foreign_class, 'get_filtering_field', None)!=None else None,
                                                            'target_class': foreign_class.__module__ + '.' + foreign_class.__name__}
                    else:
                        # TODO Get effective type, you'll never know if you won't need it in the future
                        object_static_fields[field_name] = {'type': 'FIELD_TYPE_CHOICE', 'link': linked_to}
                else:
                    object_static_fields[field_name] = {'type': get_internal_type(clazz._meta.get_field(field_name).get_internal_type())}
        except FieldDoesNotExist:
            None
    return object_static_fields

def get_internal_type(external_type):
    if external_type=='BooleanField':
        return 'FIELD_TYPE_CHOICE'
    elif external_type=='CharField':
        return 'FIELD_TYPE_TEXT'
    elif external_type=='TextField':
        return 'FIELD_TYPE_TEXT'
    elif external_type=='DateField':
        return 'FIELD_TYPE_DATE'
    elif external_type=='DateTimeField':
        return 'FIELD_TYPE_DATETIME'
    elif external_type=='AutoField':
        return 'FIELD_TYPE_INTEGER'
    elif external_type=='FloatField':
        return 'FIELD_TYPE_FLOAT'
    elif external_type=='IntegerField':
        return 'FIELD_TYPE_INTEGER'
    
    return 'FIELD_TYPE_TEXT'

def dict_to_json_compliance(data, data_type=None):
    if data_type!=None and not hasattr(data_type, '_meta'):
        data_type = None
    if isinstance(data, datetime.date):
        new_data = data.strftime('%Y-%m-%d')
    elif isinstance(data, datetime.datetime):
        new_data = data.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(data, dict):
        new_data = {}
        for key in data.keys():
            if data_type==None:
                new_data[key] = dict_to_json_compliance(data[key], data_type)
            else:
                if data_type._meta.get_field(key).get_internal_type()=='ForeignKey' and data[key]!=None:
                    foreign_class = data_type._meta.get_field(key).rel.to
                    new_data[key] = dict_to_json_compliance(model_to_dict(foreign_class.objects.get(id=data[key])))
                elif data_type._meta.get_field(key).get_internal_type()=='ManyToManyField':
                    foreign_class = data_type._meta.get_field(key).rel.to
                    new_data[key] = [dict_to_json_compliance(model_to_dict(foreign_class.objects.get(id=item))) for item in data[key]]
                else:
                    new_data[key] = dict_to_json_compliance(data[key])
    elif isinstance(data, list):
        new_data = [dict_to_json_compliance(item, data_type) for item in data]
    else:
        return data
    return new_data