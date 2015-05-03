from django.db import models
import os
from django.template.context import Context
from django.template import loader
import logging
from seq_common.utils import classes
from openpyxl.reader.excel import load_workbook
import datetime
from django.db.models.fields import FieldDoesNotExist
from django.db.models import Q
import traceback
from django.contrib.auth.models import User
import container
from container.settings import RESOURCES_MAIN_PATH, STATICS_PATH,\
    TEMPLATES_STATICS_PATH
from gso_mycustomers.settings import TEMPLATE_DIRS

LOGGER = logging.getLogger(__name__)

def setup():
    setup_attributes()
    setup_labels()
    populate_model_from_xlsx('container.models.MenuEntries', os.path.join(RESOURCES_MAIN_PATH,'Repository Setup.xlsx'))
    generate_attributes()
    setup_menus()
    setup_global_menus()

def setup_menus():
    MenuEntries.objects.all().delete()
    populate_model_from_xlsx('container.models.MenuEntries', os.path.join(RESOURCES_MAIN_PATH,'Repository Setup.xlsx'))
    GlobalMenuEntries.objects.all().delete()
    populate_model_from_xlsx('container.models.GlobalMenuEntries', os.path.join(RESOURCES_MAIN_PATH,'Repository Setup.xlsx'))
    generate_global_templates()
    
def setup_global_menus():
    GlobalMenuEntries.objects.all().delete()
    populate_model_from_xlsx('container.models.GlobalMenuEntries', os.path.join(RESOURCES_MAIN_PATH,'Repository Setup.xlsx'))
    generate_global_templates()

def setup_labels():
    FieldLabel.objects.all().delete()
    populate_labels_from_xlsx('container.models.FieldLabel', os.path.join(RESOURCES_MAIN_PATH,'Repository Setup.xlsx'))

def setup_attributes():
    populate_attributes_from_xlsx('container.models.Attributes', os.path.join(RESOURCES_MAIN_PATH,'Repository Setup.xlsx'))
    populate_attributes_from_xlsx('container.models.Dictionary', os.path.join(RESOURCES_MAIN_PATH,'Repository Setup.xlsx'))
    generate_attributes()

def generate_global_templates():
    languages = Attributes.objects.filter(active=True, type='available_language')
    template = loader.get_template('rendition/gso.html')
    for language in languages:
        entries = GlobalMenuEntries.objects.all().order_by('id')
        context = Context({'entries': entries, 'language_code': language.short_name})
        rendition = template.render(context)
        outfile = os.path.join(TEMPLATE_DIRS[0], 'gso_' + language.short_name + '.html')
        with open(outfile,'w') as o:
            o.write(rendition.encode('utf-8'))

def generate_attributes():
    all_types = Attributes.objects.all().order_by('type').distinct('type')
    languages = Attributes.objects.filter(active=True, type='available_language')
    for language in languages:
        context = Context({'selection': all_types, 'language_code': language.short_name})
        template = loader.get_template('rendition/attributes_list_option_renderer.html')
        rendition = template.render(context)
        outfile = os.path.join(TEMPLATES_STATICS_PATH, 'all_types_option_' + language.short_name + '.html')
        with open(outfile,'w') as o:
            o.write(rendition.encode('utf-8'))
        template = loader.get_template('rendition/attributes_list_select_renderer.html')
        rendition = template.render(context)
        outfile = os.path.join(TEMPLATES_STATICS_PATH, 'all_types_select_' + language.short_name + '.html')
        with open(outfile,'w') as o:
            o.write(rendition.encode('utf-8'))
        for a_type in all_types:
            all_elements = Attributes.objects.filter(type=a_type.type, active=True)
            context = Context({"selection": all_elements, 'language_code': language.short_name})
            template = loader.get_template('rendition/attributes_option_renderer.html')
            rendition = template.render(context)
            outfile = os.path.join(TEMPLATES_STATICS_PATH, a_type.type + '_' + language.short_name + '.html')
            with open(outfile,'w') as o:
                o.write(rendition.encode('utf-8'))
            template = loader.get_template('rendition/attributes_select_renderer.html')
            rendition = template.render(context)
            outfile = os.path.join(TEMPLATES_STATICS_PATH, a_type.type + '_select_' + language.short_name + '.html')
            with open(outfile,'w') as o:
                o.write(rendition.encode('utf-8'))
            template = loader.get_template('rendition/attributes_list_elements_renderer.html')
            rendition = template.render(context)
            outfile = os.path.join(TEMPLATES_STATICS_PATH, a_type.type + '_list_elements_' + language.short_name + '.html')
            with open(outfile,'w') as o:
                o.write(rendition.encode('utf-8'))

def populate_attributes_from_xlsx(model_name, xlsx_file):
    model = classes.my_class_import(model_name)
    workbook = load_workbook(xlsx_file)
    sheet = workbook.get_sheet_by_name(name=model.__name__)
    row_index = 1
    # Reading header
    header = []
    for column_index in range(1, sheet.get_highest_column() + 1):
        value = sheet.cell(row = row_index, column=column_index).value
        if value!=None:
            header.append(value if value!='' else header[-1])
        else:
            break
    LOGGER.info('Using header:' + str(header))
    row_index += 1
    while row_index<=sheet.get_highest_row():
        if model.objects.filter(identifier=sheet.cell(row = row_index, column=1).value).exists():
            instance = model.objects.get(identifier=sheet.cell(row = row_index, column=1).value)
        else:
            instance = model()
        for i in range(0,len(header)):
            value = sheet.cell(row = row_index, column=i+1).value
            setattr(instance, header[i], value)
        instance.save()
        row_index += 1
        
def populate_labels_from_xlsx(model_name, xlsx_file):
    model = classes.my_class_import(model_name)
    workbook = load_workbook(xlsx_file)
    sheet = workbook.get_sheet_by_name(name=model.__name__)
    row_index = 1
    # Reading header
    header = []
    for column_index in range(1, sheet.get_highest_column() + 1):
        value = sheet.cell(row = row_index, column=column_index).value
        if value!=None:
            header.append(value if value!='' else header[-1])
        else:
            break
    LOGGER.info('Using header:' + str(header))
    row_index += 1
    while row_index<=sheet.get_highest_row():
        if model.objects.filter(identifier=sheet.cell(row = row_index, column=1).value, language=sheet.cell(row = row_index, column=2)).exists():
            instance = model.objects.get(identifier=sheet.cell(row = row_index, column=1).value, language=sheet.cell(row = row_index, column=2))
        else:
            instance = model()
        for i in range(0,len(header)):
            value = sheet.cell(row = row_index, column=i+1).value
            setattr(instance, header[i], value)
        instance.save()
        row_index += 1

def populate_model_from_xlsx(model_name, xlsx_file):
    LOGGER.info("Loading data in " + model_name)
    model = classes.my_class_import(model_name)
    workbook = load_workbook(xlsx_file)
    sheet = workbook.get_sheet_by_name(name=model.__name__)
    row_index = 1
    # Reading header
    header = []
    for column_index in range(1, sheet.get_highest_column() + 1):
        value = sheet.cell(row = row_index, column=column_index).value
        if value!=None:
            header.append(value if value!='' else header[-1])
        else:
            break
    LOGGER.info('Using header:' + str(header))
    row_index += 1
    while row_index<=sheet.get_highest_row():
        instance = model()
        for i in range(0,len(header)):
            value = sheet.cell(row = row_index, column=i+1).value
            field_info = Attributes()
            field_info.short_name = header[i]
            field_info.name = header[i]
            instance.set_attribute('excel', field_info, value)
        instance.save()
        row_index += 1
        
class CoreModel(models.Model):

    def get_editable_fields(self):
        values = []
        for field in self.get_fields():
            if self._meta.get_field(field).get_internal_type()!='ManyToManyField':
                values.append(field)
        return values
        
    def get_associable_field(self):
        values = []
        for field in self.get_fields():
            if self._meta.get_field(field).get_internal_type()=='ManyToManyField':
                values.append(field)
        return values        

    @staticmethod
    def get_fields():
        return []
    
    def get_identifier(self):
        return 'name'
    
    def list_values(self):
        values = []
        for field in self.get_fields():
            LOGGER.debug(self.__class__.__name__ + ' * ' + field)
            if field in self._meta.get_all_field_names():
                if self._meta.get_field(field).get_internal_type()=='ManyToManyField' and getattr(self,field)!=None:
                    values.append(str([e.list_values() for e in list(getattr(self,field).all())]))
                elif self._meta.get_field(field).get_internal_type()=='ForeignKey' and getattr(self,field)!=None:
                    values.append(getattr(self,field).get_value())
                else:
                    values.append(str(getattr(self,field)))
            else:
                # Generic foreign key
                values.append(getattr(self,field).get_value())
        return values
    
    def get_value(self):
        if self.get_identifier()!=None:
            return getattr(self, self.get_identifier())
        else:
            return None
        
    def __unicode__(self):
        return unicode(self.get_value())
    
    def set_attribute(self, source, field_info, string_value):
        try:
            if string_value!='' and string_value!=None:
                if self._meta.get_field(field_info.short_name).get_internal_type()=='ManyToManyField':
                    if not self.many_fields.has_key(field_info.short_name):
                        self.many_fields[field_info.short_name] = []
                    foreign = self._meta.get_field(field_info.short_name).rel.to
                    foreign_element = foreign.retrieve_or_create(self, source, field_info.name, string_value)
                    if foreign_element!=None:                
                        self.many_fields[field_info.short_name].append(foreign_element)
                elif self._meta.get_field(field_info.short_name).get_internal_type()=='DateField' or self._meta.get_field(field_info.short_name).get_internal_type()=='DateTimeField':
                    try:
                        dt = datetime.datetime.strptime(string_value,'%m/%d/%Y' if source!='web' else '%y-%m-%d')
                        if self._meta.get_field(field_info.short_name).get_internal_type()=='DateField':
                            dt = datetime.date(dt.year, dt.month, dt.day)
                    except:
                        dt = string_value # This is not a String???
                    setattr(self, field_info.short_name, dt)
                elif self._meta.get_field(field_info.short_name).get_internal_type()=='ForeignKey':
                    linked_to = self._meta.get_field(field_info.short_name).rel.limit_choices_to
                    foreign = self._meta.get_field(field_info.short_name).rel.to
                    filtering_by_name = dict(linked_to)
                    filtering_by_name['name'] = string_value
                    by_name = foreign.objects.filter(**filtering_by_name)
                    filtering_by_short = dict(linked_to)
                    filtering_by_short['short_name'] = string_value
                    by_short = foreign.objects.filter(**filtering_by_short)
                    if foreign==container.models.Attributes:
                        filtering_by_identifier = dict(linked_to)
                        filtering_by_identifier['identifier'] = string_value
                        by_identifier = foreign.objects.filter(**filtering_by_identifier)
                    else:
                        by_identifier = None
                    if by_name.exists():
                        setattr(self, field_info.short_name, by_name[0])
                    elif by_short.exists():
                        setattr(self, field_info.short_name, by_short[0])
                    elif by_identifier!=None and by_identifier.exists():
                        setattr(self, field_info.short_name, by_identifier[0])
                    else:
                        dict_entry = Dictionary.objects.filter(name=linked_to['type'], auto_create=True)
                        if dict_entry.exists():
                            LOGGER.info('Creating new attribute for ' + linked_to['type'] + ' with value ' + string_value)
                            new_attribute = Attributes()
                            new_attribute.active = True
                            new_attribute.identifier = dict_entry[0].identifier + str(string_value.upper()).replace(' ', '_')
                            new_attribute.name = string_value
                            new_attribute.short_name = string_value[0:32]
                            new_attribute.type = linked_to['type']
                            new_attribute.save()
                            setattr(self, field_info.short_name, new_attribute)
                        else:
                            LOGGER.warn('Cannot find foreign key instance on ' + str(self) + '.' + field_info.short_name + ' for value [' + string_value + '] and relation ' + str(linked_to))
                else:
                    setattr(self, field_info.short_name, string_value)
        except FieldDoesNotExist:
            traceback.print_exc()
            LOGGER.error("Wrong security type for " + self.name + ", please check your settings...")
    
    class Meta:
        ordering = ['id']

class FieldLabel(CoreModel):
    identifier = models.CharField(max_length=512)
    language = models.CharField(max_length=3)
    field_label = models.CharField(max_length=1024)
    
    @staticmethod
    def get_fields():
        return ['identifier','language','field_label']
    
    def get_identifier(self):
        return 'identifier'
    
class Attributes(CoreModel):
    identifier = models.CharField(max_length=128)
    name = models.CharField(max_length=128)
    short_name = models.CharField(max_length=32)
    type = models.CharField(max_length=64)
    active = models.BooleanField()
    
    @staticmethod
    def get_fields():
        return ['identifier','name','short_name','type','active']
    
    def get_short_json(self):
        return {'id': self.id, 'name': self.name, 'short_name': self.short_name, 'identifier': self.identifier }

    class Meta:
        ordering = ['name']
        

class MenuEntries(CoreModel):
    name = models.CharField(max_length=128)
    short_name = models.CharField(max_length=32)
    menu_target = models.ForeignKey(Attributes, limit_choices_to={'type':'container_menu_target'}, related_name='container_menu_target_rel', null=True)
    menu_type = models.CharField(max_length=128)
    container_type = models.ForeignKey(Attributes, limit_choices_to={'type':'container_type'}, related_name='container_type_menu_rel', null=True)
    language_identifier = models.CharField(max_length=64)
    data_target = models.CharField(max_length=128)
    action_type = models.CharField(max_length=128, null=True, blank=True)
    
    @staticmethod
    def get_fields():
        return ['menu_target','menu_type','container_type','language_identifier','data_target','action_type']

    class Meta:
        ordering = ['menu_target']
        
    
class GlobalMenuEntries(CoreModel):
    name = models.CharField(max_length=128)
    short_name = models.CharField(max_length=32)
    menu_target = models.CharField(max_length=128)
    menu_group_target = models.CharField(max_length=128, null=True, blank=True)
    menu_type = models.CharField(max_length=128)
    container_type = models.ForeignKey(Attributes, limit_choices_to={'type':'container_type'}, related_name='container_type_gbl_menu_rel', null=True)
    language_identifier = models.CharField(max_length=64)
    data_target = models.CharField(max_length=128)
    action_type = models.CharField(max_length=128, null=True, blank=True)
    administrator_only = models.BooleanField(default=False)

    @staticmethod
    def get_fields():
        return ['menu_target','menu_group_target','menu_type','container_type','language_identifier','data_target','action_type','administrator_only']

    class Meta:
        ordering = ['menu_target']
    
class Dictionary(CoreModel):
    identifier = models.CharField(max_length=128)
    name = models.CharField(max_length=128)
    auto_create = models.BooleanField()
    
    @staticmethod
    def get_fields():
        return ['identifier','name','auto_create']
    
    class Meta:
        ordering = ['name']
        
class Address(CoreModel):
    address_type = models.ForeignKey(Attributes, limit_choices_to={'type':'address_type'}, related_name='address_type_rel', null=True)
    line_1 = models.CharField(max_length=128, null=True)
    line_2 = models.CharField(max_length=128, null=True)
    zip_code = models.CharField(max_length=16, null=True)
    city = models.CharField(max_length=128, null=True)
    country = models.ForeignKey(Attributes, limit_choices_to={'type':'country_iso2'}, related_name='address_country_rel', null=True)

    def get_identifier(self):
        return 'id'

    @staticmethod
    def get_fields():
        return ['address_type','line_1','line_2','zip_code','city','country']
    
    @staticmethod
    def get_filtering_field():
        return "address_type"
    
    @staticmethod
    def get_displayed_fields(rendition_width):
        if rendition_width=='large':
            return ['address_type.name', 'line_1','line_2','zip_code','city', 'country.name']
        elif rendition_width=='small':
            return ['address_type.name', 'city', 'country.name']

class Email(CoreModel):
    address_type = models.ForeignKey(Attributes, limit_choices_to={'type':'email_type'}, related_name='email_type_rel', null=True)
    email_address = models.EmailField()

    def get_identifier(self):
        return 'id'

    @staticmethod
    def get_fields():
        return ['address_type','email_address']
    
    @staticmethod
    def get_filtering_field():
        return "address_type"
    
    @staticmethod
    def get_displayed_fields(rendition_width):
        if rendition_width=='large':
            return ['address_type.name', 'email_address']
        elif rendition_width=='small':
            return ['address_type.name', 'email_address']
    
class Phone(CoreModel):
    line_type = models.ForeignKey(Attributes, limit_choices_to={'type':'phone_type'}, related_name='phone_type_rel', null=True)
    phone_number = models.TextField(max_length=32)

    @staticmethod
    def get_filtering_field():
        return "line_type"

    def get_identifier(self):
        return 'id'

    @staticmethod
    def get_fields():
        return ['line_type','phone_number']
    
    @staticmethod
    def get_displayed_fields(rendition_width):
        if rendition_width=='large':
            return ['line_type.name', 'phone_number']
        elif rendition_width=='small':
            return ['line_type.name', 'phone_number']
    
class Alias(CoreModel):
    alias_type = models.ForeignKey(Attributes, limit_choices_to={'type':'alias_type'}, related_name='alias_type_rel', null=True)
    alias_value = models.CharField(max_length=512)
    alias_additional = models.CharField(max_length=512)
    
    def get_identifier(self):
        return 'id'
    
    @staticmethod
    def get_fields():
        return ['alias_type','alias_value','alias_additional']
    
    @staticmethod
    def get_querying_fields():
        return ['alias_value','alias_additional']

    @staticmethod
    def get_filtering_field():
        return "alias_type"
    
    @staticmethod
    def get_displayed_fields(rendition_width):
        if rendition_width=='large':
            return ['alias_type.name','alias_value','alias_additional']
        elif rendition_width=='small':
            return ['alias_type.name','alias_value']
        
    @staticmethod
    def retrieve_or_create(parent, source, key, value):
        if isinstance(value, basestring):
            translation = Attributes.objects.filter(active=True, name=key, type=source.lower() + '_translation')
            if translation.exists():
                translation = translation[0].short_name
            else:
                translation = key
    
            alias_type = Attributes.objects.get(Q(active=True), Q(type='alias_type'), Q(identifier=translation) | Q(name=translation) | Q(short_name=translation))
            if not parent.aliases.filter(alias_type__id=alias_type.id).exists():
                new_alias = Alias()        
                new_alias.alias_type = alias_type
                new_alias.alias_value = value
                new_alias.alias_additional = ''
                new_alias.save()
                return new_alias
            else:
                return parent.aliases.get(alias_type__id=alias_type.id)
        else:
            if value['id']!=None and value['id']!='':
                alias = Alias.objects.get(id=value['id'])
            else:
                alias = Alias()
            for field in value.keys():
                if field not in ['id', 'many-to-many']:
                    if field!='alias_type':
                        setattr(alias, field, value[field])
                    else:
                        alias.alias_type = Attributes.objects.get(active=True, type='alias_type', identifier=value[field])
            alias.save()
            return alias

    class Meta:
        ordering = ['alias_value']

class Container(CoreModel):
    name = models.CharField(max_length=1024)
    short_name = models.CharField(max_length=512)
    type = models.ForeignKey(Attributes, limit_choices_to={'type':'container_type'}, related_name='container_type_rel', null=True)
    inception_date = models.DateField(null=True)
    closed_date = models.DateField(null=True)
    short_description = models.TextField(null=True, blank=True)
    status = models.ForeignKey(Attributes,limit_choices_to = {'type':'status'}, related_name='container_status_rel', null=True)
    
    many_fields = {}
    
    @classmethod
    def create(cls):
        entity = cls()
        entity.many_fields = {}
        return entity
    
    @staticmethod
    def get_fields():
        return ['name','short_name','type','inception_date','closed_date','status']
    
    def finalize(self):
        active = Attributes.objects.get(active=True, type='status', identifier='STATUS_ACTIVE')
        self.status = active
        self.save()
        # TODO Loop on many to many only
        for field_name in self._meta.get_all_field_names():
            try:
                if self._meta.get_field(field_name).get_internal_type()=='ManyToManyField':
                    if self.many_fields.has_key(field_name):
                        values = list(self.many_fields[field_name])
                        setattr(self, field_name, values)
            except FieldDoesNotExist:
                None
        self.save()
        
    @staticmethod
    def get_querying_fields():
        return ['name', 'short_name', 'short_description']
        
    def clean(self):
        self.many_fields = {}
        for field_name in self._meta.get_all_field_names():
            try:
                if self._meta.get_field(field_name).get_internal_type()=='ForeignKey':
                    setattr(self, field_name, None)
                elif self._meta.get_field(field_name).get_internal_type()=='ManyToManyField':
                    setattr(self, field_name, [])
            except FieldDoesNotExist:
                None

    def clone(self, _class):
        _clone = _class()
        [setattr(_clone, fld.name, getattr(self, fld.name)) for fld in self._meta.fields if fld.name != self._meta.pk and fld.name.find('_ptr')==-1]
        _clone.id = None
        _clone.pk = None
        return _clone

    class Meta:
        ordering = ['name']
        
class Universe(Container):
    public = models.BooleanField()
    members = models.ManyToManyField("Container", related_name='universe_inventory_rel')
    owner = models.ForeignKey(User, related_name='universe_owner_rel')
    description = models.TextField(null=True, blank=True)