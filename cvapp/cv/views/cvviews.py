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
	return render_to_response('cv/cv_list_angular.html', {'solrurl': solrurl, 'templates': templates}, context_instance=RequestContext(request))
	
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

		subject = "Message from %s in ACS" % sendername
		mailtext = '''%s

%s

Update your CV here: %s?q=name:%%22%s%%22

---

It is of key importance to us that we have consistent and complete information in ACS as we use it on a daily basis to find and allocate the correct people for the tasks. 
If you have problems accessing or updating ACS, please check https://wiki.cantara.no/display/ACS/User+Manual for FAQ, User Manual and contact information.
''' % ( message, missing, localsettings.APP_URL, p.name.replace(" ","%20") )
		try:
			mail = EmailMessage(subject, mailtext, 'noreply@altran.com', [p.mail], headers = {'Reply-To': sendermail})
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
	sendermail = request.POST.get('sendermail', '')
	sendername = request.POST.get('sendername', '')
	#sendcopy = request.POST.get('checkboxcopy', '')
	no_reply = 'no-reply@altran.com'
	if receiver_email and message:
		if not sendermail:
			sendermail = no_reply
		subject = "Message from %s in ACS" % sendername
		mailtext = '''%s
---
ACS
%s''' % (message, "https://"+request.get_host())
		temp_list = receiver_email.split(';', 1)
		try:
			mail = EmailMessage(subject, mailtext, 'noreply@altran.com', temp_list, headers = {'Reply-To': sendermail})
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

def add_experience(request):

	pid = request.POST.get('pid','')
	p = get_object_or_404(Person, pk=pid)

	if request.user.is_superuser or request.user.person == p:

		from_year = request.POST.get('from_year','')
		from_month = request.POST.get('from_month','')
		to_year = request.POST.get('to_year','')
		to_month = request.POST.get('to_month','')
		title = request.POST.get('title','')
		title_en = request.POST.get('title_en','')
		company = request.POST.get('company','')
		company_en = request.POST.get('company_en','')
		description = request.POST.get('description','')
		description_en = request.POST.get('description_en','')
		techs = request.POST.get('techs','')
		techs_en = request.POST.get('techs_en','')

		# TODO: Validity check before creating experience object
		# 

		if title != '':

			exp = Experience(
				person = p,
				from_year = int(from_year),
				title = title,
				title_en = title_en,
				company = company,
				company_en = company_en,
				description = description, 
				description_en = description_en,
				techs = techs,
				techs_en = techs_en,
				)

			if isinstance(from_month, int):
				exp.from_month = int(from_month)+1
			if isinstance(to_year, int):
				exp.to_year = int(to_year)
			if isinstance(to_month, int):
				exp.to_month = int(to_month)+1

			exp.save()

			cv_ids = request.POST.getlist('cv_ids')

			for cv_id in cv_ids:
				cv = get_object_or_404(Cv, pk=cv_id)
				cv.experience.add(exp)
				cv.save()

			return HttpResponse( "Experience added: %s %s" % ( title, company ) )
			
		else:
			return HttpResponseBadRequest( "Please fill out the required fields.")

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