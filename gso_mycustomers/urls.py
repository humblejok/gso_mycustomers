from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'gso_mycustomers.views.home', name='home'),
    # url(r'^gso_mycustomers/', include('gso_mycustomers.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Setup views
    url(r'^setup.html', 'inventory.views.setup', name='setup'),
    url(r'^menu_setup_render.html', 'inventory.views.menu_setup_render', name='menu_setup_render'),
    # Custom view
    url(r'^custom_edit.html', 'inventory.views.custom_edit', name='custom_edit'),
    url(r'^custom_view.html', 'inventory.views.custom_view', name='custom_view'),
    url(r'^custom_export.html', 'inventory.views.custom_export', name='custom_export'),
    url(r'^custom_save.html', 'inventory.views.custom_save', name='custom_save'),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^index.html$', 'inventory.views.index', name='index'),
    
    url(r'^containers.html', 'inventory.container.views.lists', name='containers'),
    url(r'^container_definition_save.html','inventory.container.views.definition_save', name='container_definition_save'),
    url(r'^container_delete.html', 'inventory.container.views.delete', name='container_delete'),
    url(r'^container_get.html', 'inventory.container.views.get', name='container_get'),
    url(r'^container_setup_save.html', 'inventory.container.views.setup_save', name='container_setup_save'),
    url(r'^container_search.html', 'inventory.container.views.search', name='container_search'),
    url(r'^container_base_edit.html', 'inventory.container.views.base_edit', name='container_base_edit'),
    url(r'^container_filter.html', 'inventory.container.views.filters', name='container_filter'),
    url(r'^container_render_many_to_many.html', 'inventory.container.views.render_many_to_many', name='container_render_many_to_many'),
    url(r'^container_render_singles_list.html', 'inventory.container.views.render_singles_list', name='container_render_singles_list'),
    url(r'^container_render_history_chart.html', 'inventory.container.views.render_history_chart', name='container_render_history_chart'),
    url(r'^container_render_custom_standard.html', 'inventory.container.views.render_custom_standard', name='container_render_custom_standard'),
    url(r'^container_render_custom_template.html', 'inventory.container.views.render_custom_template', name='container_render_custom_template'),
)
