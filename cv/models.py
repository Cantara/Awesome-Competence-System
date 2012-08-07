from django.db import models

# Create your models here.
class Person(models.Model):
	name = models.CharField(max_length=50)
	title = models.CharField(max_length=50, null=True, blank=True)
	title_en = models.CharField(max_length=50, null=True, blank=True)
	phone = models.CharField(max_length=20, null=True, blank=True)
	mail = models.EmailField()
	photo = models.URLField()
	profile = models.TextField(null=True, blank=True)
	profile_en = models.TextField(null=True, blank=True)
	
	def __unicode__(self):
		return self.name

class Technologies(models.Model):
	person = models.ForeignKey(Person)
	title = models.CharField(max_length=50, null=True, blank=True)
	title_en = models.CharField(max_length=50, null=True, blank=True)
	data = models.TextField(null=True, blank=True)
	def data_as_list(self):
		return self.data.split(',')
	
class Experience(models.Model):
	person = models.ForeignKey(Person)
	title = models.CharField(max_length=50, null=True, blank=True)
	title_en = models.CharField(max_length=50, null=True, blank=True)
	years = models.CharField(max_length=20)
	company = models.CharField(max_length=50, null=True, blank=True)
	company_en = models.CharField(max_length=50, null=True, blank=True)
	description = models.TextField(null=True, blank=True)
	description_en = models.TextField(null=True, blank=True)
	techs = models.CharField(max_length=100, null=True, blank=True)

class Workplaces(models.Model):
	person = models.ForeignKey(Person)
	title = models.CharField(max_length=50, null=True, blank=True)
	title_en = models.CharField(max_length=50, null=True, blank=True)
	years = models.CharField(max_length=20)
	company = models.CharField(max_length=50, null=True, blank=True)
	company_en = models.CharField(max_length=50, null=True, blank=True)
	description = models.TextField(null=True, blank=True)
	description_en = models.TextField(null=True, blank=True)
	
class Education(models.Model):
	person = models.ForeignKey(Person)
	title = models.CharField(max_length=50, null=True, blank=True)
	title_en = models.CharField(max_length=50, null=True, blank=True)
	years = models.CharField(max_length=20)
	school = models.CharField(max_length=50, null=True, blank=True)
	school_en = models.CharField(max_length=50, null=True, blank=True)
	description = models.TextField(null=True, blank=True)
	description_en = models.TextField(null=True, blank=True)
	
class Others(models.Model):
	person = models.ForeignKey(Person)
	title = models.CharField(max_length=50, null=True, blank=True)
	title_en = models.CharField(max_length=50, null=True, blank=True)
	data = models.TextField(null=True, blank=True)
	data_en = models.TextField(null=True, blank=True)
	def data_as_list(self):
		return self.data.split('\n')