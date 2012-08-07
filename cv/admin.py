from cv.models import Person, Technologies, Experience, Workplaces, Education, Others
from django.contrib import admin

class TechnologiesInline(admin.TabularInline):
	model = Technologies
	extra = 1

class ExperienceInline(admin.StackedInline):
	model = Experience
	extra = 1

class WorkplacesInline(admin.TabularInline):
	model = Workplaces
	extra = 1

class EducationInline(admin.TabularInline):
	model = Education
	extra = 1

class OthersInline(admin.TabularInline):
	model = Others
	extra = 1

class PersonAdmin(admin.ModelAdmin):
	inlines = [TechnologiesInline, ExperienceInline, WorkplacesInline, EducationInline, OthersInline]

admin.site.register(Person, PersonAdmin)