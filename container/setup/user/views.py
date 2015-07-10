'''
Created on Apr 30, 2015

@author: sdejonckheere
'''
from django.shortcuts import render
from django.http.response import HttpResponse
from django.contrib.auth.models import User
from container.utilities.utils import clean_post_value
from container.utilities import setup_content
from container.models import Attributes
import logging
from container.utilities.security import get_or_create_user_profile

LOGGER = logging.getLogger(__name__)

def setup(request):
    profile = get_or_create_user_profile(request.user.id)
    return render(request, 'container/edit/user/setup.html', {'base_template': profile['base_template'], 'profile': profile})

def save(request):
    user = request.user
    user.username = request.POST['login']
    user.first_name = request.POST['first_name']
    user.last_name = request.POST['last_name']
    user.email = request.POST['email']
    user.save()
    
    language = clean_post_value(request.POST['language'])
    language_attribute = Attributes.objects.get(active=True, identifier=language)
    profile = get_or_create_user_profile(user.id)
    profile['base_template'] = 'gso_' + language_attribute.short_name + '.html'
    profile['language_code'] = language_attribute.short_name
    profile['language'] = language
    if request.POST['default_work_place'].lower()!='administrator':
        try:
            profile['default_work_place'] = next(data for (index, data) in enumerate(profile['available_work_places']) if data['third_name'] == request.POST['default_work_place'])
        except StopIteration:
            LOGGER.error("Could not find work place " + request.POST['default_work_place'] + " for user " + user.username)
    else:
        profile['default_work_place'] = 'administrator'
    if profile.has_key('current_work_as'):
        del profile['current_work_as']
    setup_content.set_data('user_profiles', profile, False)
    return HttpResponse('{"result": true, "status_message": "Saved"}',"json")

def set_work_as(request):
    profile = get_or_create_user_profile(request.user.id)
    try:
        profile['current_work_as'] = next(data for (index, data) in enumerate(profile['available_work_places']) if str(data['third_id']) == request.POST['third_id'])
        setup_content.set_data('user_profiles', profile, False)
    except StopIteration:
        LOGGER.error("Could not find work place with " + request.POST['third_id'] + " for user " + request.user.username)
    return HttpResponse('{"result": true, "status_message": "Saved"}',"json")

def remove(request):
    user = User.objects.get(id=request.user.id)
    user.is_active = False
    user.save()
    return HttpResponse('{"result": true, "status_message": "Saved"}',"json")