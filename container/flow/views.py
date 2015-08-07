'''
Created on Aug 5, 2015

@author: sdejonckheere
'''
from django.shortcuts import render
from container.utilities.security import get_or_create_user_profile
from container.models import Attributes
from container.flow.modify import AVAILABLE_OPERATIONS
from json import dumps
from container.utilities import setup_content
import json
from django.http.response import HttpResponse

def crud(request):
    profile = get_or_create_user_profile(request.user.id)
    context = {'base_template': profile['base_template'],
               'profile': profile,
               'selection_template': 'statics/container_type_' + profile['language_code'] + '.html',
               'global': dumps(setup_content.get_data('container_flow_crud')),
               'operations': dumps(AVAILABLE_OPERATIONS),
               'steps': Attributes.objects.filter(type='crud_step', active=True).order_by('id')
               }
    return render(request, 'container/edit/flow/crud.html', context)

def crud_save(request):
    profile = get_or_create_user_profile(request.user.id)
    crud_data = request.POST['crud_data']
    crud_data = json.loads(crud_data)
    setup_content.set_data('container_flow_crud', crud_data)
    return HttpResponse('{"result": true, "status_message": "Saved"}',"json")
    
def status(request):
    profile = get_or_create_user_profile(request.user.id)
    context = {'base_template': profile['base_template'], 'profile': profile}
    return render(request, 'container/edit/flow/status.html', context)