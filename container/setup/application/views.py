'''
Created on 26 juin 2015

@author: humble_jok
'''
from container.utilities.utils import get_or_create_user_profile
from django.shortcuts import render
from django.http.response import HttpResponse
from container.utilities.setup_content import available_data_sets
from container.utilities import setup_content
import logging

LOGGER = logging.getLogger(__name__)

def setup(request):
    profile = get_or_create_user_profile(request.user.id)
    # TODO Check permissions
    return render(request, 'container/edit/application/setup.html', {'base_template': profile['base_template'], 'profile': profile})

def reset_nosql(request):
    profile = get_or_create_user_profile(request.user.id)
    # TODO Check permissions
    return render(request, 'container/edit/application/reset_nosql.html', {'base_template': profile['base_template'], 'profile': profile, 'data_sets': available_data_sets})

def reset_nosql_execute(request):
    profile = get_or_create_user_profile(request.user.id)
    # TODO Check permissions
    for key_set in request.POST.keys():
        LOGGER.info("Cleaning " + key_set)
        if key_set in available_data_sets:
            setup_content.set_data(key_set, {})
    return HttpResponse('{"result": true, "status_message": "Deleted"}',"json")