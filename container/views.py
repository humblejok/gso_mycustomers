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
from django.http.response import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from seq_common.utils import classes

from container.models import Attributes, Container, Universe, DocumentContainer,\
    ThirdPartyContainer
from container.utilities import setup_content, external_content,\
    container_container
from container.utilities.container_container import get_container_information, \
    set_container_information, set_container_history
from container.utilities.utils import complete_fields_information, \
    dict_to_json_compliance, complete_custom_fields_information, get_effective_class, \
    get_effective_container, get_model_foreign_field_class, get_static_fields, filter_custom_fields,\
    complete_custom_historical_fields_information
from django.utils.datastructures import MultiValueDictKeyError
from container.setup.application.settings import WORKING_PATH, STORER
from container.utilities.security import get_or_create_user_profile,get_or_create_ownership_universes,\
    container_visible
import datetime
from container.storage import get_uuid
from container.flow import modify
from container.setup.application import settings

LOGGER = logging.getLogger(__name__)

def documents(request):
    profile = get_or_create_user_profile(request.user.id)
    pending_docs = DocumentContainer.objects.filter(status__identifier='STATUS_TO_BE_VALIDATED')
    global_docs = DocumentContainer.objects.filter(status__identifier='STATUS_ACTIVE', containers=None)
    context = {'base_template': profile['base_template'], 'profile': profile, 'globals': global_docs, 'pendings': pending_docs, 'application_settings': settings}
    return render(request, 'container/view/documents.html', context)

def document_upload(request):
    profile = get_or_create_user_profile(request.user.id)
    file_name = os.path.join(WORKING_PATH,request.FILES['uploaded_file'].name)
    with open(file_name, 'wb+') as destination:
        for chunk in request.FILES['uploaded_file'].chunks():
            destination.write(chunk)
    document = DocumentContainer()
    document.name = request.FILES['uploaded_file'].name
    document.short_name = os.path.splitext(request.FILES['uploaded_file'].name)[0]
    document.type = Attributes.objects.get(active=True, identifier='CONT_DOCUMENT')
    document.inception_date = datetime.date.today()
    document.status = Attributes.objects.get(active=True, identifier='STATUS_TO_BE_VALIDATED')
    document.last_technical_updater = request.user
    document.last_updater = ThirdPartyContainer.objects.get(id=profile['current_work_as']['third_id']) if profile.has_key('current_work_as') and profile['current_work_as'].lower()!='administrator' else None
    document.document_version_high = 1
    document.document_version_low = 0
    document.document_uid = get_uuid()
    document.document_phid = 0
    document.save()
    STORER.store_file(document, file_name)
    if profile.has_key('current_work_as') and str(profile['current_work_as']).lower()!='administrator':
        # Assign to universe
        working_universes = get_or_create_ownership_universes(profile['current_work_as'])
        working_universes[0].members.add(document)
    return HttpResponse('{"result": true, "status_message": "Saved"}',"json")

def lists(request):
    # TODO: Check user
    if not request.user.is_authenticated():
        return redirect('/accounts/login')
    profile = get_or_create_user_profile(request.user.id)
    container_type = request.GET['item']
    # TODO: Handle error
    effective_class = get_effective_class(container_type)
    if profile['is_staff'] or str(profile['current_work_as']).lower()=='administrator':
        results = effective_class.objects.all()
    elif effective_class==Universe:
        filter_query = Q(owner__id=profile['current_work_as']['third_id']) | Q(public=True)
        results = effective_class.objects.filter(filter_query)
    else:
        all_universes = get_or_create_ownership_universes(profile['current_work_as'])
        results = None
        for universe in all_universes:
            if results==None:
                results = universe.members.filter(type__identifier=container_type)
            else:
                results = results | universe.members.filter(type__identifier=container_type)
    results = [get_effective_container(result.id) for result in results]
    request.session['django_language'] = profile['language_code']
    context = {'base_template': profile['base_template'], 'profile': profile, 'containers': results,
               'container_type': container_type, 'container_label': Attributes.objects.get(identifier=container_type).name,
               'application_settings': settings}
    return render(request, 'statics/' + container_type + '_results_lists_en.html', context)

def definition_save(request):
    # TODO: Check user
    user = User.objects.get(id=request.user.id)
    container = request.POST['container']
    definitions = request.POST['definitions']
    definitions = json.loads(definitions)
    all_data = setup_content.get_data('container_type_fields')
    all_data[container] = definitions
    setup_content.set_data('container_type_fields', all_data)
    return HttpResponse('{"result": true, "status_message": "Saved"}',"json")

def base_edit(request):
    # TODO: Check user
    profile = get_or_create_user_profile(request.user.id)
    container_type = request.POST['container_type']
    # TODO: Handle error
    effective_class = get_effective_class(container_type)

    pending_status = Attributes.objects.get(identifier='STATUS_TO_BE_VALIDATED')
    container_attribute = Attributes.objects.get(identifier=container_type, active=True)
    if request.POST.has_key('container_id'):
        container_id = request.POST['container_id']
        try:
            source = effective_class.objects.get(Q(id=container_id))
        except:
            # TODO: Return error message
            return redirect(request.META.get('HTTP_REFERER'))
    else:
        container_id = None
        source = effective_class()
    # Initial setup
    # TODO: Check if name already exists for that container type
    source.type = container_attribute
    # PRE SAVE UPDATE
    modify.execute_modify(source, 'STEP_PRE_CREATE')
    for post_field in request.POST.keys():
        field_info = Attributes()
        field_info.short_name = post_field
        field_info.name = post_field
        source.set_attribute('web', field_info, request.POST[post_field])

    source.status = pending_status
    source.save()
    # Working on creations mandatory fields
    creation_data = setup_content.get_data('container_type_creations')
    if creation_data.has_key(container_type):
        creation_data = creation_data[container_type]
    else:
        creation_data = {}
    creation_data = complete_fields_information(effective_class,  creation_data)
    for field in creation_data.keys():
        if creation_data[field]['type'] in ['ForeignKey', 'ManyToManyField']:
            if creation_data[field]['type']=='ForeignKey':
                # TODO: Implement not attribute
                foreign_class, fields_information = get_model_foreign_field_class(effective_class, field)
                if foreign_class==Attributes:
                    setattr(source, field, Attributes.objects.get(identifier=request.POST[field], active=True))
                else:
                    try:
                        setattr(source, field, foreign_class.objects.get(id=request.POST[field]))
                    except ValueError:
                        setattr(source, field, foreign_class.objects.get(Q(name=request.POST[field])|Q(short_name=request.POST[field])))
            else:
                target_class = classes.my_class_import(creation_data[field]['target_class'])
                keys_set = [key for key in request.POST.keys() if key.startswith(field)]
                index = 0
                new_instances = []
                while (field + "_" + str(index)) in keys_set:
                    base_key = field + "_" + str(index)
                    current_keys = [key for key in keys_set if key.startswith(base_key)]
                    data = {}
                    for key in current_keys:
                        if key==base_key:
                            data[creation_data[field]['filter']] = request.POST[base_key]
                        else:
                            data[key.replace(base_key + '.', '')] = request.POST[key]
                    new_instance = target_class.retrieve_or_create('web', 'FinaLE', field, data)
                    new_instances.append(new_instance)
                    index = index + 1
                setattr(source, field,new_instances)
                source.save()
        else:
            try:
                setattr(source, field, request.POST[field])
            except MultiValueDictKeyError:
                if creation_data[field]['type']=='FIELD_TYPE_CHOICE':
                    setattr(source, field, False)
                else:
                    LOGGER.error(field + " - Received data are incomplete, it does not match the creation requirements!")
    modify.execute_modify(source, 'STEP_POST_CREATE')
    source.save()
    if container_id==None and profile.has_key('current_work_as') and str(profile['current_work_as']).lower()!='administrator':
        # Assign to universe
        working_universes = get_or_create_ownership_universes(profile['current_work_as'])
        working_universes[0].members.add(source)
    return redirect(request.META.get('HTTP_REFERER'))

def delete(request):
    profile = get_or_create_user_profile(request.user.id)
    container_id = request.GET['container_id']
    if container_visible(container_id, profile):
        # TODO: Handle error
        container = get_effective_container(container_id)
        modify.execute_modify(container, 'STEP_PRE_DELETE')
        container.delete()
        modify.execute_modify(container, 'STEP_POST_DELETE')
        return HttpResponse('{"result": true, "status_message": "Deleted"}',"json")

def get(request):
    # TODO: Check user
    profile = get_or_create_user_profile(request.user.id)
    container_id = request.GET['container_id']
    container_type = request.GET['container_type']
    if container_visible(container_id, profile):
        # TODO: Handle error
        effective_class = get_effective_class(container_type)
        container = get_effective_container(container_id)
        filtering = lambda d, k: d[k]['data']
        working_data = setup_content.get_data('container_type_details')
        fields = list(itertools.chain(*[filtering(working_data[container_type]['data'], k) for k in working_data[container_type]['data'].keys()]))
        custom_fields = complete_custom_fields_information(container_type, language_code=profile['language_code'])
        custom_history_fields = complete_custom_historical_fields_information(container_type, language_code=profile['language_code'])
        custom_data = get_container_information(container)
        context = {'base_template': profile['base_template'], 'profile': profile, 
                   'custom_fields': custom_fields, 'custom_history_fields': custom_history_fields, 'complete_fields': complete_fields_information(effective_class,  {field:{} for field in fields}, profile['language_code']),
                   'container': container, 'container_json': dumps(dict_to_json_compliance(model_to_dict(container), effective_class)),
                   'custom_data': custom_data, 'application_settings': settings,
                   'container_type': container_type, 'layout': working_data[container_type]}
        return render(request,'rendition/container_type/details/view.html', context)
    else:
        return HttpResponseForbidden()
        
def reset_container_custom_information(request):
    profile = get_or_create_user_profile(request.user.id)
    container_id = request.GET['container_id']
    if container_visible(container_id, profile):
        # TODO: Handle error
        container = get_effective_container(container_id)
        container_container.reset_container_information(container)
        return HttpResponse('{"result": true, "status_message": "Deleted"}',"json")
    else:
        return HttpResponseForbidden()

def get_field_type(request):
    profile = get_or_create_user_profile(request.user.id)
    
    container_type = request.POST['container_type']
    current_field = request.POST['current_field']
    
    all_fields = get_static_fields(get_effective_class(container_type))
    return HttpResponse(all_fields[current_field]['type']) 

def get_selectable_foreign(request):
    profile = get_or_create_user_profile(request.user.id)
    
    container_type = request.POST['container_type']
    foreign_field = request.POST['foreign_field']

    foreign_class, fields_information = get_model_foreign_field_class(get_effective_class(container_type), foreign_field)
    if foreign_class==Attributes:
        return render(request, 'statics/' + fields_information[foreign_field]['link']['type'] + '_' + profile['language_code'] + '.html')
    elif foreign_class==User:
        # TODO Add visibility rules
        users = User.objects.all()
        return render(request, 'statics/application_users.html', {'users': users})
    print foreign_class
    print fields_information[foreign_field]

def filters(request):
    profile = get_or_create_user_profile(request.user.id)
    if request.GET.has_key('container_type'):
        container_type = request.GET['container_type']
        container_class = container_type + '_CLASS'
        effective_class_name = Attributes.objects.get(identifier=container_class, active=True).name
    else:
        effective_class_name = request.GET['container_class']
    searching = request.GET['term']
    effective_class = classes.my_class_import(effective_class_name)
    if getattr(effective_class,'get_querying_class', None)!=None:
        effective_class = effective_class.get_querying_class()
    
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
    # TODO Optimize
    results = [result for result in results if container_visible(result.id, profile)]
    results = dumps([dict_to_json_compliance(model_to_dict(item)) for item in results], default=json_util.default)
    return HttpResponse('{"result": ' + results + ', "status_message": "Found"}',"json")

def element_delete(request):
    # TODO: Check user
    profile = get_or_create_user_profile(request.user.id)
    container_id = request.POST['container_id']
    container_type = request.POST['container_type']
    container_field = request.POST['container_field']
    item_id = request.POST['item_id']
    if container_visible(container_id, profile):
        # TODO: Handle error
        effective_class = get_effective_class(container_type)
        container = get_effective_container(container_id)
        foreign, all_fields = get_model_foreign_field_class(effective_class, container_field)
        if foreign!=None:
            entry = foreign.objects.get(id=item_id)
            getattr(container, container_field).remove(entry)
            container.save()
        return HttpResponse('{"result": "Finished", "status_message": "Saved"}',"json")
    else:
        return HttpResponseForbidden()

def element_save(request):
    # TODO: Check user
    profile = get_or_create_user_profile(request.user.id)
    user = User.objects.get(id=request.user.id)
    container_id = request.POST['container_id']
    container_custom = request.POST['container_custom']=='True'
    container_data = request.POST['container_data']
    container_data = json.loads(container_data)
    container_type = request.POST['container_type']
    if container_visible(container_id, profile):
        # TODO: Handle error
        effective_class = get_effective_class(container_type)
        container = get_effective_container(container_id)
        modify.execute_modify(container, 'STEP_PRE_SAVE')
        if container_data.has_key('many-to-many'):
            foreign, all_fields = get_model_foreign_field_class(effective_class, container_data['many-to-many'])
            if foreign!=None:
                if issubclass(foreign, Container):
                    try:
                        entry = foreign.objects.get(id=container_data['id'])
                    except:
                        entry = foreign()
                        for field_key in [key for key in container_data.keys() if key not in ['many-to-many']]:
                            field_info = Attributes()
                            field_info.short_name = field_key
                            field_info.name = field_key
                            entry.set_attribute('web', field_info, container_data[field_key])
                        entry.save()
                else:
                    entry = foreign.retrieve_or_create('web', None, None, container_data)
                if container_data['id']!=None and container_data['id']!='':
                    getattr(container, container_data['many-to-many']).remove(foreign.objects.get(id=container_data['id']))
                getattr(container, container_data['many-to-many']).add(entry)
                container.save()
        elif container_custom:
            if container_data.has_key('history') and container_data['history']=='True':
                current_history_field = container_data['field']
                del container_data['history']
                del container_data['field']
                set_container_history(container, current_history_field, container_data, None)
            else:
                for entry in container_data.keys():
                    set_container_information(container, entry, container_data[entry], None)
        else:
            for field_key in container_data.keys():
                #TODO Handle relation
                field_info = Attributes()
                field_info.short_name = field_key.split('.')[0]
                field_info.name = field_key.split('.')[0]
                container.set_attribute('web', field_info, container_data[field_key])
        modify.execute_modify(container, 'STEP_POST_SAVE')
        container.save()
        return HttpResponse('{"result": "Finished", "status_message": "Saved"}',"json")
    else:
        return HttpResponseForbidden()

def full_search(request):
    profile = get_or_create_user_profile(request.user.id)
    container_type = request.POST['container_type']
    container_data = request.POST['container_data']
    container_data = json.loads(container_data)
    results = []
    context = {'base_template': profile['base_template'], 'profile': profile, 'application_settings': settings}
    if container_data.has_key('type') and container_data['type']!=None and container_data['type']!='':
        effective_class = get_effective_class(container_type)
        if container_data.has_key('many-to-many'):
            foreign, all_fields = get_model_foreign_field_class(effective_class, container_data['many-to-many'])
            del container_data['many-to-many']
        else:
            foreign = effective_class
            all_fields = get_static_fields(foreign)
        del container_data['id']
        query_filter = {(key + '__identifier' if all_fields.has_key(key) and all_fields[key]['type']=='ForeignKey' and all_fields[key]['target_class']=='container.models.Attributes' else key):container_data[key] for key in container_data.keys() if container_data[key]!='' and container_data[key]!=None}
        query_filter = {(key + '__icontains' if all_fields.has_key(key) and all_fields[key]['type']=='FIELD_TYPE_TEXT' else key):query_filter[key] for key in query_filter.keys()}
        query_Q = {key:container_data[key] for key in query_filter.keys() if all_fields.has_key(key) and all_fields[key]['type'] in ['ForeignKey','ManyToManyField']}
        query_Q_filters = []
        for key in query_Q.keys():
            query_Q_filters.append(Q({key + '__name__icontains':container_data[key]}) | Q({key + '__short_name__icontains':container_data[key]}))
            del query_filter[key]
        first = foreign.objects.filter(**query_filter)
        results = first.filter(*query_Q_filters)
    context['results'] = results
    return render(request, 'container/view/search_results.html', context)


def search(request):
    profile = get_or_create_user_profile(request.user.id)
    context = {'base_template': profile['base_template'], 'profile': profile}
    try:
        searching = request.POST[u'searching']
        
        if not isinstance(searching, basestring):
            searching = searching[0]
        action = request.POST['action']
        # TODO: Check user
        user = User.objects.get(id=request.user.id)
        # TODO: Handle error
        effective_class = get_effective_class(request.POST['container_type'])
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
    # TODO: Handle error
    effective_class = get_effective_class(request.POST['container_type'])
    object_static_fields = get_static_fields(effective_class)
    
    object_custom_fields = setup_content.get_data('container_type_fields')
    if object_custom_fields.has_key(request.POST['container_type']):
        object_custom_fields = object_custom_fields[request.POST['container_type']]
    else:
        object_custom_fields = []
    [object_.update({'fields_group':filter_custom_fields(object_['type'], object_['name'])}) for object_ in object_custom_fields]
    return HttpResponse('{"static_fields": ' + dumps(object_static_fields) + ', "custom_fields": ' + dumps(object_custom_fields) + ', "status_message": "Found"}',"json")

def get_filtering_entry(request):
    user = User.objects.get(id=request.user.id)
    # TODO: Check user
    filtered_field = request.POST['filtered_field']
    filtering_field = request.POST['filtering_field']
    effective_class = get_effective_class(request.POST['container_type'])
    target_class = effective_class._meta.get_field(filtered_field).rel.to
    limit = dict(target_class._meta.get_field(str(filtering_field)).rel.limit_choices_to)
    limit['active'] = True
    results = dumps([model_to_dict(item) for item in target_class._meta.get_field(filtering_field).rel.to.objects.filter(**limit)])
    return HttpResponse('{"result": ' + results + ', "status_message": "Saved"}',"json")


def custom_edit(request):
    # TODO: Check user
    profile = get_or_create_user_profile(request.user.id)
    container_id = request.GET['container_id']
    custom_id = request.GET['custom']
    target = request.GET['target']
    container = get_effective_container(container_id)
    context = {'base_template': profile['base_template'], 'profile': profile,'container': container, 'all_types': {}, 'application_settings': settings}
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
    container = get_effective_container(container_id)
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
    profile = get_or_create_user_profile(request.user.id)
    container_id = request.GET['container_id']
    custom_id = request.GET['custom']
    target = request.GET['target']
    container = get_effective_container(container_id)
    context = {'base_template': profile['base_template'], 'profile': profile, 'container': container}
    return render(request, 'external/' + custom_id + '/' + target +'/view.html', context)