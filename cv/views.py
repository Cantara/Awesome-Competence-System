# -*- coding: utf-8 -*-

# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, Context
from django.http import HttpResponse, HttpResponseRedirect
from django import http
from cv.models import Cv, Person, Technology, Experience, Workplace, Education, Other
from webodt.shortcuts import _ifile, render_to_response as rtr
from webodt.converters import converter
import webodt
from reportlab.pdfgen import canvas
import simplejson as json
import settings
import ordereddict as odict
from django.contrib.auth import authenticate, login, logout

from appy.pod.renderer import Renderer
import requests #get it http://docs.python-requests.org/en/latest/index.html

def download(request, format):
	
	if(request.POST['cvjson']):
	
		a = json.loads(request.POST['cvjson'], object_pairs_hook = odict.OrderedDict, strict=False)
			
		p = Person(
			name = a['name'],
			phone = a['phone'],
			mail = a['mail'],
		)
		
		c = Cv(
			title = a['title'],
			profile = a['profile'].encode( "utf-8" ),
		)
		
		try:
			imgUrl = settings.PROJECT_ROOT + a['photo']
			f = open(imgUrl, 'r')
			data = f.read()
			f.close()
		except:
			imgUrl = "http://www.freecode.no/wp-content/uploads/2012/03/FreeCode-black-300px.jpg"
			re = requests.get(imgUrl)
			data = re.content
		
		t_set = []
		e_set = []
		w_set = []
		d_set = []
		o_set = []
		
		if 'technology' in a:
			for x, item in a['technology'].items():
				t_set.append( 
					Technology( 
						title		= item['title'], 
						data		= item['data']
					) 
				)
		
		if 'experience' in a:
			for x in a['experience']:
				e_set.append( 
					Experience( 
						title		= x['title'], 
						from_year	= x['years'], # Must fix this later
						company		= x['company'],
						description = x['description'].encode( "utf-8" ),
						techs		= x['techs'],
					) 
				)
		
		if 'workplace' in a:
			for x in a['workplace']:
				w_set.append( 
					Workplace( 
						title		= x['title'], 
						from_year	= x['years'], # Must fix this later
						company		= x['company'],
						description = x['description'].encode( "utf-8" ),
					) 
				)
		
		if 'education' in a:
			for x in a['education']:
				d_set.append( 
					Education( 
						title		= x['title'], 
						from_year	= x['years'], # Must fix this later
						school		= x['school'],
						description = x['description'].encode( "utf-8" ),
					) 
				)
		
		if 'other' in a:
			for x, item in a['other'].items():
				datalist = "<ul><li>" + item['data'].replace('<br/>','</li><li>') + "</li></ul>"
				o_set.append( 
					Other( 
						title		= item['title'], 
						data		= datalist.encode( "utf-8", "ignore" )
					) 
				)
			
		dict = {
			'l': {
				'profile': 'Profil',
				'experience': 'Erfaring',
				'workplace': 'Arbeidsgivere',
				'education': 'Utdanning'
			}, 
			'a': a, # Contains age (as it is calculated and don't need special encoding - Also, it doesn't exist in the model :-/ )
			'p': p, # Person-related data
			'c': c, # CV-related data
			't': t_set, 
			'e': e_set,
			'w': w_set, 
			'd': d_set, 
			'o': o_set,
			'img': data,
		}
		
	#else:
		#get cvid from url and render the entire set of stuff from cv
	
	
	doc=""
	if format != "odt": doc = "doc"
	
	srcFile = settings.PROJECT_ROOT + '/cv/cvjsontest%s.odt' % doc
	
	rsltFile = '/tmp/%s.odt' % p.name.encode('ascii', 'ignore')
	r = Renderer(srcFile, dict, rsltFile, overwriteExisting=True)
	r.run()
	if format == "odt":
		response = HttpResponse(open(rsltFile, 'rb').read(), mimetype='application/vnd.oasis.opendocument.text')
		response['Content-Disposition'] = 'attachment; filename=%s %s Freecode CV.odt' % (p.name.encode('ascii', 'ignore'), c.title.encode('ascii', 'ignore').replace(" ", "_"))
		return response
	else:
		return rtr(p.name.encode('ascii', 'ignore')+'.odt', filename='%s %s Freecode CV.odt' % (p.name.encode('ascii', 'ignore'), c.title.encode('ascii', 'ignore').replace(" ", "_")), format=format) 
		# Works with GoogleDocs backend, but not pretty. Try OpenOffice backend instead.

def odt(request, person_id=1):

	p = get_object_or_404(Person, pk=person_id)
	
	try:
		imgUrl = p.image.url
	except:
		imgUrl = "http://www.freecode.no/wp-content/uploads/2012/03/FreeCode-black-300px.jpg"
	re = requests.get(imgUrl)
	data = re.content
	
	p.profile = p.profile.replace('\n','<br/>')
	pro = p.profile.encode( "utf-8" )
	p.profile = pro
	t = p.technology_set.all()
	e = p.experience_set.all()
	w = p.workplace_set.all()
	d = p.education_set.all()
	dict = {
		'l': {
			'profile': 'Profil',
			'experience': 'Erfaring',
			'workplace': 'Arbeidsgivere',
			'education': 'Utdanning'
		}, 
		'p': p, 
		't': t, 
		'e': e, 
		'w': w, 
		'd': d, 
		'img': data,
	}
	srcFile = 'cvtest.odt'
	rsltFile = 'resultatat.odt'
	r = Renderer(srcFile, dict, rsltFile, overwriteExisting=True)
	r.run()
	
	return HttpResponse("""
		<html><body>
			<h1>Fil skrevet</h1>
		</body></html>
		""")
	
	'''response = HttpResponse(open(rsltFile, 'rb').read(),mimetype='application/vnd.oasis.opendocument.text')
	response['Content-Disposition'] = 'attachment; filename=lol.odt'
	return response'''

def cvlist(request):
	all_persons = Person.objects.all()
	return render_to_response('cv/cvlist.html', {'all_persons': all_persons}, context_instance=RequestContext(request))
	
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
		if b != "" and a != " ": return b
		return ""
	
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
	
	return render_to_response('cv/cvpre.html', {'cv': cv, 'p': p, 't': t, 'e': e, 'w': w, 'd': d, 'o': o, 'l': l}, context_instance=RequestContext(request))

def mylogin(request):
	if request.method == 'POST':
		user = authenticate(username=request.POST['username'], password=request.POST['password'])
		if user is not None:
			if user.is_active:
				login(request, user)
				# You are now logged in, dog!
				return HttpResponseRedirect('/')
			else:
				# This account is stupid!
				return HttpResponseRedirect('/')
		else:
			# This didn't work lol
			return HttpResponseRedirect('/')
			
def mylogout(request):
	logout(request)
	return HttpResponseRedirect('/')