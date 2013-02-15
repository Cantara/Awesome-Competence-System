from cv.models import Person, Technology, Experience, Workplace, Education, Other, Cv, Matrix, Competence, MatrixEntry, CompetenceEntry, Skillgroup
from django.contrib import admin
from django.forms import TextInput, Textarea, ModelForm, DateField, DateTimeInput
from django.db import models
from django.http import HttpResponseRedirect
from django import forms

small = {
		models.TextField: { 'widget': Textarea( attrs = {'rows':2, 'cols':30 } ) },
	}
medium = {
		models.TextField: { 'widget': Textarea( attrs = {'rows':3, 'cols':36 } ) },
		models.CharField: { 'widget': TextInput( attrs = {'size':51} ) }
	}
large = {
		models.TextField: { 'widget': Textarea( attrs = {'rows':7, 'cols':36 } ) },
		models.CharField: { 'widget': TextInput( attrs = {'size':51} ) }
	}
wide = {
		models.TextField: { 'widget': Textarea( attrs = {'rows':5, 'cols':80 } ) },
		models.CharField: { 'widget': TextInput( attrs = {'size':51} ) }
	}
	
# Originally I wanted to sort first on to_year and to_month, but if I add those, then it would place first all entries without those fields. I wanted to use my custom "from_ym", but it's not possible.
order = ('-from_year','-from_month',)

class TechnologyInline(admin.StackedInline):
	model = Technology
	verbose_name_plural = "Technologies"
	extra = 0
	formfield_overrides = medium
	fields = (('title', 'title_en'), ('data', 'data_en'))

class WorkplaceInline(admin.StackedInline):
	model = Workplace
	extra = 0
	ordering = order
	formfield_overrides = medium
	fields = (('from_year', 'from_month', 'to_year', 'to_month'), ('title', 'title_en'), ('company', 'company_en'), ('description', 'description_en'))

class ExperienceInline(admin.StackedInline):
	model = Experience
	extra = 0
	ordering = order
	formfield_overrides = medium
	fields = (('from_year', 'from_month', 'to_year', 'to_month'), ('title', 'title_en'), ('company', 'company_en'), ('description', 'description_en'), ('techs',))

class EducationInline(admin.StackedInline):
	model = Education
	verbose_name_plural = "Education"
	extra = 0
	ordering = order
	formfield_overrides = medium
	fields = (('from_year', 'from_month', 'to_year', 'to_month'), ('title', 'title_en'), ('school', 'school_en'), ('description', 'description_en'))

class OtherInline(admin.StackedInline):
	model = Other
	extra = 0
	formfield_overrides = wide
	fields = ('title', 'data', 'title_en', 'data_en')

class PersonAdmin(admin.ModelAdmin):
	
	save_on_top = True
	
	fields = ('user', 'name', 'title', 'phone', 'mail', 'image', 'birthdate', 'linkedin')
	
	inlines = [TechnologyInline, WorkplaceInline, ExperienceInline, EducationInline, OtherInline]
	def response_change(self, request, obj, post_url_continue=None):
		if request.POST.has_key("_continue"):
			return HttpResponseRedirect("/admin/cv/person/%s" % obj.pk)
		else:
			return HttpResponseRedirect("/cv/")
	def response_add(self, request, obj, post_url_continue=None):
		return HttpResponseRedirect("/cv/")
	def response_delete(self, request, obj, post_url_continue=None):
		return HttpResponseRedirect("/cv/")
	
	# Adding the list of popular techs
	def render_change_form(self, request, context, *args, **kwargs):
		
		techlist = {}
		
		for p in Person.objects.all():
			for t_set in p.technology_set.all():
				for t in t_set.data_as_list():
					item = t.encode('utf-8','ignore').replace('\n','').strip()
					if len(item) < 20 and len(item) > 0:
						if item in techlist:
							techlist[item] +=1
						else:
							techlist[item] = 1
		
		sortedtechlist = [x for x in techlist.iteritems()]
		sortedtechlist.sort(key=lambda x: x[1])
		sortedtechlist.reverse()
		
		t = []
		for i in sortedtechlist:
			if i[1] > 1:
				t.append(i[0])
		
		extra = {
			'has_file_field': True, # Make your form render as multi-part.
			'techlist': t,
		}

		context.update(extra)
        
		superclass = super(PersonAdmin, self)
		return superclass.render_change_form(request, context, *args, **kwargs)
	
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
	save_on_top = True
	form = CvForm
	readonly_fields = ['person']
	fields = ('person','tags', ('title', 'title_en'), ('profile', 'profile_en'), 'technology', 'experience', 'workplace', 'education', 'other')
	formfield_overrides = large
	list_display = ('person', 'tags', 'title', 'last_edited', 'is_recent')
	#filter_horizontal = ['experience']
	def response_change(self, request, obj, post_url_continue=None):
		if request.POST.has_key("_continue"):
			return HttpResponseRedirect("/admin/cv/cv/%s" % obj.pk)
		else:
			return HttpResponseRedirect("/cv/%s" % obj.id)

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
admin.site.register(Skillgroup)


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