'''
Created on Apr 27, 2015

@author: sdejonckheere
'''
from container.models import Attributes, FieldLabel
from seq_common.utils import classes
from django.shortcuts import render
from container.utilities.utils import complete_custom_fields_information,\
    get_or_create_user_profile
from container.utilities.container_container import get_container_information,\
    enhance_container_information
    
def render_singles_list(request):
    # TODO: Check user
    profile = get_or_create_user_profile(request.user.id)
    container_id = request.POST['container_id'][0] if isinstance(request.POST['container_id'], list) else request.POST['container_id']
    container_type = request.POST['container_type'][0] if isinstance(request.POST['container_type'], list) else request.POST['container_type']
    container_class = container_type + '_CLASS'
    container_fields = eval(request.POST['container_fields'])
    widget_index = request.POST['widget_index'][0] if isinstance(request.POST['widget_index'], list) else request.POST['widget_index']
    widget_title = request.POST['widget_title'][0] if isinstance(request.POST['widget_title'], list) else request.POST['widget_title']
    # TODO: Handle error
    effective_class_name = Attributes.objects.get(identifier=container_class, active=True).name
    effective_class = classes.my_class_import(effective_class_name)

    container = effective_class.objects.get(id=container_id)
    context = {'base_template': profile['base_template'], 'profile': profile, 'title': widget_title, 'index':widget_index, 'container': container, 'fields': container_fields}
    return render(request, 'container/view/simple_fields_list.html', context)

def render_custom_standard(request):
    # TODO: Check user
    profile = get_or_create_user_profile(request.user.id)
    container_id = request.POST['container_id'][0] if isinstance(request.POST['container_id'], list) else request.POST['container_id']
    container_type = request.POST['container_type'][0] if isinstance(request.POST['container_type'], list) else request.POST['container_type']
    container_class = container_type + '_CLASS'
    container_fields = eval(request.POST['container_fields'])
    widget_index = request.POST['widget_index'][0] if isinstance(request.POST['widget_index'], list) else request.POST['widget_index']
    widget_title = request.POST['widget_title'][0] if isinstance(request.POST['widget_title'], list) else request.POST['widget_title']
    # TODO: Handle error
    effective_class_name = Attributes.objects.get(identifier=container_class, active=True).name
    effective_class = classes.my_class_import(effective_class_name)

    container = effective_class.objects.get(id=container_id)
    
    effective_container_fields = complete_custom_fields_information(container_type, container_fields)
    
    custom_data = enhance_container_information(get_container_information(container), effective_container_fields)
                        
    context = {'base_template': profile['base_template'], 'profile': profile, 'title': widget_title, 'index':widget_index, 'container': container, 'fields': effective_container_fields, 'custom_data': custom_data}
    return render(request, 'container/view/custom_fields_list.html', context)

def render_custom_template(request):
    # TODO: Check user
    profile = get_or_create_user_profile(request.user.id)
    container_id = request.POST['container_id'][0] if isinstance(request.POST['container_id'], list) else request.POST['container_id']
    container_type = request.POST['container_type'][0] if isinstance(request.POST['container_type'], list) else request.POST['container_type']
    container_class = container_type + '_CLASS'
    container_template = request.POST['container_template']
    widget_index = request.POST['widget_index'][0] if isinstance(request.POST['widget_index'], list) else request.POST['widget_index']
    widget_title = request.POST['widget_title'][0] if isinstance(request.POST['widget_title'], list) else request.POST['widget_title']
    # TODO: Handle error
    effective_class_name = Attributes.objects.get(identifier=container_class, active=True).name
    effective_class = classes.my_class_import(effective_class_name)

    container = effective_class.objects.get(id=container_id)
    
    
    custom_data = get_container_information(container)
    
    context = {'base_template': profile['base_template'], 'profile': profile, 'title': widget_title, 'index':widget_index, 'container': container, 'custom_data': custom_data}
    return render(request, container_template, context)

def render_many_to_many(request):
    # TODO: Check user
    profile = get_or_create_user_profile(request.user.id)
    container_id = request.POST['container_id'][0] if isinstance(request.POST['container_id'], list) else request.POST['container_id']
    container_type = request.POST['container_type'][0] if isinstance(request.POST['container_type'], list) else request.POST['container_type']
    container_class = container_type + '_CLASS'
    container_field = request.POST['container_field'][0] if isinstance(request.POST['container_field'], list) else request.POST['container_field']
    rendition_witdh = request.POST['rendition_width'][0] if isinstance(request.POST['rendition_width'], list) else request.POST['rendition_width']
    widget_index = request.POST['widget_index'][0] if isinstance(request.POST['widget_index'], list) else request.POST['widget_index']
    widget_title = request.POST['widget_title'][0] if isinstance(request.POST['widget_title'], list) else request.POST['widget_title']
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
               'fields': foreign_class.get_displayed_fields(rendition_witdh)}
    return render(request, 'container/view/many_to_many_field.html', context)