'''
Created on Jul 10, 2015

@author: sdejonckheere
'''
from seq_common.utils.classes import my_class_import
from container.utilities import setup_content
from django.contrib.auth.models import User
import datetime
from container.utilities.utils import get_effective_instance,\
    get_effective_container
import logging
from container.models import Universe
from django.db.models import Q

LOGGER = logging.getLogger(__name__)

def container_visible(container_id, profile):
    if profile['is_staff'] or str(profile['current_work_as']).lower()=='administrator':
        return True
    else:
        effective_instance =  get_effective_container(container_id)
        if isinstance(effective_instance, Universe):
            return Universe.objects.filter(Q(id=container_id), Q(owner__id=profile['current_work_as']['third_id']) | Q(public=True)).exists()
        else:
            # TODO Optimize with SQL
            all_universes = get_or_create_ownership_universes(profile['current_work_as'])
            for universe in all_universes:
                if universe.members.filter(id=container_id).exists():
                    return True
    return False

def recurse_company_structure(container):
    company = get_effective_container(container.id)
    structure = [{'third_id':company.id, 'third_name': company.name, 'third_short_name': company.short_name}]
    for sub_company in company.subsidiary.all():
        structure += recurse_company_structure(sub_company.company)
    else:
        return structure
    

def get_or_create_ownership_universes(working_as):
    universe_class = my_class_import('container.models.Universe')
    attributes_class = my_class_import('container.models.Attributes')
    third_class = my_class_import('container.models.ThirdPartyContainer')
    
    third_id = working_as['third_id']
    third = third_class.objects.get(id=third_id)
    universe = universe_class.objects.filter(public=False, owner=third, short_name=third_id)
    if not universe.exists():
        universe = universe_class()
        universe.owner = third
        universe.public = False
        universe.description = 'Technical universe that allows the management of the global permissions for user:' + third.name + '.'
        universe.name = 'Ownership - ' + third.name
        universe.short_name = third_id
        universe.type = attributes_class.objects.get(active=True, type='container_type', identifier='CONT_UNIVERSE')
        universe.inception_date = datetime.date.today()
        universe.closed_date = None
        universe.status = attributes_class.objects.get(active=True, type='status', identifier='STATUS_ACTIVE')
        universe.save()
    else:
        universe = universe[0]
    effective_third = get_effective_instance(third)
    all_sub_universes = [universe]
    if effective_third.type.identifier=='CONT_COMPANY':
        # TODO Control that there are no loops
        for subsidiary in effective_third.subsidiary.all():
            sub_universe = get_or_create_ownership_universes({'third_id': subsidiary.company.id})
            all_sub_universes += sub_universe
        for member in effective_third.members.all():
            sub_universe = get_or_create_ownership_universes({'third_id': member.person.id})
            all_sub_universes += sub_universe
    return all_sub_universes

def get_or_create_user_profile(user_id):
    profile = setup_content.get_data('user_profiles', user_id)
    current_user = User.objects.get(id=user_id)
    mapping_class = my_class_import('container.models.UserMapping')
    if profile==None or not profile:
        language_attribute = my_class_import('container.models.Attributes').objects.get(active=True, identifier='AVAIL_LANGUAGE_EN')
        profile = {'_id': user_id, 'user_name': current_user.username, 'language':language_attribute.identifier, 'base_template': 'gso_' + language_attribute.short_name + '.html', 'language_code': language_attribute.short_name}
    if not profile.has_key('user_name') or profile['user_name']!=current_user.username:
        profile['user_name'] = current_user.username
    profile['is_staff'] = current_user.is_staff or current_user.is_superuser
    # TODO Cache that
    mappings = mapping_class.objects.filter(related_user__id=user_id)
    profile['available_work_places'] = []
    for mapping in mappings:
        if mapping.third_container.type.identifier=='CONT_COMPANY':
            profile['available_work_places'] += recurse_company_structure(mapping.third_container)
        else:
            profile['available_work_places'].append({'third_id':mapping.third_container.id, 'third_name': mapping.third_container.name, 'third_short_name': mapping.third_container.short_name})
    if not profile.has_key('current_work_as'):
        # TODO Reset at login and clean the mess of tests
        if profile.has_key('default_work_place') and profile['default_work_place']!='administrator':
            try:
                profile['current_work_as'] = next(data for (index, data) in enumerate(profile['available_work_places']) if data['third_name'] == profile['default_work_place']['third_name'])
            except StopIteration:
                if len(profile['available_work_places'])>0:
                    profile['current_work_as'] = profile['available_work_places'][0]
                else:
                    LOGGER.error('Invalid profile setup for user ' + current_user.username)
        elif profile.has_key('default_work_place') and profile['default_work_place']=='administrator':
            profile['current_work_as'] = profile['default_work_place']
        else:
            if len(profile['available_work_places'])>0:
                profile['current_work_as'] = profile['available_work_places'][0]
            else:
                LOGGER.error('Invalid profile setup for user ' + current_user.username)
    setup_content.set_data('user_profiles', profile, False)
    return profile