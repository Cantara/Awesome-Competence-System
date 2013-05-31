from cv.models.cvmodels import Cv, Person, Technology, Experience, Workplace, Education, Other
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
import json
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse

def cvlist(request):
	all_persons = Person.objects.all()
	# style = Style.objects.get(id=1)
	return render_to_response('cv/cvlist.html', {'all_persons': all_persons, 'style': ''}, context_instance=RequestContext(request))

def cv_list(request):
	all_persons = [] # Person.objects.all()
	get_params = False;
	if(request.GET):
		get_params = json.dumps(request.GET)
	# style = Style.objects.get(id=1)
	return render_to_response('cv/cv_list.html', {'all_persons': all_persons, 'g': get_params}, context_instance=RequestContext(request))
	
def detail(request, cv_id, lang = ''):
	cv = get_object_or_404(Cv, pk=cv_id)
	p = cv.person
	t = cv.technology.all()
	e = cv.experience.all()
	w = cv.workplace.all()
	d = cv.education.all()
	o = cv.other.all()
	
	# Returns the a if it exists and isn't empty, or else b
	def q(a, b):
		if a != "" and a != " ": return a
		if b != "" and b != " ": return b + " X-MISSING-TRANSLATION-X"
		return "X-NOT-FILLED-X"
	
	# If they want English, give them English
	if lang == 'eng':
		cv.profile			= q(cv.profile_en, cv.profile)
		cv.title			= q(cv.title_en, cv.title)
		
		for te in t:
			te.title		= q(te.title_en, te.title)
		
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
		l = {
			'profile': 'Profile',
			'experience': 'Experience',
			'workplace': 'Workplaces',
			'education': 'Education',
		}
	else:
		cv.profile			= q(cv.profile, cv.profile_en)
		cv.title			= q(cv.title, cv.title_en)
		
		for te in t:
			te.title		= q(te.title, te.title_en)
		
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
	
		# Norwegian subheaders
		l = {
			'profile': 'Profil',
			'experience': 'Erfaring',
			'workplace': 'Arbeidsgivere',
			'education': 'Utdanning',
		}
		
	# style = Style.objects.get(id=1)
	
	return render_to_response('cv/cv_detail.html', {'cv': cv, 'p': p, 't': t, 'e': e, 'w': w, 'd': d, 'o': o, 'l': l, 'style': '', 'lang': lang}, context_instance=RequestContext(request))

def nagmail(request):
	receiver_id = request.POST.get('receiver_id', '')
	message = request.POST.get('message', '')
	sendermail = request.POST.get('sendermail', '')
	if receiver_id and message and sendermail:
		p = get_object_or_404(Person, pk=receiver_id)
		'''try:
			send_mail("Hi, please complete your CV! -ACS", message, sendermail, [p.mail])
		except BadHeaderError:
			return HttpResponse('Invalid header found.')'''
		testmail = "Hi, please complete your CV! -ACS "+message+sendermail+p.mail
		return HttpResponse(testmail)
	else:
		# In reality we'd use a form class
		# to get proper validation errors.
		return HttpResponse('Make sure all fields are entered and valid.')