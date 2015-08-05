'''
Created on Aug 5, 2015

@author: sdejonckheere
'''
from django.shortcuts import render
from container.utilities.security import get_or_create_user_profile
from container.models import Attributes
from container.flow.modify import AVAILABLE_OPERATIONS
from json import dumps

def crud(request):
    profile = get_or_create_user_profile(request.user.id)
    context = {'base_template': profile['base_template'],
               'profile': profile,
               'selection_template': 'statics/container_type_' + profile['language_code'] + '.html',
               'global': {},
               'operations': dumps(AVAILABLE_OPERATIONS),
               'steps': Attributes.objects.filter(type='crud_step', active=True).order_by('id')
               }
    return render(request, 'container/edit/flow/crud.html', context)
    
def status(request):
    profile = get_or_create_user_profile(request.user.id)
    context = {'base_template': profile['base_template'], 'profile': profile}
    return render(request, 'container/edit/flow/status.html', context)