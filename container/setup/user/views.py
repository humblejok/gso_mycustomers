'''
Created on Apr 30, 2015

@author: sdejonckheere
'''
from django.shortcuts import render
from django.http.response import HttpResponse
from django.contrib.auth.models import User
from container.utilities.utils import clean_post_value,\
    get_or_create_user_profile
from container.utilities import setup_content
from container.models import Attributes

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
    setup_content.set_data('user_profiles', {'_id': user.id, 'base_template': 'gso_' + language_attribute.short_name + '.html', 'language_code': language_attribute.short_name,'language': language}, False)
    return HttpResponse('{"result": true, "status_message": "Saved"}',"json")

def remove(request):
    user = User.objects.get(id=request.user.id)
    user.is_active = False
    user.save()
    return HttpResponse('{"result": true, "status_message": "Saved"}',"json")