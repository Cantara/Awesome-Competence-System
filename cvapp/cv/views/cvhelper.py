# coding=UTF-8

labels = {
	'en': {
		'cvheading': 'Consultant profile',
		'profile': 'Profile',
		'period': 'Period',
		'client': 'Client',
		'techs': 'Technologies',
		'workplace2': 'Workplace',
		'school': 'School',
		'experience': 'Experience',
		'workplace': 'Workplaces',
		'education': 'Education',
		'phone': 'Phone',
		'age': 'Age',
		'email': 'E-mail',
	},
	'no': {
		'cvheading': 'Konsulentprofil',
		'profile': 'Profil',
		'period': 'Periode',
		'client': 'Klient',
		'techs': 'Teknologier',
		'workplace2': 'Arbeidssted',
		'school': 'Skole',
		'experience': 'Erfaring',
		'workplace': 'Arbeidsgivere',
		'education': 'Utdanning',
		'phone': 'Tlf',
		'age': 'Alder',
		'email': 'E-post',
	},
	'se': {
		'cvheading': 'Konsultprofil',
		'profile': 'Profil',
		'period': 'Period',
		'client': 'Kund',
		'techs': 'Teknologier',
		'workplace2': 'Arbetsplats',
		'school': 'Skola',
		'experience': 'Erfarenhet',
		'workplace': 'Arbetsgivare',
		'education': 'Utbildning',
		'phone': 'Tfn',
		'age': u'Ålder',
		'email': 'E-post',
	}, 
}

def getTranslatedParts(cv, lang, alerts=False):

	t = cv.technology.all()
	e = cv.experience.all()
	w = cv.workplace.all()
	d = cv.education.all()
	o = cv.other.all()
	
	# Returns the a if it exists and isn't empty, or else b
	def q(a, b):
		if a.strip(): 
			return a
		if b.strip(): 
			if alerts:
				return b + " X-MISSING-TRANSLATION-X"
			else:
				return b
		if alerts:
			return "X-NOT-FILLED-X"
		return ""
	
	# If they want English, give them English
	if lang == 'en':
		cv.profile			= q(cv.profile_en, cv.profile)
		cv.title			= q(cv.title_en, cv.title)
		
		for te in t:
			te.title		= q(te.title_en, te.title)
			te.data			= q(te.data_en, te.data)
		
		for ex in e:
			ex.title		= q(ex.title_en, ex.title)
			ex.company		= q(ex.company_en, ex.company)
			ex.description	= q(ex.description_en, ex.description)
			
		for wp in w:
			wp.title		= q(wp.title_en, wp.title)
			wp.company		= q(wp.company_en, wp.title)
			wp.description	= q(wp.description_en, wp.description)
			
		for du in d:
			du.title		= q(du.title_en, du.title)
			du.school		= q(du.school_en, du.school)
			du.description	= q(du.description_en, du.description)
		
		for ot in o:
			ot.title		= q(ot.title_en, ot.title)
			ot.data			= q(ot.data_en, ot.data)
		
		# English subheaders
		l = labels['en']
	else:
		cv.profile			= q(cv.profile, cv.profile_en)
		cv.title			= q(cv.title, cv.title_en)
		
		for te in t:
			te.title		= q(te.title, te.title_en)
			te.data			= q(te.data, te.data_en)
		
		for ex in e:
			ex.title		= q(ex.title, ex.title_en)
			ex.company		= q(ex.company, ex.company_en)
			ex.description	= q(ex.description, ex.description_en)
			
		for wp in w:
			wp.title		= q(wp.title, wp.title_en)
			wp.company		= q(wp.company, wp.title_en)
			wp.description	= q(wp.description, wp.description_en)
			
		for du in d:
			du.title		= q(du.title, du.title_en)
			du.school		= q(du.school, du.school_en)
			du.description	= q(du.description, du.description_en)
		
		for ot in o:
			ot.title		= q(ot.title, ot.title_en)
			ot.data			= q(ot.data, ot.data_en)
		
		languagecode = cv.person.country()
		if not languagecode:
			languagecode = 'en'

		l = labels[languagecode]

	return t, e, w, d, o, l