"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from cv.models.cvmodels import Cv, Person, Technology, Experience, Workplace, Education, Other
from cv.views.cvhelper import getTranslatedParts

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

class CvHelperTest(TestCase):

	def test_getTranslatedParts(self):
		test_person = Person.objects.create(name='Test Person',mail='test.person@email.com')
		test_cv = Cv.objects.create(person=test_person,tags='Test CV')
		test_exp = Experience.objects.create(
			person=test_person,
			from_year=2001,
			title='Native title',
			title_en='English title',
			description='Native description',
			description_en='English description')
		test_cv.experience.add(test_exp)
		# test_cv = Cv.objects.get(tags='Test CV')
		t, e, w, d, o, l = getTranslatedParts(test_cv, 'en')
		for ex in e:
			print( 'Experience description translated:', ex.description)
			print( 'Experience description (en-version):', test_exp.description_en)
			self.assertEqual(ex.description, test_exp.description_en)