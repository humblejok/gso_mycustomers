'''
Created on Apr 27, 2015

@author: sdejonckheere
'''
from container.models import Attributes
from seq_common.utils import classes
from django.shortcuts import render
from container.utilities.utils import complete_custom_fields_information,clean_post_value,\
    complete_custom_historical_fields_information
from container.utilities.container_container import get_container_information,\
    enhance_container_information
from container.utilities.security import get_or_create_user_profile
from container.setup.application import settings
    
def render_singles_list(request):
    # TODO: Check user
    profile = get_or_create_user_profile(request.user.id)
    container_id = clean_post_value(request.POST['container_id'])
    container_type = clean_post_value(request.POST['container_type'])
    container_class = container_type + '_CLASS'
    container_fields = eval(clean_post_value(request.POST['container_fields']))
    widget_index = clean_post_value(request.POST['widget_index'])
    widget_title = clean_post_value(request.POST['widget_title'])
    # TODO: Handle error
    effective_class_name = Attributes.objects.get(identifier=container_class, active=True).name
    effective_class = classes.my_class_import(effective_class_name)

    container = effective_class.objects.get(id=container_id)
    context = {'base_template': profile['base_template'], 'profile': profile, 'title': widget_title, 'index':widget_index, 'container': container, 'fields': container_fields, 'application_settings': settings}
    return render(request, 'container/view/simple_fields_list.html', context)

def render_custom_standard(request):
    # TODO: Check user
    profile = get_or_create_user_profile(request.user.id)
    container_id = clean_post_value(request.POST['container_id'])
    container_type = clean_post_value(request.POST['container_type'])
    container_class = container_type + '_CLASS'
    container_fields = eval(clean_post_value(request.POST['container_fields']))
    widget_index = clean_post_value(request.POST['widget_index'])
    widget_title = clean_post_value(request.POST['widget_title'])
    # TODO: Handle error
    effective_class_name = Attributes.objects.get(identifier=container_class, active=True).name
    effective_class = classes.my_class_import(effective_class_name)

    container = effective_class.objects.get(id=container_id)
    
    effective_container_fields = complete_custom_fields_information(container_type, container_fields, profile['language_code'])
    custom_data = enhance_container_information(get_container_information(container), effective_container_fields)
                        
    context = {'base_template': profile['base_template'], 'profile': profile, 'title': widget_title, 'index':widget_index,
               'container': container, 'fields': effective_container_fields, 'custom_data': custom_data,
               'application_settings': settings}
    return render(request, 'container/view/custom_fields_list.html', context)

def render_custom_history(request):
    # TODO: Check user
    profile = get_or_create_user_profile(request.user.id)
    container_id = clean_post_value(request.POST['container_id'])
    container_type = clean_post_value(request.POST['container_type'])
    container_class = container_type + '_CLASS'
    container_fields = eval(clean_post_value(request.POST['container_fields']))
    widget_index = clean_post_value(request.POST['widget_index'])
    widget_title = clean_post_value(request.POST['widget_title'])
    # TODO: Handle error
    effective_class_name = Attributes.objects.get(identifier=container_class, active=True).name
    effective_class = classes.my_class_import(effective_class_name)

    container = effective_class.objects.get(id=container_id)
    
    effective_container_fields = complete_custom_historical_fields_information(container_type, container_fields, profile['language_code'])
    custom_data = enhance_container_information(get_container_information(container), effective_container_fields)
    context = {'base_template': profile['base_template'], 'profile': profile, 'title': widget_title,
               'index':widget_index, 'container': container, 'fields': effective_container_fields[container_fields[0]],
               'custom_data': custom_data, 'application_settings': settings}
    return render(request, 'container/view/custom_fields_history.html', context)

def render_custom_template(request):
    # TODO: Check user
    profile = get_or_create_user_profile(request.user.id)
    container_id = clean_post_value(request.POST['container_id'])
    container_type = clean_post_value(request.POST['container_type'])
    container_class = container_type + '_CLASS'
    container_template = clean_post_value(request.POST['container_template'])
    widget_index =clean_post_value(request.POST['widget_index'])
    widget_title = clean_post_value(request.POST['widget_title'])
    # TODO: Handle error
    effective_class_name = Attributes.objects.get(identifier=container_class, active=True).name
    effective_class = classes.my_class_import(effective_class_name)

    container = effective_class.objects.get(id=container_id)
    
    
    custom_data = get_container_information(container)
    
    context = {'base_template': profile['base_template'], 'profile': profile, 'title': widget_title, 'index':widget_index, 'container': container, 'custom_data': custom_data, 'application_settings': settings}
    return render(request, container_template, context)

def render_many_to_many(request):
    # TODO: Check user
    profile = get_or_create_user_profile(request.user.id)
    container_id = clean_post_value(request.POST['container_id'])
    container_type = clean_post_value(request.POST['container_type'])
    container_class = container_type + '_CLASS'
    container_field = clean_post_value(request.POST['container_field'])
    rendition_witdh = clean_post_value(request.POST['rendition_width'])
    widget_index = clean_post_value(request.POST['widget_index'])
    widget_title = clean_post_value(request.POST['widget_title'])
    # TODO: Handle error
    effective_class_name = Attributes.objects.get(identifier=container_class, active=True).name
    effective_class = classes.my_class_import(effective_class_name)

    foreign_class = effective_class._meta.get_field(container_field).rel.to

    container = effective_class.objects.get(id=container_id)
    context = {'base_template': profile['base_template'], 'profile': profile,
               'title': widget_title,
               'container_id': container_id, 'container_type': container_type, 'container_field': container_field,
               'index':widget_index,
               'data': getattr(container,container_field),
               'fields': foreign_class.get_displayed_fields(rendition_witdh),
               'application_settings': settings}
    return render(request, 'container/view/many_to_many_field.html', context)

def render_template_for_load(request):
    profile = get_or_create_user_profile(request.user.id)
    template_name = clean_post_value(request.POST['template_name'])
    if request.POST.has_key('selected_value'):
        selected_value = clean_post_value(request.POST['selected_value'])
    else:
        selected_value = ''
    context = {'value': selected_value, 'application_settings': settings}
    return render(request, 'statics/' + template_name + '_' + profile['language_code'] + '.html', context)