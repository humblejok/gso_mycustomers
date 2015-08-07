'''
Created on Aug 5, 2015

@author: sdejonckheere
'''
from container.models import Attributes
from container.utilities.utils import get_effective_instance
from container.setup.application.settings import STORER
from django.template import loader
from django.template.context import Context
import os
from gso_mycustomers.settings import TEMPLATE_DIRS
from container.utilities import setup_content
import sys

AVAILABLE_OPERATIONS = {
                    'set_field': {
                        'name': 'set_field',
                        'arguments': ['field','value'],
                        'target': None
                        },
                   'compute':{
                        'name': 'compute',
                        'arguments': ['field', 'formula'],
                        'target': None
                        },
                   'auto_validate':{
                        'name': 'auto_validate',
                        'arguments': [],
                        'target': None
                        },
                   'clean_document':{
                        'name': 'clean_document',
                        'arguments': [],
                        'target': ['CONT_DOCUMENT']
                        }
                   }

SELF = sys.modules[__name__]

def execute_modify(container, operation):
    crud_flow = setup_content.get_data('container_flow_crud')
    if crud_flow.has_key(container.type.identifier):
        if crud_flow[container.type.identifier].has_key(operation):
            for operation_step in crud_flow[container.type.identifier][operation]:
                getattr(SELF, operation_step['step'])(container, **operation_step)

def set_field(container, **kwargs):
    field_info = Attributes()
    field_info.short_name = kwargs['field']
    container.set_attribute('flow', field_info, kwargs['value'])
    
def compute(container, **kwargs):
    value = container.process_formula(kwargs['formula'])
    set_field(container, field=kwargs['field'], value=value)
    
def auto_validate(container, **kwargs):
    set_field(container, field='status', value='STATUS_ACTIVE')
    
def clean_document(container, **kwargs):
    STORER.delete_file(get_effective_instance(container))
    
def generate_wizards():
    all_types = Attributes.objects.filter(type='container_type', active=True)
    languages = Attributes.objects.filter(active=True, type='available_language')
    for a_type in all_types:
        avail_ops = []
        for operation in AVAILABLE_OPERATIONS.keys():
            if AVAILABLE_OPERATIONS[operation]['target']==None or a_type.identifier in AVAILABLE_OPERATIONS[operation]['target']:
                avail_ops.append(AVAILABLE_OPERATIONS[operation])
                template = loader.get_template('container/edit/flow/arguments_editor.html')
                # TODO Implement field analysis
                for language in languages:
                    context = Context({'operation': AVAILABLE_OPERATIONS[operation], 'language_code': language.short_name})
                    rendition = template.render(context)
                    outfile = os.path.join(TEMPLATE_DIRS[0], 'statics', a_type.identifier + '_' + operation + '_arguments_editor_' + language.short_name + '.html')
                    with open(outfile,'w') as o:
                        o.write(rendition.encode('utf-8'))
        template = loader.get_template('container/edit/flow/modify_operations.html')
        for language in languages:
            context = Context({'operations': avail_ops, 'language_code': language.short_name})
            rendition = template.render(context)
            outfile = os.path.join(TEMPLATE_DIRS[0], 'statics', a_type.identifier + '_modify_operations_' + language.short_name + '.html')
            with open(outfile,'w') as o:
                o.write(rendition.encode('utf-8'))
            