from cv.models import Person, Technology, Experience, Workplace, Education, Other, Cv, Matrix, Competence, MatrixEntry, CompetenceEntry, Skillgroup, Template
from django.contrib import admin
from django.forms import TextInput, Textarea, ModelForm, DateField, DateTimeInput, URLField
from django.db import models
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django import forms
import logging
log = logging.getLogger('admin.py')

small = {
        models.TextField: { 'widget': Textarea( attrs = {'rows':2, 'cols':30 } ) },
    }
large = {
        models.TextField: { 'widget': Textarea( attrs = {'rows':9, 'cols':47 } ) },
        models.CharField: { 'widget': TextInput( attrs = {'size':45} ) },
        models.URLField: { 'widget': TextInput( attrs = {'size':45} ) },
        models.ManyToManyField: { 'widget': forms.SelectMultiple( attrs = {'size':16, 'style':'min-width: 200px;'} ) }
    }
xlarge = {
        models.TextField: { 'widget': Textarea( attrs = {'rows':22, 'cols':120 } ) },
        models.CharField: { 'widget': TextInput( attrs = {'size':45} ) },
        models.URLField: { 'widget': TextInput( attrs = {'size':45} ) },
        models.ManyToManyField: { 'widget': forms.SelectMultiple( attrs = {'size':16, 'style':'min-width: 200px;'} ) }
    }
wide = {
        models.TextField: { 'widget': Textarea( attrs = {'rows':5, 'cols':80 } ) },
        models.CharField: { 'widget': TextInput( attrs = {'size':51} ) }
    }
    
# Originally I wanted to sort first on to_year and to_month, but if I add those, then it would place first all entries without those fields. I wanted to use my custom "from_ym", but it's not possible.
order = ('-from_year','-from_month',)

class TechnologyInline(admin.StackedInline):
    model = Technology
    verbose_name = "Competence category"
    verbose_name_plural = "Competences"
    extra = 0
    formfield_overrides = large
    fields = (('title', 'title_en'), ('data', 'data_en'))

    def has_change_permission(self, request, obj=None):
        return True #has_permission_for_person(request, obj)
    def has_delete_permission(self, request, obj=None):
        return True #has_permission_for_person(request, obj)
    def has_add_permission(self, request):
        return True

class WorkplaceInline(admin.StackedInline):
    model = Workplace
    extra = 0
    ordering = order
    formfield_overrides = large
    fields = (('from_year', 'from_month', 'to_year', 'to_month'), ('title', 'title_en'), ('company', 'company_en'), ('description', 'description_en'))

    def has_change_permission(self, request, obj=None):
        return True #has_permission_for_person(request, obj)
    def has_delete_permission(self, request, obj=None):
        return True #has_permission_for_person(request, obj)
    def has_add_permission(self, request):
        return True

class ExperienceInline(admin.StackedInline):
    model = Experience
    verbose_name_plural = "Assignments/Experiences"
    extra = 0
    ordering = order
    formfield_overrides = large
    fields = (('from_year', 'from_month', 'to_year', 'to_month'), ('title', 'title_en'), ('company', 'company_en'), ('description', 'description_en'), ('techs','techs_en'))

    def has_change_permission(self, request, obj=None):
        return True #has_permission_for_person(request, obj)
    def has_delete_permission(self, request, obj=None):
        return True #has_permission_for_person(request, obj)
    def has_add_permission(self, request):
        return True

class EducationInline(admin.StackedInline):
    model = Education
    verbose_name_plural = "Education"
    extra = 0
    ordering = order
    formfield_overrides = large
    fields = (('from_year', 'from_month', 'to_year', 'to_month'), ('title', 'title_en'), ('school', 'school_en'), ('description', 'description_en'))

    def has_change_permission(self, request, obj=None):
        return True #has_permission_for_person(request, obj)
    def has_delete_permission(self, request, obj=None):
        return True #has_permission_for_person(request, obj)
    def has_add_permission(self, request):
        return True

    class Media:
        css = {
            'all': ('/static/css/hotfix.css',)
        }

class OtherInline(admin.StackedInline):
    model = Other
    extra = 0
    formfield_overrides = large
    fields = (('title', 'title_en'), ('data','data_en'))

    def has_change_permission(self, request, obj=None):
        return True #has_permission_for_person(request, obj)
    def has_delete_permission(self, request, obj=None):
        return True #has_permission_for_person(request, obj)
    def has_add_permission(self, request):
        return True

def has_permission_for_person(request, obj):
    user_is_person = False
    try: 
        user_is_person = request.user.person == obj
    except:
        pass
    if request.user.is_superuser or user_is_person:
        return True
    return False

class PersonAdmin(admin.ModelAdmin):

    formfield_overrides = large
    fields = ('user', 'status', 'name', 'title', 'location', 'department', 'phone', 'mail', 'image', 'birthdate', 'linkedin')
    list_display = ('name', 'user', 'status', 'last_edited')
    search_fields = ['name']

    inlines = [TechnologyInline, WorkplaceInline, ExperienceInline, EducationInline, OtherInline]

    actions = ['deactivate_person', 'activate_person']

    def deactivate_person(self, request, queryset):
        queryset.update(status='inactive')
        for item in queryset:
            item.save()
    deactivate_person.short_description = "Deactivate selected persons"

    def activate_person(self, request, queryset):
        queryset.update(status='active')
        for item in queryset:
            item.save()
    activate_person.short_description = "Activate selected persons"
    
    def has_change_permission(self, request, obj=None):
        return has_permission_for_person(request, obj)

    def has_delete_permission(self, request, obj=None):
        # Only allows deletes from the admin-page for persons, not from the change_form
        if request.path[-7:] == 'person/' and request.user.is_superuser:
            return True
        return False
    
    def response_change(self, request, obj, post_url_continue=None):
        solr_update(obj)
        response = super(PersonAdmin, self).response_change(request, obj)
        if request.POST.has_key("_continue"):
            return response
        else:
            return redirect("cv_list")
    
    def response_add(self, request, obj, post_url_continue=None):
        solr_update(obj)
        response = super(PersonAdmin, self).response_change(request, obj)
        if request.POST.has_key("_createcv"):
            return redirect('cv_add_cv_for_person', obj.pk)
        else:
            return redirect("cv_list")

    def response_delete(self, request, obj, post_url_continue=None):
        solr_remove(obj)
        return redirect("cv_list")

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []
        else:
            return ['user', 'status']

    # Adding the list of popular techs
    def render_change_form(self, request, context, *args, **kwargs):
        
        extra = {
            'has_file_field': True, # Make your form render as multi-part.
            'is_add_person_form': False,
        }

        try:
            extra['cvs'] = kwargs['obj'].cv_set.all()
        except:
            pass

        if context['title'] == 'Add person':
            extra['is_add_person_form'] = True

        context.update(extra)
        
        return super(PersonAdmin, self).render_change_form(request, context, *args, **kwargs)




admin.site.register(Person, PersonAdmin)

class CvForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(CvForm, self).__init__(*args, **kwargs)
        # Filter all the select-fields to only those values that are related
        self.fields['technology'].queryset = Technology.objects.filter(person__exact = self.instance.person)
        self.fields['experience'].queryset = Experience.objects.filter(person__exact = self.instance.person)
        self.fields['workplace'].queryset = Workplace.objects.filter(person__exact = self.instance.person)
        self.fields['education'].queryset = Education.objects.filter(person__exact = self.instance.person)
        self.fields['other'].queryset = Other.objects.filter(person__exact = self.instance.person)

class CvAdmin(admin.ModelAdmin):
    form = CvForm
    readonly_fields = ['person']
    fields = ('person','tags', ('title', 'title_en'), 'profile', 'profile_en', 'technology', 'experience', 'workplace', 'education', 'other')
    formfield_overrides = xlarge
    list_display = ( 'person', 'completenesspercent', 'tags', 'title', 'last_edited', 'is_recent', )
    #filter_horizontal = ['experience']

    def response_change(self, request, obj, post_url_continue=None):
        solr_update(obj.person)
        response = super(CvAdmin, self).response_change(request, obj)
        if request.POST.has_key("_continue"):
            return response
        else:
            return redirect("cv_list")

    '''def response_delete(self, request, obj, post_url_continue=None):
        solr_update(obj.person)
        return super(CvAdmin, self).response_delete(request, obj)'''

    def render_change_form(self, request, context, *args, **kwargs):
        try:
            person_id = kwargs['obj'].person.pk
        except:
            pass
        extra = {
            'has_file_field': True, # Make your form render as multi-part.
            'is_cv_form': True,
            'person_id': person_id,
        }
        context.update(extra)
        superclass = super(CvAdmin, self)
        return superclass.render_change_form(request, context, *args, **kwargs)

    def has_change_permission(self, request, obj=None):
        try:
            return has_permission_for_person(request, obj.person)
        except:
            return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        '''try:
            return has_permission_for_person(request, obj.person)
        except:'''
        return request.user.is_superuser

admin.site.register(Cv, CvAdmin)

class CompetenceInline(admin.TabularInline):
    model = Competence
    formfield_overrides = small
    extra = 1

class MatrixAdmin(admin.ModelAdmin):
    model = Matrix
    verbose_name_plural = "Competencematrices"
    #inlines = [CompetenceFieldInline]

admin.site.register(Matrix, MatrixAdmin)

admin.site.register(MatrixEntry)
admin.site.register(Competence)
admin.site.register(CompetenceEntry)
admin.site.register(Skillgroup)


# Solr Indexing functions

from cv.search_indexes import PersonIndex

def solr_update(person):
    log.debug('CV Reindex Fired')
    try:
        PersonIndex().update_object(person)
    except:
        log.debug('Unable to update index')
        pass

def solr_remove(person):
    try:
        PersonIndex().remove_object(person)
    except:
        log.debug('Unable to remove index')
        pass



class TemplateAdmin(admin.ModelAdmin):
    model = Template

admin.site.register(Template, TemplateAdmin)

'''
class StyleAdmin(admin.ModelAdmin):
    
    def render_change_form(self, request, context, *args, **kwargs):
        style = Style.objects.get(id=1)
        extra = {
            'has_file_field': True, # Make your form render as multi-part.
            'style': style,
        }
        context.update(extra)
        superclass = super(StyleAdmin, self)
        return superclass.render_change_form(request, context, *args, **kwargs)
        
    def response_change(self, request, obj, post_url_continue=None):
        if request.POST.has_key("_continue"):
            return HttpResponseRedirect("/admin/cv/style/%s" % obj.pk)
        else:
            return HttpResponseRedirect("/cv/")

admin.site.register(Style, StyleAdmin)
'''
