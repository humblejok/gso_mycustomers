from django.db import models
from django.db.models import Q
from container.models import Address, Email, Phone, Container, CoreModel,\
    Attributes
    
class ThirdPartyContainer(Container):
    addresses = models.ManyToManyField(Address)
    emails = models.ManyToManyField(Email)
    phones = models.ManyToManyField(Phone)

    @staticmethod
    def get_fields():
        return Container.get_fields() + ['addresses','emails','phones']

class PersonContainer(ThirdPartyContainer):
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    birth_date = models.DateField(null=True)
    
    @staticmethod
    def get_fields():
        return ThirdPartyContainer.get_fields() + ['first_name','last_name','birth_date']
    
    def get_short_json(self):
        return {'id': self.id, 'first_name': self.first_name, 'last_name': self.last_name}
    
    @staticmethod
    def get_querying_fields():
        return ['name', 'short_name', 'short_description', 'first_name', 'last_name']

class CompanyMember(CoreModel):
    person = models.ForeignKey(PersonContainer, null=True)
    role = models.ForeignKey(Attributes, limit_choices_to={'type':'company_member_role'}, related_name='company_member_role_rel', null=True)

    def get_identifier(self):
        return 'id'

    @staticmethod
    def get_fields():
        return ['person','role']
    
    @staticmethod
    def get_filtering_field():
        return "role"
    
    @staticmethod
    def get_querying_class():
        return PersonContainer
    
    @staticmethod
    def get_displayed_fields(rendition_width):
        if rendition_width=='large':
            return ['person.last_name', 'person.first_name', 'person.birth_date']
        elif rendition_width=='small':
            return ['person.last_name', 'person.first_name']

class CompanyContainer(ThirdPartyContainer):
    members = models.ManyToManyField(CompanyMember)
    subsidiary = models.ManyToManyField('CompanySubsidiary')
    
    @staticmethod
    def get_fields():
        return ThirdPartyContainer.get_fields() + ['members','subsidiary']

    def get_short_json(self):
        data_provider = Attributes.objects.get(identifier='SCR_DP', active=True)
        is_provider = RelatedCompany.objects.filter(company=self, role=data_provider).exists()

        return {'id': self.id, 'name': self.name, 'short_name': self.short_name, 'provider': is_provider}
    
    @staticmethod
    def get_querying_fields():
        return ['name', 'short_name']

class CompanySubsidiary(CoreModel):
    company = models.ForeignKey('CompanyContainer', null=True)
    role = models.ForeignKey(Attributes, limit_choices_to={'type':'company_subsidiary_role'}, related_name='company_subsidiary_role_rel', null=True)

    def get_identifier(self):
        return 'id'
    
    @staticmethod
    def get_fields():
        return ['company','role']
    
    @staticmethod
    def get_filtering_field():
        return "role"
    
    @staticmethod
    def get_querying_class():
        return CompanyContainer
    
    @staticmethod
    def get_displayed_fields(rendition_width):
        if rendition_width=='large':
            return ['company.name', 'company.inception_date', 'company.status.name']
        elif rendition_width=='small':
            return ['company.name']
    
class RelatedCompany(CoreModel):
    company = models.ForeignKey(CompanyContainer, null=True)
    role = models.ForeignKey(Attributes, limit_choices_to={'type':'security_company_role'}, related_name='security_company_role_rel', null=True)

    def get_identifier(self):
        return 'id'

    @staticmethod
    def get_fields():
        return ['company','role']

    @staticmethod
    def get_displayed_fields(rendition_width):
        if rendition_width=='large':
            return ['company.name','role.name','company.status.name']
        elif rendition_width=='small':
            return ['company.name','role.name']
    
    @staticmethod
    def get_filtering_field():
        return "role"
    
    @staticmethod
    def get_querying_class():
        return CompanyContainer
    
    @staticmethod
    def retrieve_or_create(parent, source, key, value):
        if parent!='web':
            translation = Attributes.objects.filter(active=True, name=key, type=source.lower() + '_translation')
            if translation.exists():
                translation = translation[0].short_name
            else:
                translation = key
            working_value = value
        else:
            translation = value['role']
            working_value = value['company']
            
        company = CompanyContainer.objects.filter(name=working_value)
        if company.exists():
            company = company[0]
        else:
            company = CompanyContainer()
            company.name = working_value
            company.short_name = 'Company...'
            tbv = Attributes.objects.get(active=True, type='status', identifier='STATUS_TO_BE_VALIDATED')
            company.status = tbv
            company.type = Attributes.objects.get(active=True, type='container_type', identifier='CONT_COMPANY')
            company.save()
        role = Attributes.objects.get(Q(active=True), Q(type='security_company_role'), Q(identifier=translation) | Q(name=translation) | Q(short_name=translation))
        relation = RelatedCompany.objects.filter(company__id=company.id, role__id=role.id)
        if relation.exists():
            return relation[0]
        else:
            new_relation = RelatedCompany()        
            new_relation.role = role
            new_relation.company = company
            new_relation.save()
            return new_relation


class RelatedThird(CoreModel):
    third = models.ForeignKey(PersonContainer)
    role = models.ForeignKey(Attributes, limit_choices_to={'type':'security_third_role'}, related_name='security_third_role_rel', null=True)

    def get_identifier(self):
        return 'id'

    @staticmethod
    def get_fields():
        return ['third','role']
    
    @staticmethod
    def get_filtering_field():
        return "role"
    
    @staticmethod
    def get_querying_class():
        return PersonContainer
    
    @staticmethod
    def get_displayed_fields(rendition_width):
        if rendition_width=='large':
            return ['third.name','role.name','third.status.name']
        elif rendition_width=='small':
            return ['third.name','role.name']
    
    @staticmethod
    def retrieve_or_create(parent, source, key, value):
        translation = Attributes.objects.filter(active=True, name=key, type=source.lower() + '_translation')
        if translation.exists():
            translation = translation[0].short_name
        else:
            translation = key
        third = PersonContainer.objects.filter(name=value)
        if third.exists():
            third = third[0]
        else:
            third = PersonContainer()
            third.name = value
            third.short_name = 'Company...'
            tbv = Attributes.objects.get(active=True, type='status', identifier='STATUS_TO_BE_VALIDATED')
            third.status = tbv
            third.type = Attributes.objects.get(active=True, type='container_type', identifier='CONT_PERSON')
            third.save()
            
        new_relation = RelatedThird()        
        new_relation.role = Attributes.objects.get(Q(active=True), Q(type='security_third_role'), Q(identifier=translation) | Q(name=translation) | Q(short_name=translation))
        new_relation.third = third
        new_relation.save()
        return new_relation