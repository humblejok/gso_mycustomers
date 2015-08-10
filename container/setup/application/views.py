'''
Created on 26 juin 2015

@author: humble_jok
'''
from container.utilities.utils import complete_fields_information, get_static_fields, get_effective_container,\
    clean_post_value
from django.shortcuts import render
from django.http.response import HttpResponse
from container.utilities.setup_content import available_data_sets
from container.utilities import setup_content
import logging
from container.setup.application import settings
from django.template import loader
from django.template.context import Context
from container.models import UserMapping, ThirdPartyContainer, PersonContainer,\
    Attributes, Email
from django.contrib.auth.models import User
from container.utilities.security import get_or_create_user_profile

LOGGER = logging.getLogger(__name__)

def setup(request):
    profile = get_or_create_user_profile(request.user.id)
    # TODO Check permissions
    return render(request, 'container/edit/application/setup.html', {'base_template': profile['base_template'], 'profile': profile, 'application_settings': settings})

def save(request):
    if settings.SETTINGS_PATH.endswith('.pyc'):
        working_file = settings.SETTINGS_PATH[:-1]
    else:
        working_file = settings.SETTINGS_PATH
    LOGGER.info("Changing global settings:" + working_file)
    template = loader.get_template('rendition/application/settings.py')
    context = Context({'application_settings': request.POST})
    rendition = template.render(context)
    with open(working_file,'w') as o:
        o.write(rendition.encode('utf-8'))
    reload(settings)
    print settings.WORKING_PATH
    return HttpResponse('{"result": true, "status_message": "Saved"}',"json")

def reset_nosql(request):
    profile = get_or_create_user_profile(request.user.id)
    # TODO Check permissions
    return render(request, 'container/edit/application/reset_nosql.html', {'base_template': profile['base_template'], 'profile': profile, 'data_sets': available_data_sets.keys(), 'application_settings': settings})

def reset_nosql_execute(request):
    profile = get_or_create_user_profile(request.user.id)
    # TODO Check permissions
    for key_set in request.POST.keys():
        if key_set in available_data_sets.keys():
            LOGGER.info("Cleaning " + key_set)
            if available_data_sets[key_set]:
                setup_content.set_data(key_set, {})
            else:
                setup_content.drop_collection(key_set)
    return HttpResponse('{"result": true, "status_message": "Deleted"}',"json")

def setup_users(request):
    profile = get_or_create_user_profile(request.user.id)
    all_users = User.objects.all().order_by('username')
    # TODO Check permissions
    print complete_fields_information(UserMapping, get_static_fields(UserMapping), profile['language_code'])
    return render(request, 'container/edit/application/setup_users.html',
                  {'base_template': profile['base_template'], 'profile': profile, 'application_settings': settings,
                   'all_users': all_users, 'mapping_fields':complete_fields_information(UserMapping, get_static_fields(UserMapping), profile['language_code'])})

def get_user_assigment(request):
    profile = get_or_create_user_profile(request.user.id)
    mapping = UserMapping.objects.filter(related_user__id=request.POST['user_id']).order_by('third_container__type', 'third_container__name')
    context = {'thirds': mapping, 'language_code': profile['language_code'], 'application_settings': settings}
    return render(request, 'rendition/application/user_mapping.html', context)
    
def add_user_assigment(request):
    profile = get_or_create_user_profile(request.user.id)
    third = get_effective_container(request.POST['third_container_id'])
    mapping = UserMapping()
    mapping.related_user = User.objects.get(id=request.POST['user_id'])
    mapping.third_container = third
    mapping.save();
    return HttpResponse('{"result": true, "status_message": "Added"}',"json")
    
    
def remove_user_assigment(request):
    profile = get_or_create_user_profile(request.user.id)
    mapping = UserMapping.objects.get(id=request.POST['mapping_id']).delete()
    return HttpResponse('{"result": true, "status_message": "Removed"}',"json")

def create_edit_user(request):
    profile = get_or_create_user_profile(request.user.id)
    # TODO Check permissions
    if request.POST.has_key('id') and request.POST['id']!='':
        working_user = User.objects.get(id=request.POST['id'])
    else:
        working_user = User.objects.create(username=clean_post_value(request.POST['username']))
    if clean_post_value(request.POST['password'])!='':
        working_user.set_password(clean_post_value(request.POST['password']))
    for key in request.POST:
        if key not in ['id', 'password']:
            setattr(working_user,key, clean_post_value(request.POST[key]))
    working_user.save()
    if request.POST.has_key('create_person') and clean_post_value(request.POST['create_person'])=='True':
        person = PersonContainer.objects.filter(first_name__iexact=clean_post_value(request.POST['first_name']), last_name__iexact=clean_post_value(request.POST['last_name']))
        if person.exists() and len(person)==1:
            person = person[0]
        elif person.exists():
            person = person.filter(emails__email_address=clean_post_value(request.POST['email']))
            if person.exists() and len(person)==1:
                person = person[0]
            else:
                # TODO Add warning message: Too many possibilities
                person = None
        else:
            person = PersonContainer()
            person.type = Attributes.objects.get(active=True, identifier='CONT_PERSON')
            person.name = clean_post_value(request.POST['last_name']).upper() + ' ' + clean_post_value(request.POST['first_name'])
            person.last_name = clean_post_value(request.POST['last_name']).upper()
            person.first_name = clean_post_value(request.POST['first_name']).upper()
            person.save()
            if clean_post_value(request.POST['email'])!='':
                mail = Email()
                mail.address_type = Attributes.objects.get(active=True, identifier='EMAIL_CONTACT')
                mail.email_address = clean_post_value(request.POST['email']).lower()
                mail.save()
                person.emails.add()
                person.save()
        if person!=None:
            mapping = UserMapping()
            mapping.related_user = working_user
            mapping.third_container = person
            mapping.save();
    return HttpResponse('{"result": true, "status_message": "Created"}',"json")