from cv.models import Person, Technology, Experience, Workplace, Education, Other, Cv
from django.contrib import admin
from django.forms import TextInput, Textarea, ModelForm
from django.db import models
from django.http import HttpResponseRedirect

small = {
		models.TextField: { 'widget': Textarea( attrs = {'rows':2, 'cols':30 } ) },
	}
medium = {
		models.TextField: { 'widget': Textarea( attrs = {'rows':3, 'cols':36 } ) },
		models.CharField: { 'widget': TextInput( attrs = {'size':51} ) }
	}

class TechnologyInline(admin.StackedInline):
	model = Technology
	extra = 0
	formfield_overrides = medium
	fields = (('title', 'title_en'), ('data', 'data_en'))

class WorkplaceInline(admin.StackedInline):
	model = Workplace
	extra = 0
	formfield_overrides = medium
	fields = (('from_year', 'from_month', 'to_year', 'to_month'), ('title', 'title_en'), ('company', 'company_en'), ('description', 'description_en'))

class ExperienceInline(admin.StackedInline):
	model = Experience
	extra = 0
	formfield_overrides = medium
	fields = (('from_year', 'from_month', 'to_year', 'to_month'), ('title', 'title_en'), ('company', 'company_en'), ('description', 'description_en'), 'techs')

class EducationInline(admin.StackedInline):
	model = Education
	extra = 0
	formfield_overrides = medium
	fields = (('from_year', 'from_month', 'to_year', 'to_month'), ('title', 'title_en'), ('school', 'school_en'), ('description', 'description_en'))

class OtherInline(admin.StackedInline):
	model = Other
	extra = 0
	formfield_overrides = medium
	fields = (('title', 'title_en'), ('data', 'data_en'))

class PersonAdmin(admin.ModelAdmin):
	inlines = [TechnologyInline, WorkplaceInline, ExperienceInline, EducationInline, OtherInline]
	def response_change(self, request, obj, post_url_continue=None):
		return HttpResponseRedirect("/cv/")
	def response_add(self, request, obj, post_url_continue=None):
		return HttpResponseRedirect("/cv/")
	def response_delete(self, request, obj, post_url_continue=None):
		return HttpResponseRedirect("/cv/")
	
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
	fields = ('person','tags', ('title', 'title_en'), ('profile', 'profile_en'), 'technology', 'experience', 'workplace', 'education', 'other')
	formfield_overrides = medium
	list_display = ('person', 'tags', 'title', 'last_edited', 'is_recent')
	#filter_horizontal = ['experience']
	def response_change(self, request, obj, post_url_continue=None):
		return HttpResponseRedirect("/cv/%s" % obj.id)

admin.site.register(Cv, CvAdmin)