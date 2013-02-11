from django.db import models
from cv.models.cvmodels import Person, Experience
import datetime

class Matrix(models.Model):
	title = models.CharField("Title", max_length=128)
	description = models.TextField(null=True, blank=True)
	legend = models.TextField(null=True, blank=True)
	last_edited = models.DateTimeField(auto_now=True)
	created = models.DateTimeField(auto_now_add=True)
	def __unicode__(self):
		return self.title
	def competence_count(self):
		count = 0
		for g in self.skillgroup_set.all():
			count += g.competence_set.count()
		return count
	def rating(self):
		return self.matrixentry_set.all().aggregate(Avg('rating')).values()[0]
		# Get all entries, get average (returns a dict), get first value of dict containing avg rating
	class Meta:
		app_label = 'cv'
		db_table = 'cv_matrix'

class Skillgroup(models.Model):
	matrix = models.ForeignKey(Matrix)
	title = models.CharField("Title", max_length=128)
	description = models.TextField(null=True, blank=True)
	last_edited = models.DateTimeField(auto_now=True)
	def __unicode__(self):
		return self.title
	class Meta:
		app_label = 'cv'
		db_table = 'cv_skillgroup'

class Competence(models.Model):
	skillgroup = models.ManyToManyField(Skillgroup)
	title = models.CharField("Title", max_length=128)
	description = models.TextField(null=True, blank=True)
	last_edited = models.DateTimeField(auto_now=True)
	def __unicode__(self):
		return self.title
	class Meta:
		app_label = 'cv'
		db_table = 'cv_competence'

class MatrixEntry(models.Model):
	person = models.ForeignKey(Person)
	matrix = models.ForeignKey(Matrix)
	last_edited = models.DateTimeField(auto_now=True)
	rating = models.IntegerField(null=True, blank=True)
	comment = models.TextField(null=True, blank=True)
	class Meta:
		app_label = 'cv'
		db_table = 'cv_matrixentry'

class CompetenceEntry(models.Model):
	person = models.ForeignKey(Person)
	competence = models.ForeignKey(Competence)
	rating = models.IntegerField()
	relevant_experience = models.ManyToManyField(Experience)
	last_edited = models.DateTimeField(auto_now=True)
	class Meta:
		app_label = 'cv'
		db_table = 'cv_competenceentry'