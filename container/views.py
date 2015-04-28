'''
Created on Oct 3, 2014

@author: sdejonckheere
'''
import itertools
from json import dumps
import json
import logging
import os

from bson import json_util
from django.contrib.auth.models import User
from django.db.models import Q
from django.forms.models import model_to_dict
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from seq_common.utils import classes

from container.models import Attributes, FieldLabel, Container
from container.settings import WORKING_PATH
from container.utilities import external_content
from container.utilities.container_container import get_container_information, set_container_information
from container.utilities.setup_content import get_container_type_fields
from container.utilities.utils import get_static_fields, filter_custom_fields, \
    complete_fields_information, dict_to_json_compliance, \
    complete_custom_fields_information, get_model_foreign_field_class, \
    get_effective_instance
from utilities import setup_content


LOGGER = logging.getLogger(__name__)

def lists(request):
    # TODO: Check user
    container_type = request.GET['item']
    container_class = container_type + '_CLASS'
    # TODO: Handle error
    effective_class_name = Attributes.objects.get(identifier=container_class, active=True).name
    effective_class = classes.my_class_import(effective_class_name)
    results = effective_class.objects.all().order_by('name')
    context = {'base_template': 'gso_fr.html', 'containers': results, 'container_type': container_type, 'container_label': Attributes.objects.get(identifier=container_type).name}
    return render(request, 'statics/' + container_type + '_results_lists_en.html', context)

def definition_save(request):
    # TODO: Check user
    user = User.objects.get(id=request.user.id)
    container = request.POST['container']
    definitions = request.POST['definitions']
    definitions = json.loads(definitions)
    all_data = setup_content.get_container_type_fields()
    all_data[container] = definitions
    setup_content.set_container_type_fields(all_data)
    return HttpResponse('{"result": true, "status_message": "Saved"}',"json")

def base_edit(request):
    # TODO: Check user
    container_type = request.POST['container_type']
    container_class = container_type + '_CLASS'
    # TODO: Handle error
    effective_class_name = Attributes.objects.get(identifier=container_class, active=True).name
    effective_class = classes.my_class_import(effective_class_name)

    active_status = Attributes.objects.get(identifier='STATUS_ACTIVE')
    container_attribute = Attributes.objects.get(identifier=container_type)
    if request.POST.has_key('container_id'):
        portfolio_id = request.POST['container_id']
        try:
            source = effective_class.objects.get(Q(id=portfolio_id))
        except:
            # TODO: Return error message
            return redirect('/lists.html?item=' + container_type)
    else:
        source = effective_class()
    # Initial setup
    # TODO: Check if name already exists for that container type
    source.type = container_attribute
    source.name = request.POST['name']
    source.short_name = request.POST['short_name']
    source.status = active_status
    source.save()
    # Working on creations mandatory fields
    creation_data = setup_content.get_container_type_creations()
    if creation_data.has_key(container_type):
        creation_data = creation_data[container_type]
    else:
        creation_data = {}
    creation_data = complete_fields_information(effective_class,  creation_data)
    for field in creation_data.keys():
        if creation_data[field]['type'] in ['ForeignKey', 'ManyToManyField']:
            if creation_data[field]['type']=='ForeignKey':
                # TODO: Implement not attribute
                setattr(source, field, Attributes.objects.get(identifier=request.POST[field], active=True))
                source.save()
            else:
                target_class = classes.my_class_import(creation_data[field]['target_class'])
                new_instance = target_class.retrieve_or_create(source, 'FinaLE', request.POST[field + '-' + creation_data[field]['filter']], request.POST[field])
                setattr(source, field,[new_instance])
                source.save()
        else:
            setattr(source, field, request.POST[field])
    return redirect('/container/lists.html?item=' + container_type)

def delete(request):
    # TODO: Check user
    user = User.objects.get(id=request.user.id)
    container_id = request.GET['container_id']
    container_type = request.GET['container_type']
    container_class = container_type + '_CLASS'
    # TODO: Handle error
    effective_class_name = Attributes.objects.get(identifier=container_class, active=True).name
    effective_class = classes.my_class_import(effective_class_name)
    
    effective_class.objects.get(id=container_id).delete()
    return HttpResponse('{"result": true, "status_message": "Deleted"}',"json")

def get(request):
    # TODO: Check user
    user = User.objects.get(id=request.user.id)
    container_id = request.GET['container_id']
    container_type = request.GET['container_type']
    container_class = container_type + '_CLASS'
    # TODO: Handle error
    effective_class_name = Attributes.objects.get(identifier=container_class, active=True).name
    effective_class = classes.my_class_import(effective_class_name)
    
    container = effective_class.objects.get(id=container_id)
    filtering = lambda d, k: d[k]['data']
    fields = list(itertools.chain(*[filtering(setup_content.get_container_type_details()[container_type]['data'], k) for k in setup_content.get_container_type_details()[container_type]['data'].keys()]))
    custom_fields = complete_custom_fields_information(container_type)
    custom_data = get_container_information(container)
    # TODO: Handle other langage and factorize with other views
    labels = dict_to_json_compliance({label.identifier: label.field_label for label in FieldLabel.objects.filter(identifier__in=fields, langage='en')})
    context = {'base_template': 'gso_fr.html', 
               'custom_fields': custom_fields, 'complete_fields': complete_fields_information(effective_class,  {field:{} for field in fields}),
               'container': container, 'container_json': dumps(dict_to_json_compliance(model_to_dict(container), effective_class)),
               'custom_data': custom_data,
               'container_type': container_type, 'layout': setup_content.get_container_type_details()[container_type], 'labels': labels}
    return render(request,'rendition/container_type/details/view.html', context)

def filters(request):
    user = User.objects.get(id=request.user.id)
    if request.GET.has_key('container_type'):
        container_type = request.GET['container_type']
        container_class = container_type + '_CLASS'
        effective_class_name = Attributes.objects.get(identifier=container_class, active=True).name
    else:
        effective_class_name = request.GET['container_class']
    effective_class = classes.my_class_import(effective_class_name)
    if getattr(effective_class,'get_querying_class', None)!=None:
        effective_class = effective_class.get_querying_class()
    searching = request.GET['term']
    query_filter = None
    for field in effective_class.get_querying_fields():
        query_dict = {}
        field = field.replace('.','__') + '__icontains'
        query_dict[field] = searching
        if query_filter==None:
            query_filter = Q(**query_dict)
        else:
            query_filter = query_filter | Q(**query_dict)
    results = effective_class.objects.filter(query_filter).distinct()
    results = dumps([dict_to_json_compliance(model_to_dict(item)) for item in results], default=json_util.default)
    return HttpResponse('{"result": ' + results + ', "status_message": "Deleted"}',"json")

def partial_delete(request):
    # TODO: Check user
    user = User.objects.get(id=request.user.id)
    container_id = request.POST['container_id']
    container_type = request.POST['container_type']
    container_class = container_type + '_CLASS'
    container_field = request.POST['container_field']
    item_id = request.POST['item_id']
    # TODO: Handle error
    effective_class_name = Attributes.objects.get(identifier=container_class, active=True).name
    effective_class = classes.my_class_import(effective_class_name)
    container = effective_class.objects.get(id=container_id)
    foreign = get_model_foreign_field_class(effective_class, container_field)
    if foreign!=None:
        entry = foreign.objects.get(id=item_id)
        getattr(container, container_field).remove(entry)
        container.save()
    return HttpResponse('{"result": "Finished", "status_message": "Saved"}',"json")

def partial_save(request):
    # TODO: Check user
    user = User.objects.get(id=request.user.id)
    container_id = request.POST['container_id']
    container_custom = request.POST['container_custom']=='True'
    container_data = request.POST['container_data']
    container_data = json.loads(container_data)
    container_type = request.POST['container_type']
    container_class = container_type + '_CLASS'
    # TODO: Handle error
    effective_class_name = Attributes.objects.get(identifier=container_class, active=True).name
    effective_class = classes.my_class_import(effective_class_name)
    container = effective_class.objects.get(id=container_id)
    if container_data.has_key('many-to-many'):
        foreign = get_model_foreign_field_class(effective_class, container_data['many-to-many'])
        if foreign!=None:
            entry = foreign.retrieve_or_create('web', None, None, container_data)
            if container_data['id']!=None and container_data['id']!='':
                getattr(container, container_data['many-to-many']).remove(foreign.objects.get(id=container_data['id']))
            getattr(container, container_data['many-to-many']).add(entry)
            container.save()
    elif container_custom:
        for entry in container_data.keys():
            set_container_information(container, entry, container_data[entry], None)
    else:
        for field_key in container_data.keys():
            #TODO Handle relation
            field_info = Attributes()
            field_info.short_name = field_key.split('.')[0]
            field_info.name = field_key.split('.')[0]
            container.set_attribute('web', field_info, container_data[field_key])
    container.save()
    return HttpResponse('{"result": "Finished", "status_message": "Saved"}',"json")

def search(request):
    context = {'base_template': 'gso_fr.html'}
    try:
        searching = request.POST[u'searching']
        
        if not isinstance(searching, basestring):
            searching = searching[0]
        action = request.POST['action']
        # TODO: Check user
        user = User.objects.get(id=request.user.id)
        container_type = request.POST['container_type']
        container_class = container_type + '_CLASS'
        # TODO: Handle error
        effective_class_name = Attributes.objects.get(identifier=container_class, active=True).name
        effective_class = classes.my_class_import(effective_class_name)
        results = effective_class.objects.filter(Q(name__icontains=searching) | Q(short_name__icontains=searching) | Q(aliases__alias_value__icontains=searching)).order_by('name').distinct()
        results_list = [result.get_short_json() for result in results]
        context['securities'] = results_list
        context['action'] = action
    except:
        context['message'] = 'Error while querying for:' + searching
    return render(request, 'rendition/securities_list.html', context)

def fields_get(request):
    # TODO: Check user
    user = User.objects.get(id=request.user.id)
    container_class = request.POST['container_type'] + '_CLASS'
    # TODO: Handle error
    effective_class_name = Attributes.objects.get(identifier=container_class, active=True).name
    effective_class = classes.my_class_import(effective_class_name)
    object_static_fields = get_static_fields(effective_class)
    
    object_custom_fields = get_container_type_fields()
    if object_custom_fields.has_key(request.POST['container_type']):
        object_custom_fields = object_custom_fields[request.POST['container_type']]
    else:
        object_custom_fields = []
    [object_.update({'fields_group':filter_custom_fields(object_['type'], object_['name'])}) for object_ in object_custom_fields]
    return HttpResponse('{"static_fields": ' + dumps(object_static_fields) + ', "custom_fields": ' + dumps(object_custom_fields) + ', "status_message": "Found"}',"json")

def get_filtering_entry(request):
    user = User.objects.get(id=request.user.id)
    # TODO: Check user
    container_type = request.POST['container_type']
    filtered_field = request.POST['filtered_field']
    filtering_field = request.POST['filtering_field']
    
    container_class = container_type + '_CLASS'
    # TODO: Handle error
    effective_class_name = Attributes.objects.get(identifier=container_class, active=True).name
    effective_class = classes.my_class_import(effective_class_name)
    target_class = effective_class._meta.get_field(filtered_field).rel.to
    limit = dict(target_class._meta.get_field(str(filtering_field)).rel.limit_choices_to)
    limit['active'] = True
    results = dumps([model_to_dict(item) for item in target_class._meta.get_field(filtering_field).rel.to.objects.filter(**limit)])
    return HttpResponse('{"result": ' + results + ', "status_message": "Saved"}',"json")


def custom_edit(request):
    # TODO: Check user
    container_id = request.GET['container_id']
    custom_id = request.GET['custom']
    target = request.GET['target']
    container = Container.objects.get(id=container_id)
    container = get_effective_instance(container)
    context = {'base_template': 'gso_fr.html','container': container, 'all_types': {}}
    all_types = Attributes.objects.filter(type__startswith=custom_id).order_by('type').distinct('type')
    all_types_json = {}
    for a_type in all_types:
        all_types_json[a_type.type] = [attribute.get_short_json() for attribute in Attributes.objects.filter(type=a_type.type, active=True).order_by('identifier')]
    context['all_types_json'] = dumps(all_types_json);
    content = getattr(external_content, 'get_' + custom_id + "_" + target)()
    context['custom_data'] = content[container_id] if content.has_key(container_id) else getattr(external_content,'create_' + custom_id + '_' + target + '_entry')(container)
    context['custom_data_json'] = dumps(context['custom_data'])
    return render(request, 'external/' + custom_id + '/' + target +'/edit.html', context)

def custom_export(request):
    # TODO: Check user
    user = User.objects.get(id=request.user.id)
    container_id = request.GET['container_id']
    custom_id = request.GET['custom']
    target = request.GET['target']
    file_type = request.GET['file_type']
    container = Container.objects.get(id=container_id)
    container = get_effective_instance(container)
    external = classes.my_import('external.' + custom_id)
    content = getattr(external, 'export_' + target)(container, getattr(external_content, 'get_' + custom_id + "_" + target)()[str(container.id)])
    # TODO: handle mime-type
    if file_type=='excel':
        xlsx_mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        path = os.path.join(WORKING_PATH, custom_id + '_' + target + '_' + container.short_name + '.xlsx')
        content.save(path)
        with open(path,'rb') as f:
            content = f.read()
        response = HttpResponse(content,xlsx_mime)
        split_path = os.path.split(path)
        response['Content-Disposition'] = 'attachement; filename="' + split_path[len(split_path)-1] + '"'
    return response
        
def custom_save(request):
    # TODO: Check user
    container_id = request.POST['container_id']
    custom_id = request.POST['custom']
    target = request.POST['target']
    custom_data = request.POST['new_data']
    custom_data = json.loads(custom_data)
    content = getattr(external_content, 'get_' + custom_id + "_" + target)()
    content[container_id] = custom_data
    getattr(external_content, 'set_' + custom_id + "_" + target)(content)
    return HttpResponse('{"result": true, "status_message": "Saved"}',"json")

def custom_view(request):
    # TODO: Check user
    container_id = request.GET['container_id']
    custom_id = request.GET['custom']
    target = request.GET['target']
    container = Container.objects.get(id=container_id)
    container = get_effective_instance(container)
    context = {'base_template': 'gso_fr.html', 'container': container}
    return render(request, 'external/' + custom_id + '/' + target +'/view.html', context)