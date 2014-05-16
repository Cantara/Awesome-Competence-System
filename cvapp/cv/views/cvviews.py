from cv.models.cvmodels import Cv, Person, Technology, Experience, Workplace, Education, Other, Template
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
import json
from django.core.mail import send_mail, EmailMessage, BadHeaderError
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.utils.html import escape
import localsettings

from cvhelper import labels, getTranslatedParts

def cv_list(request):
	templates = Template.objects.all()
	try:
		solrurl = localsettings.SOLRURL
	except:
		solrurl = "/solr/collection1/select"
	return render_to_response('cv/cv_list.html', {'solrurl': solrurl, 'templates': templates}, context_instance=RequestContext(request))
	
def detail(request, cv_id, lang = ''):
	cv = get_object_or_404(Cv, pk=cv_id)
	p = cv.person

	t, e, w, d, o, l = getTranslatedParts(cv, lang, alerts=True)
		
	# style = Style.objects.get(id=1)
	templates = Template.objects.all()
	
	if not lang:
		lang = p.country

	dictionary = {
		'cv': cv,
		'p': p, 
		't': t, 
		'e': e, 
		'w': w, 
		'd': d, 
		'o': o, 
		'l': l, 
		'style': '', 
		'lang': lang,
		'templates': templates
	}
	
	return render_to_response('cv/cv_detail.html', dictionary, context_instance=RequestContext(request))

def nagmail(request):
	receiver_id = request.POST.get('receiver_id', '')
	message = request.POST.get('message', '')
	sendermail = request.POST.get('sendermail', '')
	sendername = request.POST.get('sendername', '')
	if receiver_id and message and sendermail and sendername:
		p = get_object_or_404(Person, pk=receiver_id)

		missing = ''
		if p.completeness()['percent'] < 100:
			missing = 'Missing elements in your profile include: \n -%s' % '\n- '.join(p.completeness()['comment'])

		subject = "%s has indicated that you should update your data in ACS" % sendername
		mailtext = '''Hi %s,

A colleague of yours, %s, has indicated that you should update your CV in ACS with the message:

"%s"

%s

Update your CV here: %s?q=name:%%22%s%%22

It is of key importance to us that we have consistent and complete information in ACS as we use it on a daily basis to find and allocate the correct people for the tasks. 
If you have problems accessing or updating ACS, please check https://wiki.cantara.no/display/ACS/User+Manual for FAQ, User Manual and contact information.

Best regards,

The Awesome Competence System''' % ( p.name, sendername, message, missing, localsettings.APP_URL, p.name.replace(" ","%20") )
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
		
def multinagmail(request):
	receiver_email = request.POST.get('receiver_email', '')
	message = request.POST.get('message', '')
	sendermail = request.POST.get('multisendermail', '')
	sendername = request.POST.get('multisendername', '')
	#sendcopy = request.POST.get('checkboxcopy', '')
	no_reply = 'no-reply@altran.com'
	if receiver_email and message:
		if not sendermail:
			sendermail = no_reply
		if not sendername:
			sendername = 'Mr/Ms Not_logged_in'
		subject = "%s is nagging you through ACS" % sendername
		mailtext = '''Hi, 
The following message have been sent through ACS.
Sent by: %s
Sent by E-mail: %s

%s

ACS url: %s''' % (sendername, sendermail, message, "https://"+request.get_host())
		temp_list = receiver_email.split(';', 1)
		try:
			mail = EmailMessage(subject, mailtext, sendermail, temp_list, headers = {'Reply-To': sendermail})
			mail.send()
			#if sendcopy:
				#copy = EmailMessage(subject, mailtext, no_reply, [sendermail], headers = {'Reply-To': no_reply})
				#copy.send()
		except BadHeaderError:
			return HttpResponseBadRequest('Invalid header found.')
		testmail = "Nag mail sent!<br/><br/>To: %s <br/><br/>Subject: %s <br/><br/>%s" % ( receiver_email, subject, escape(mailtext).replace("\n","<br/>") ) 
		return HttpResponse(testmail)
	else:
		# In reality we'd use a form class
		# to get proper validation errors.
		return HttpResponseBadRequest('Make sure all fields are entered and valid.')

from django.contrib.admin.models import LogEntry

def changelog(request):
	# log = LogEntry.objects.filter(user__person__location='Oslo').select_related('content_type', 'user', 'person')[:20]
	log = LogEntry.objects.all().select_related('content_type', 'user', 'person')
	for l in log:
		try: 
			l_obj = l.get_edited_object()
			if ( hasattr(l_obj, 'location') ):
				l.location = l_obj.location
				l.department = l_obj.department
				l.personname = l_obj.name
			else: 
				l.location = l_obj.person.location
				l.department = l_obj.person.department
				l.personname = l_obj.person.name
		except: 
			pass
	return render_to_response('cv/changelog.html', {'log':log}, context_instance=RequestContext(request))

def multisearch(request):
	return render_to_response('cv/multisearch.html', context_instance=RequestContext(request) )

from django.core import serializers

def expautocomplete(request):
	if(request.GET['term']):
		term = request.GET['term']
		es = Experience.objects.filter(company__icontains=term) | Experience.objects.filter(description__icontains=term)
		jsones = serializers.serialize('json', es, indent=2, use_natural_keys=True)
	return HttpResponse(jsones)

import logging
log = logging.getLogger('cv')

def add_person_for_user(request):
	try:
		p = request.user.person
		HttpResponseForbidden()
	except:
		if request.user.first_name != '':
			name = "%s %s" % (request.user.first_name, request.user.last_name)
		else:
			name = request.user.username
		mail = request.user.email
		p = Person(
			user = request.user,
			name = name,
			mail = mail
			)
		p.save()
		return redirect('admin:cv_person_change', p.pk)

def add_cv_for_person(request, pid):
	user_is_person = False
	p = get_object_or_404(Person, pk=pid)
	if request.user.is_superuser or request.user.person == p:
		tags = 'NEW CV '
		title = ''
		try:
			tags += p.title
			title = p.title
		except:
			pass
		cv = Cv(
			tags = tags, 
			person = p, 
			profile = '', 
			profile_en = '',
			title = title,
			title_en = '',
			)
		cv.save()
		cv.technology.add( *list( p.technology_set.all() ) )
		cv.experience.add( *list( p.experience_set.all() ) )
		cv.workplace.add( *list( p.workplace_set.all() ) )
		cv.education.add( *list( p.education_set.all() ) )
		cv.other.add( *list( p.other_set.all() ) )
		cv.save()
		return redirect('admin:cv_cv_change', cv.pk)
	else:
		return HttpResponseForbidden()

import locale
import sys
 
def view_locale(request):
	loc_info = "getlocale: " + str(locale.getlocale()) + \
		"<br/>getdefaultlocale(): " + str(locale.getdefaultlocale()) + \
		"<br/>fs_encoding: " + str(sys.getfilesystemencoding()) + \
		"<br/>sys default encoding: " + str(sys.getdefaultencoding())
	return HttpResponse(loc_info)