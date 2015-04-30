'''
Created on Apr 30, 2015

@author: sdejonckheere
'''
from django.shortcuts import render
from django.http.response import HttpResponse
from django.contrib.auth.models import User
from container.utilities.utils import clean_post_value
from container.utilities import setup_content

def setup(request):
    return render(request, 'container/edit/user/setup.html', {'language': 'fr'})

def save(request):
    user = User.objects.get(id=request.user.id)
    user.login = request.POST['login']
    user.first_name = request.POST['first_name']
    user.last_name = request.POST['last_name']
    user.email = request.POST['email']
    user.save()
    setup_content.set_data('user_profiles', {'_id': user.id, 'language':clean_post_value(request.POST['language'])}, False)
    return HttpResponse('{"result": true, "status_message": "Saved"}',"json")