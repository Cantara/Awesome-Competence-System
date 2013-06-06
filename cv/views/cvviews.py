from cv.models.cvmodels import Cv, Person, Technology, Experience, Workplace, Education, Other
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
import json
from django.core.mail import send_mail, EmailMessage, BadHeaderError
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils.html import escape
import localsettings

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
	sendername = request.POST.get('sendername', '')
	if receiver_id and message and sendermail and sendername:
		p = get_object_or_404(Person, pk=receiver_id)
		subject = "%s has indicated that you should update your data in ACS" % sendername
		mailtext = '''Hi %s,

A colleague of yours, %s, has indicated that you should update your CV in ACS with the message:

"%s"

Missing elements in your profile include:

- %s

Update your CV here: http://%s%s?q=name:"%s"

It is of key importance to us that we have consistent and complete information in ACS as we use it on a daily basis to find and allocate the correct people for the tasks. 
If you have problems accessing or updating ACS, please check https://wiki.cantara.no/display/ACS/User+Manual for FAQ, User Manual and contact information.

Best regards,

The Awesome Competence System''' % ( p.name, sendername, message, '\n- '.join(p.completeness()['comment']), localsettings.HTTP_AUTH, localsettings.APP_URL, p.name.replace(" ","%20") )
		try:
			mail = EmailMessage(subject, mailtext, 'noreply@altran.no', [p.mail], headers = {'Reply-To': sendermail})
			mail.send()
		except BadHeaderError:
			return HttpResponseBadRequest('Invalid header found.')
		testmail = "Nag mail sent!<br/><br/>To: %s <br/><br/>Subject: %s <br/><br/>%s" % ( p.mail, subject, escape(mailtext).replace("\n","<br/>") ) 
		return HttpResponse(testmail)
	else:
		# In reality we'd use a form class
		# to get proper validation errors.
		return HttpResponseBadRequest('Make sure all fields are entered and valid.')

from django.contrib.admin.models import LogEntry

def changelog(request):
	# log = LogEntry.objects.filter(user__person__location='Oslo').select_related('content_type', 'user', 'person')[:20]
	log = LogEntry.objects.all().select_related('content_type', 'user', 'person')[:100]
	return render_to_response('cv/changelog.html', {'log':log}, context_instance=RequestContext(request))