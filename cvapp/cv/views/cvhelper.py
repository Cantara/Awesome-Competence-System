# coding=UTF-8

import operator
from xml.sax.saxutils import escape # escape string to valid xml

labels = {
	'en': {
		'cvheading': 'Consultant profile',
		'profile': 'Profile',
		'period': 'Period',
		'client': 'Client',
		'techs': 'Technologies/Methods',
		'workplace2': 'Workplace',
		'school': 'School',
		'experience': 'Experience',
		'workplace': 'Workplaces',
		'education': 'Education',
		'other': 'Other',
		'phone': 'Phone',
		'age': 'Age',
		'email': 'E-mail',
		'ongoing': 'ongoing',
	},
	'no': {
		'cvheading': 'Konsulentprofil',
		'profile': 'Profil',
		'period': 'Periode',
		'client': 'Klient',
		'techs': 'Teknologier/Metoder',
		'workplace2': 'Arbeidssted',
		'school': 'Skole',
		'experience': 'Erfaring',
		'workplace': 'Arbeidsgivere',
		'education': 'Utdanning',
		'other': 'Annet',
		'phone': 'Tlf',
		'age': 'Alder',
		'email': 'E-post',
		'ongoing': 'd.d.',
	},
	'se': {
		'cvheading': 'Konsultprofil',
		'profile': 'Profil',
		'period': 'Period',
		'client': 'Kund',
		'techs': 'Teknologier/Metoder',
		'workplace2': 'Arbetsplats',
		'school': 'Skola',
		'experience': 'Erfarenhet',
		'workplace': 'Arbetsgivare',
		'education': 'Utbildning',
		'other': u'Övrigt',
		'phone': 'Tfn',
		'age': u'Ålder',
		'email': 'E-post',
		'ongoing': 'pågående',
	}, 
}

def getTranslatedParts(cv, lang, alerts=False):

	t = cv.technology.all()
	e = cv.experience.all()
	w = cv.workplace.all()
	d = cv.education.all()
	o = cv.other.all()
	
	# Returns the a if it exists and isn't empty, or else b
	def getAorB(a, b):
		if a is not None:
			if a.strip(): 
				return a
		if b is not None:
			if b.strip(): 
				if alerts:
					return b + " X-MISSING-TRANSLATION-X"
				else:
					return b
		if alerts:
			return "X-NOT-FILLED-X"
		return ""

	def getBorA(a,b):
		return getAorB(b,a)
	
	# If they want English, give them English
	if lang == 'en':
		q = getBorA
		# English subheaders
		l = labels['en']
		languagecode = 'en'
	else:
		q = getAorB
		
		languagecode = cv.person.country()
		if not languagecode:
			languagecode = 'en'

		l = labels[languagecode]

	cv.profile			= q(cv.profile, cv.profile_en)
	cv.title			= q(cv.title, cv.title_en)
	
	for te in t:
		te.title		= q(te.title, te.title_en)
		te.data			= q(te.data, te.data_en)
	
	for ex in e:
		ex.title		= q(ex.title, ex.title_en)
		ex.company		= q(ex.company, ex.company_en)
		ex.techs		= q(ex.techs, ex.techs_en)
		ex.from_year 	= getPeriod(ex, languagecode)
		ex.description	= q(ex.description, ex.description_en)
		if not alerts:
			ex.description	= escape( ex.description.encode("utf-8") )
		ex.orderkey 	= ex.from_ym()
		
	for wp in w:
		wp.title		= q(wp.title, wp.title_en)
		wp.company		= q(wp.company, wp.company_en)
		wp.from_year 	= getPeriod(wp, languagecode)
		wp.description	= q(wp.description, wp.description_en)
		if not alerts:
			wp.description	= escape( wp.description.encode('utf-8') )
		wp.orderkey 	= wp.from_ym()
		
	for du in d:
		du.title		= q(du.title, du.title_en)
		du.school		= q(du.school, du.school_en)
		du.from_year 	= getPeriod(du, languagecode)
		du.description	= q(du.description, du.description_en)
		if not alerts:
			du.description	= escape( du.description.encode('utf-8') )
		du.orderkey 	= du.from_ym()
	
	for ot in o:
		ot.title		= q(ot.title, ot.title_en)
		ot.data			= q(ot.data, ot.data_en)

	e = sorted( e, key=operator.attrgetter('orderkey'), reverse=True )
	w = sorted( w, key=operator.attrgetter('orderkey'), reverse=True )
	d = sorted( d, key=operator.attrgetter('orderkey'), reverse=True )

	return t, e, w, d, o, l

from cv.models.cvmodels import MONTH_CHOICES
from cv.templatetags.month_trans import month_trans

def getPeriod(timedskill, lang):
	l = labels[lang]
	period = ''
	if(timedskill.from_year>0):
		period = "%d " % timedskill.from_year
		if(timedskill.from_month>0):
			period = period + month_trans( MONTH_CHOICES[timedskill.from_month][1], lang )
	if(timedskill.to_year>0):
		period = "%s - %d " % (period, timedskill.to_year)
		if(timedskill.to_month>0):
			period = period + month_trans( MONTH_CHOICES[timedskill.to_month][1], lang )
	else:
		period = period + " - " + l['ongoing']
	return period