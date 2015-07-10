'''
Created on Apr 27, 2015

@author: sdejonckheere
'''
from json import dumps
import json
import os

from django.contrib.auth.models import User
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.template import loader
from django.template.context import Context
from seq_common.utils import classes

from container.models import Attributes, MenuEntries
from container.utilities import setup_content
from container.utilities.utils import complete_fields_information
import logging
from container.setup.application.settings import TEMPLATES_STATICS_PATH
from container.utilities.security import get_or_create_user_profile

LOGGER = logging.getLogger(__name__)

def application(request):
    None

def setup(request):
    # TODO: Check user
    profile = get_or_create_user_profile(request.user.id)
    item = request.GET['item']
    item_view_type = request.GET['type']
    all_data = setup_content.get_data(item + '_' + item_view_type)
    context = {'base_template': profile['base_template'], 'profile': profile, 'data_set': Attributes.objects.filter(type=item), 'selection_template': 'statics/' + item + '_' + profile['language_code'] + '.html','global': dumps(all_data) if not all_data.has_key('global') else dumps(all_data['global']), 'user': {} if not all_data.has_key('user') else dumps(all_data['user'])}
    return render(request, 'rendition/' + item + '/' + item_view_type + '/setup.html', context)

def save(request):
    # TODO: Check user
    profile = get_or_create_user_profile(request.user.id)
    container_setup = request.POST['container_setup']
    container_setup = json.loads(container_setup)
    print container_setup
    item = request.POST['item']
    item_view_type = request.POST['type']
    item_render_name = request.POST['render_name']
    
    container_class = container_setup["type"] + '_CLASS'
    # TODO: Handle error
    effective_class_name = Attributes.objects.get(identifier=container_class, active=True).name
    effective_class = classes.my_class_import(effective_class_name)
    
    all_data = setup_content.get_data(item + '_' + item_view_type)
    all_data[container_setup["type"]] = container_setup['data']
    setup_content.set_data(item + '_' + item_view_type, all_data)
    if item_view_type=='fields':
        data_as_dict = container_setup["data"]
        # TODO Clean the mess
        if isinstance(container_setup["data"], list):
            data_as_dict = {}
            for field in container_setup["data"]:
                if '.' not in field:
                    data_as_dict[field] = {'name': field}
        context = Context({"fields":container_setup['fields'], "complete_fields": complete_fields_information(effective_class,  data_as_dict), "container" : container_setup["type"]})
        template = loader.get_template('rendition/' + item + '/' + item_view_type + '/' + item_render_name + '.html')
        rendition = template.render(context)
        # TODO Implement multi-langage
        outfile = os.path.join(TEMPLATES_STATICS_PATH, container_setup["type"] + '_' + item_render_name + '_' + item_view_type + '_en.html')
        with open(outfile,'w') as o:
            o.write(rendition.encode('utf-8'))
    elif item_view_type=='menus':
        headers = Attributes.objects.filter(active=True, type='container_menu_target').order_by('name')
        entries = {}
        for entry in container_setup['data']:
            if entry['entry_id']!=None:
                if not entries.has_key(entry['menu_target']):
                    entries[entry['menu_target']] = []
                entries[entry['menu_target']].append(MenuEntries.objects.get(id=entry['entry_id']))
        languages = Attributes.objects.filter(active=True, type='available_language')
        template = loader.get_template('rendition/gso.html')
        for language in languages:
            context = Context({'entries': entries, 'headers': headers, 'language_code': language.short_name})
            template = loader.get_template('rendition/' + item + '/' + item_view_type + '/' + item_render_name + '.html')
            rendition = template.render(context)
            outfile = os.path.join(TEMPLATES_STATICS_PATH, container_setup["type"] + '_' + item_render_name + '_' + item_view_type + '_' + language.short_name + '.html')
            with open(outfile,'w') as o:
                o.write(rendition.encode('utf-8'))
    elif item_view_type!='details':
        data_as_dict = container_setup["data"]
        # TODO Clean the mess
        if isinstance(container_setup["data"], list):
            data_as_dict = {}
            for field in container_setup["data"]:
                if '.' not in field:
                    data_as_dict[field] = {'name': field}
        languages = Attributes.objects.filter(active=True, type='available_language')
        for language in languages:
            context = Context({"fields": data_as_dict,
                               "complete_fields": complete_fields_information(effective_class,  data_as_dict, language.short_name),
                               "container" : container_setup["type"],
                               "language_code": profile['language_code']})
            template = loader.get_template('rendition/' + item + '/' + item_view_type + '/' + item_render_name + '.html')
            print 'rendition/' + item + '/' + item_view_type + '/' + item_render_name + '.html'
            rendition = template.render(context)
            outfile = os.path.join(TEMPLATES_STATICS_PATH, container_setup["type"] + '_' + item_render_name + '_' + item_view_type + '_' + language.short_name + '.html')
            with open(outfile,'w') as o:
                o.write(rendition.encode('utf-8'))
    return HttpResponse('{"result": true, "status_message": "Saved"}',"json")

def object_create(request):
    # TODO: Check user
    user = User.objects.get(id=request.user.id)
    name = request.POST['name']
    new_type = request.POST['newObjectType']
    all_data = setup_content.get_data('object_type_fields')
    if not all_data.has_key(new_type) or not isinstance(all_data[new_type], list):
        all_data[new_type] = []
    all_data[new_type].append({'name': name, 'fields':[]})
    setup_content.set_data('object_type_fields', all_data)
    return redirect(request.META.get('HTTP_REFERER') + '&name=' + name + '&newObjectType=' + new_type)

def object_save(request):
    # TODO: Check user
    user = User.objects.get(id=request.user.id)
    object_type = request.POST['object_type']
    object_name = request.POST['object_name']
    object_fields = request.POST['object_fields']
    object_fields = json.loads(object_fields)
    all_data = setup_content.get_data('object_type_fields')
    for element in all_data[object_type]:
        if element['name']==object_name:
            element['fields'] = object_fields
            context = Context({"element": element})
            template = loader.get_template('rendition/object_simple_wizard.html')
            rendition = template.render(context)
            # TODO Implement multi-langage
            outfile = os.path.join(TEMPLATES_STATICS_PATH, element['name'] + '_en.html')
            print outfile
            with open(outfile,'w') as o:
                o.write(rendition.encode('utf-8'))
    setup_content.set_data('object_type_fields', all_data)
    return HttpResponse('{"result": true, "status_message": "Saved"}',"json")

def object_delete(request):
    # TODO: Check user
    user = User.objects.get(id=request.user.id)
    object_type = request.POST['object_type']
    object_name = request.POST['object_name']
    all_data = setup_content.get_data('object_type_fields')
    new_list = []
    # TODO Pythonize this
    for element in all_data[object_type]:
        if element['name']==object_name:
            None
        else:
            new_list.append(element)
    all_data[object_type] = new_list
    setup_content.set_data('object_type_fields', all_data)
    return HttpResponse('{"result": true, "status_message": "Deleted"}',"json")

def menu_render(request):
    profile = get_or_create_user_profile(request.user.id)
    container_type = request.POST['container_type']
    menu_target = request.POST['menu_target']
    selected = None
    if request.POST.has_key('selected'):
        selected = request.POST['selected']
    entries = MenuEntries.objects.filter(menu_target__identifier=menu_target, container_type__identifier=container_type)
    context = {'base_template': profile['base_template'], 'profile': profile, 'entries': entries, 'selected': selected}
    return render(request, 'rendition/menu_setup_select_renderer.html', context)