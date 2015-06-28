'''
Created on Apr 24, 2015

@author: sdejonckheere
'''
from django.conf.urls import url, patterns

urlpatterns = patterns(
    '',
    #########################
    # Base container views  #
    #########################
    url(r'^lists.html', 'container.views.lists', name='containers'),
    url(r'^definition_save.html','container.views.definition_save', name='container_definition_save'),
    url(r'^delete.html', 'container.views.delete', name='container_delete'),
    url(r'^get.html', 'container.views.get', name='container_get'),
    url(r'^search.html', 'container.views.search', name='container_search'),
    url(r'^base_edit.html', 'container.views.base_edit', name='container_base_edit'),
    url(r'^filters.html', 'container.views.filters', name='container_filters'),
    url(r'^fields_get.html', 'container.views.fields_get', name='fields_get'),
    url(r'^get_filtering_entry.html', 'container.views.get_filtering_entry', name='get_filtering_entry'),
    url(r'^get_selectable_foreign.html', 'container.views.get_selectable_foreign', name='get_selectable_foreign'),
    url(r'^get_field_type.html', 'container.views.get_field_type', name='get_field_type'),
    
    url(r'^definition_save.html','container.views.definition_save', name='container_definition_save'),
    url(r'^element_save.html','container.views.element_save', name='container_element_save'),
    url(r'^element_delete.html','container.views.element_delete', name='container_element_delete'),
    url(r'^full_search.html','container.views.full_search', name='container_full_search'),    
    
    #########################
    # Rendition views       #
    #########################
    url(r'^rendition/render_many_to_many.html', 'container.rendition.views.render_many_to_many', name='container_render_many_to_many'),
    url(r'^rendition/render_singles_list.html', 'container.rendition.views.render_singles_list', name='container_render_singles_list'),
    #url(r'^render_history_chart.html', 'container.views.render_history_chart', name='container_render_history_chart'),
    url(r'^rendition/render_custom_standard.html', 'container.rendition.views.render_custom_standard', name='container_render_custom_standard'),
    url(r'^rendition/render_custom_template.html', 'container.rendition.views.render_custom_template', name='container_render_custom_template'),
    url(r'^rendition/render_template_for_load.html', 'container.rendition.views.render_template_for_load', name='container_render_template_for_load'),
    #########################
    # Setup views           #
    #########################
    url(r'^setup.html', 'container.setup.views.setup', name='setup'),
    url(r'^setup_save.html', 'container.setup.views.save', name='container_setup_save'),
    url(r'^menu/setup_render.html', 'container.setup.views.menu_render', name='menu_setup_render'),
    url(r'^object/create.html', 'container.setup.views.object_create', name='object_create'),
    url(r'^object/save.html', 'container.setup.views.object_save', name='object_save'),
    url(r'^object/delete.html', 'container.setup.views.object_delete', name='object_delete'),
    url(r'^user/setup.html', 'container.setup.user.views.setup', name='user_setup'),
    url(r'^user/remove.html', 'container.setup.user.views.remove', name='user_remove'),
    url(r'^user/save.html', 'container.setup.user.views.save', name='user_save'),
    url(r'^application/setup.html', 'container.setup.application.views.setup', name='application_setup'),
    url(r'^application/reset_nosql.html', 'container.setup.application.views.reset_nosql', name='application_reset_nosql'),
    url(r'^application/reset_nosql_execute.html', 'container.setup.application.views.reset_nosql_execute', name='application_reset_nosql_execute'),
    
    #########################
    # Custom views          #
    #########################
    url(r'^custom_edit.html', 'container.views.custom_edit', name='custom_edit'),
    url(r'^custom_view.html', 'container.views.custom_view', name='custom_view'),
    url(r'^custom_export.html', 'container.views.custom_export', name='custom_export'),
    #url(r'^custom_save.html', 'container.views.custom_save', name='custom_save'),

    )