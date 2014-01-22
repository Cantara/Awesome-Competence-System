# -*- coding: utf-8 -*-
from django.db import models
import datetime
import django.contrib.auth.models
from django.contrib.auth.models import User
from django.utils import timezone
from utils import multidelim

import logging
log = logging.getLogger('cv')

YEAR_CHOICES = [(0,'Year')]
for r in reversed( range(1969, (datetime.datetime.now().year+1)) ):
	YEAR_CHOICES.append((r,r))
	
MONTH_CHOICES = (
	(0, 'Month'),
	(1, 'Jan'),
	(2, 'Feb'),
	(3, 'Mar'),
	(4, 'Apr'),
	(5, 'May'),
	(6, 'Jun'),
	(7, 'Jul'),
	(8, 'Aug'),
	(9, 'Sep'),
	(10, 'Oct'),
	(11, 'Nov'),
	(12, 'Dec'),
)

LOCATION_CHOICES = (
	(u'Borlänge',	'Borlänge'),
	('Gothenburg', 	'Gothenburg'),
	('Karlstad',	'Karlstad'),
	(u'Malmö',		'Malmö'),
	('Oslo', 		'Oslo'),
	('Stockholm',	'Stockholm'),
)

DEPARTMENT_CHOICES = (
	('Automotive', 'Automotive'),
	('Business and Quality Management', 'Business and Quality Management, BQM'),
	('Business Intelligence', 'Business Intelligence, BI'),
	('Connectivity','Connectivity'),
	('Digital Electronics','Digital Electronics'),
	('​Embedded Software','​Embedded Software'),
	# ('Enterprise Content Management', 'Enterprise Content Management, ECM'),
	('ECM SharePoint','ECM SharePoint'),
	('ECM Documentum​','ECM Documentum​'),
	('Identity Access Management', 'Identity and Access Management, IAM'),
	('Intelligent Systems', 'Intelligent Systems, ISY'),
	('Life Sciences', 'Life Sciences'),
	#('​Model Based Software Engineering','​Model Based Software Engineering'),
	('Power Electronics','Power Electronics'),
	('Project and Service Management', 'Project and Service Management, PSM'),
	('Software Engineering', 'Software Engineering, SE'),
	('Systems Engineering', 'Systems Engineering'),
	('Telecom', 'Telecom'),
	('Verification and Simulation','Verification and Simulation'),

	('Sales', 'Sales'),
	('Other', 'Other'),

)

# Custom storage to overwrite existing files
from django.core.files.storage import FileSystemStorage
class OverwriteStorage(FileSystemStorage):
	def _save(self, name, content):
		if self.exists(name):
			self.delete(name)
		return super(OverwriteStorage, self)._save(name, content)

	def get_available_name(self, name):
		return name

class Person(models.Model):

	def get_image_path(self, filename):
		ext = filename.split('.')[-1]
		return "photos/%s.%s" % ( self.name.replace(" ","_"), ext )

	user = models.OneToOneField(User, null=True, blank=True)
	name = models.CharField("Name*", max_length=50)
	title = models.CharField("Job title", max_length=60, null=True, blank=True)
	linkedin = models.URLField("Linked-in URL", null=True, blank=True)
	phone = models.CharField(max_length=20, null=True, blank=True)
	mail = models.EmailField("E-mail*")
	photo = models.URLField("Photo-URL", null=True, blank=True)
	image = models.ImageField(upload_to=get_image_path, storage=OverwriteStorage(), null=True, blank=True)
	birthdate = models.DateField("Date of birth (yyyy-mm-dd)", null=True, blank=True)
	last_edited = models.DateTimeField(auto_now=True)
	location = models.CharField("Location", max_length=50, choices=LOCATION_CHOICES, null=True, blank=True)
	department = models.CharField("Practice", max_length=50, choices=DEPARTMENT_CHOICES, null=True, blank=True)
	
	def __unicode__(self):
		return self.name

	def country(self):
		if self.location in ['Oslo']:
			return 'no'
		elif self.location in ['Stockholm', 'Gothenburg', 'Borlänge', u'Borlänge', 'Karlstad', 'Malmö', u'Malmö' ]:
			return 'se'
		else:
			return False
	
	def age(self):
		if self.birthdate:
			born = self.birthdate
			today = datetime.date.today()
			try:
				birthday = born.replace(year=today.year)
			except ValueError:
				birthday = born.replace(year=today.year, day=born.day-1)
			if birthday > today:
				return today.year - born.year - 1
			else:
				return today.year - born.year
		else:
			return ""
	
	def completeness(self):
		maxscore = 0
		myscore = 0
		comment = []
		
		# Has a picture
		maxscore += 1
		if self.image:
			myscore += 1
		else:
			comment.append("No picture")
			
		# Minimum 1 skillset
		maxscore += 1
		if self.technology_set.count() >= 1:
			myscore += 1
		else:
			comment.append("Does not have at least one set of competences")
		
		# Minimum 4 entries in experience and workplace combined
		maxscore += 4
		workexp = self.experience_set.count() + self.workplace_set.count()
		if workexp >= 4:
			myscore +=4
		else:
			myscore += workexp
			comment.append("Does not have at least four entries in experience and workplace combined")
		
		# Minimum 1 entry in education
		maxscore += 1
		if self.education_set.count() > 0:
			myscore += 1
		else:
			comment.append("Does not have at least one entry in education")
			
		# Has a valid CV?
		maxscore += 1
		if self.has_cv():
			myscore += 1
		else:
			comment.append("Does not have at least one complete CV (100%)")
		
		# Is recent
		maxscore += 1
		if self.is_recent():
			myscore += 1
		else:
			comment.append("Has not been updated in the past two months.")

		if len(comment) < 1:
			pass
			# comment.append("")
		
		completeness = {
			'maxscore': maxscore, 
			'myscore': myscore, 
			'percent': int(100 * float(myscore) / float (maxscore)),
			'comment': comment,
			}
		
		return completeness

	def is_recent(self):
		return self.last_edited >= timezone.now() - datetime.timedelta(days=60)
		
	def has_cv(self):
		for cv in self.cv_set.all():
			if cv.status()['complete']:
				return True
		return False
		
	def save(self, *args, **kwargs):
		super(Person, self).save(*args, **kwargs)
		if self.image:
			from cv.templatetags.image_tags import scale
			try:
				scale(self.image, '110x110')
			except:
				pass

	def natural_key(self):
		return (self.name, self.mail)

	class Meta:
		app_label = 'cv'
		db_table = 'cv_person'
		unique_together = (('name', 'mail'),)
				
class Technology(models.Model):
	person = models.ForeignKey(Person)
	title = models.CharField("Competence category", max_length=140, null=True, blank=True)
	title_en = models.CharField("Competence category (En)", max_length=140, null=True, blank=True)
	data = models.TextField("List your competences in this category (separate with comma)", null=True, blank=True)
	data_en = models.TextField(null=True, blank=True)
	
	def data_as_list(self):
		splitted_list = []
		splitted_list = self.data.split(',')
		splitted_list = multidelim.splitlist(splitted_list, ';')
		splitted_list = multidelim.splitlist(splitted_list, '.')
		striped_list = multidelim.striplist(splitted_list)
		return striped_list
		
	def __unicode__(self):
		if self.title != "":
			return self.title
		else:
			return self.title_en

	class Meta:
		app_label = 'cv'
		db_table = 'cv_technology'

class TimedSkill(models.Model):
	
	title = models.CharField("Title", max_length=50, null=True, blank=True)
	title_en = models.CharField("Title (En)", max_length=50, null=True, blank=True)
	
	from_year = models.IntegerField('From year*', max_length=4, choices=YEAR_CHOICES, default=0)
	from_month = models.IntegerField('From month', max_length=2, choices=MONTH_CHOICES, default=0, null=True, blank=True)
	to_year = models.IntegerField('To year', max_length=4, choices=YEAR_CHOICES, default=0, null=True, blank=True)
	to_month = models.IntegerField('To month', max_length=2, choices=MONTH_CHOICES, default=0, null=True, blank=True)
	
	description = models.TextField("Description", null=True, blank=True)
	description_en = models.TextField("Description (En)", null=True, blank=True)
	
	def period(self):
		period = ""
		if(self.from_year>0):
			period = "%d " % self.from_year
			if(self.from_month>0):
				period = period + MONTH_CHOICES[self.from_month][1]
		if(self.to_year>0):
			period = "%s - %d " % (period, self.to_year)
			if(self.to_month>0):
				period = period + MONTH_CHOICES[self.to_month][1]
		return period

	def from_ym(self):
		if self.to_year:
			ym = self.to_year*100
			if self.to_month:
				ym += self.to_month
		else:
			today = datetime.date.today()
			ym = today.year * 100 + 13
		return  ym
	
	def from_monthname(self):
		return MONTH_CHOICES[self.from_month][1] # Problem with languages :( Sigh, I guess we'll use Norwegian first?
	def to_monthname(self):
		return MONTH_CHOICES[self.to_month][1]

	def title_en_no(self):
		if self.title_en:
			return self.title_en
		elif self.title:
			return self.title
		else: 
			return 'No title. '

	def description_en_no(self):
		if self.description_en:
			return
		elif self.description:
			return self.description
		else:
			return 'No description available. '
	
	def save(self, *args, **kwargs):
		s = self.title + self.title_en + self.description + self.description_en
		if len(s) > 0 or self.from_year != 0:
			super(TimedSkill, self).save(*args, **kwargs)
		else:
			pass
	
	class Meta:
		ordering = ['-to_year','-from_year']
		abstract = True
			
class Experience(TimedSkill):

	person = models.ForeignKey(Person)
	
	company = models.CharField("Client company, Project title", max_length=140, null=True, blank=True)
	company_en = models.CharField("Client company, Project title (En)", max_length=140, null=True, blank=True)
	
	techs = models.CharField("Technologies / Methods", max_length=180, null=True, blank=True)
	techs_en = models.CharField("Technologies / Methods (En)", max_length=180, null=True, blank=True)
	
	def __unicode__(self):
		if self.title is not None:
			t = self.title
		elif self.title_en is not None:
			t = self.title_en
		else:
			t = "No title"
		return "%s, %s, %s - %s" % (t, self.company, self.from_year, self.to_year)

	class Meta:
		app_label = 'cv'
		db_table = 'cv_experience'

class Workplace(TimedSkill):

	person = models.ForeignKey(Person)
	
	company = models.CharField("Company", max_length=140, null=True, blank=True)
	company_en = models.CharField("Company (En)", max_length=140, null=True, blank=True)
	
	def __unicode__(self):
		return "%s, %s, %s - %s" % (self.title, self.company, self.from_year, self.to_year)

	class Meta:
		app_label = 'cv'
		db_table = 'cv_workplace'
	
class Education(TimedSkill):

	person = models.ForeignKey(Person)
	
	school = models.CharField("School", max_length=140, null=True, blank=True)
	school_en = models.CharField("School (En)", max_length=140, null=True, blank=True)
	
	def __unicode__(self):
		return "%s, %s, %s - %s" % (self.title, self.school, self.from_year, self.to_year)
	
	class Meta:
		app_label = 'cv'
		db_table = 'cv_education'
	
class Other(models.Model):

	person = models.ForeignKey(Person)
	
	title = models.CharField("Other information (e.g. languages, publications, hobbies)", max_length=50, null=True, blank=True)
	title_en = models.CharField("Other (En)", max_length=50, null=True, blank=True)
	
	data = models.TextField("List your information", null=True, blank=True)
	data_en = models.TextField("List your inforamtion (En)", null=True, blank=True)
	
	def data_as_list(self):
		return self.data.split('\n')
		
	def __unicode__(self):
		return self.title

	class Meta:
		app_label = 'cv'
		db_table = 'cv_other'

class Cv(models.Model):

	person = models.ForeignKey(Person)
	
	last_edited = models.DateTimeField(auto_now=True)
	created = models.DateTimeField(auto_now_add=True)
	
	tags = models.CharField(verbose_name='CV description', max_length=50)
	
	title = models.CharField(max_length=50, null=True, blank=True)
	title_en = models.CharField(max_length=50, null=True, blank=True)
	
	profile = models.TextField(verbose_name='Profile description', null=True, blank=True)
	profile_en = models.TextField(verbose_name='Profile description (English)', null=True, blank=True)
	
	technology = models.ManyToManyField(Technology, verbose_name='Competence', null=True, blank=True)
	experience = models.ManyToManyField(Experience, null=True, blank=True)
	workplace = models.ManyToManyField(Workplace, null=True, blank=True)
	education = models.ManyToManyField(Education, null=True, blank=True)
	other = models.ManyToManyField(Other, null=True, blank=True)
	
	def is_recent(self):
		return self.last_edited >= timezone.now() - datetime.timedelta(days=60)
		
	is_recent.admin_order_field = 'last_edited'
	is_recent.boolean = True
	is_recent.short_description = 'Less than two months old'
	
	# Returns a dictionary of status-related stuff, e.g. is this CV done? If not, what's wrong.
	def status(self):
		complete = False
		maxscore = 0
		myscore = 0
		comment = []
		
		# Has title and profile?
		maxscore += 2

		if self.title or self.title_en:
			myscore += 1
		else:
			comment.append("Lacks title")

		if self.profile:
			if len( self.profile ) > 100:
				myscore += 1
			else: 
				comment.append('Profile text too short')
		elif self.profile_en:
			if len( self.profile_en ) > 100:
				myscore += 1
			else: 
				comment.append('Profile text too short')
		else:
			comment.append("Lacks profile")
		
		# Minimum 1 skillset
		maxscore += 1
		if self.technology.count() >= 1:
			myscore += 1
		else:
			comment.append("Does not have at least one set of competences")
		
		# Minimum 4 entries in experience and workplace combined
		maxscore += 4
		if self.experience.count() + self.workplace.count() >= 4:
			myscore +=4
		else:
			myscore += self.experience.count() + self.workplace.count()
			comment.append("Does not have at least four entries in experience and workplace combined")
		
		# Minimum 1 entry in education
		maxscore += 1
		if self.education.count() > 0:
			myscore += 1
		else:
			comment.append("Does not have at least one entry in education")
		
		if len(comment) < 1:
			comment.append("Your CV is complete! Give yourself a pat on the back!")
			complete = True
		
		completeness = {
			'maxscore': maxscore, 
			'myscore': myscore, 
			'complete': complete,
			'percent': int(100 * float(myscore) / float (maxscore)),
			'comment': ", ".join(comment),
			}
		
		return completeness
	
	def completenesspercent(self):
		return str( self.status()['percent'] )

	# Custom sorting, returns an older date for all Empty CVs, so they don't get listed first. 
	def cvsort(self):
		if self.tags == "Empty CV":
			return self.last_edited - datetime.timedelta(days=60)
		return self.last_edited
		
	def __unicode__(self):
		return self.person.name + ", " + self.tags
	
	class Meta:
		app_label = 'cv'
		db_table = 'cv_cv'

from cv.search_indexes import PersonIndex

# Triggers reindex of Solr on save.
def cv_reindex_person(sender, **kwargs):
	log.debug('CV Reindex Fired')
	try:
		PersonIndex().update_object(kwargs['instance'].person)
	except:
		pass

def person_reindex_person(sender, **kwargs):
	PersonIndex().update_object(kwargs['instance'])


def person_remove_person(sender, **kwargs):
	try:
		PersonIndex().remove_object(kwargs['instance'])
	except:
		pass
		
models.signals.post_save.connect(person_reindex_person, sender=Person)
models.signals.post_delete.connect(person_remove_person, sender=Person)

'''
models.signals.post_save.connect(cv_reindex_person, sender=Cv)
models.signals.m2m_changed.connect(cv_reindex_person, sender=Cv.technology.through)
models.signals.m2m_changed.connect(cv_reindex_person, sender=Cv.experience.through)
models.signals.m2m_changed.connect(cv_reindex_person, sender=Cv.workplace.through)
models.signals.m2m_changed.connect(cv_reindex_person, sender=Cv.education.through)
models.signals.m2m_changed.connect(cv_reindex_person, sender=Cv.other.through)
models.signals.post_save.connect(cv_reindex_person, sender=Technology)
models.signals.post_save.connect(cv_reindex_person, sender=Experience)
models.signals.post_save.connect(cv_reindex_person, sender=Workplace)
models.signals.post_save.connect(cv_reindex_person, sender=Education)
models.signals.post_save.connect(cv_reindex_person, sender=Other)

models.signals.post_delete.connect(cv_reindex_person, sender=Cv)
models.signals.post_delete.connect(cv_reindex_person, sender=Technology)
models.signals.post_delete.connect(cv_reindex_person, sender=Experience)
models.signals.post_delete.connect(cv_reindex_person, sender=Workplace)
models.signals.post_delete.connect(cv_reindex_person, sender=Education)
models.signals.post_delete.connect(cv_reindex_person, sender=Other)
'''

		

STYLE_CHOICES = (
	('sky', 'Sky'),
	('flat', 'Flat'),
	('sharp', 'Sharp'),
	('win8', 'Windows 8'),
)		
		
class Style(models.Model):
	logo = models.ImageField(upload_to="photos", null=True, blank=True)
	stylesheet = models.CharField(max_length=10, choices=STYLE_CHOICES, default='sky')
