# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, Context
from django.http import HttpResponse
from django import http
from cv.models import Cv, Person, Technology, Experience, Workplace, Education, Other
from webodt.shortcuts import _ifile
import webodt
from reportlab.pdfgen import canvas
import json
import settings

from appy.pod.renderer import Renderer
import requests #get it http://docs.python-requests.org/en/latest/index.html

def index(request):
	return HttpResponse("""
		<html><body>
			<h1>Testing ODF-writing from Django</h1>
			<p><a href="odf/">OpenDocument with Picture-insert - Test</a></p>
		</body></html>
		""")

def getjpg(request, file_name):
	return HttpResponse("""
		<html><body>
			<h1>%s</h1>
		</body></html>
		""" % file_name)
		
def odtjson(request):
	
	a = json.loads(request.POST['cvjson'], strict=False)
	
	a['profile'] = a['profile'].replace('\n','<br/>').encode( "utf-8" )
	
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
		for x, item in a['technology'].iteritems():
			t_set.append( 
				Technology( 
					title		= item['title'], 
					data		= item['data']
				) 
			)
	
	if 'experience' in a:
		for x, item in a['experience'].iteritems():
			e_set.append( 
				Experience( 
					title		= item['title'], 
					from_year	= item['years'], # Must fix this later
					company		= item['company'],
					description = item['description'],
					techs		= item['techs'],
				) 
			)
	
	if 'workplace' in a:
		for x, item in a['workplace'].iteritems():
			w_set.append( 
				Workplace( 
					title		= item['title'], 
					from_year	= item['years'], # Must fix this later
					company		= item['company'],
					description = item['description'],
				) 
			)
	
	if 'education' in a:
		for x, item in a['education'].iteritems():
			d_set.append( 
				Education( 
					title		= item['title'], 
					from_year	= item['years'], # Must fix this later
					school		= item['school'],
					description = item['description'],
				) 
			)
	
	if 'other' in a:
		for x, item in a['other'].iteritems():
			o_set.append( 
				Other( 
					title		= item['title'], 
					data		= "<ul><li>" + item['data'].replace('\n','</li><li>').encode( "utf-8" ) + "</li></ul>"
				) 
			)
		
	dict = {
		'l': {
			'profile': 'Profil',
			'experience': 'Erfaring',
			'workplace': 'Arbeidsgivere',
			'education': 'Utdanning'
		}, 
		'p': a, 
		't': t_set, 
		'e': e_set,
		'w': w_set, 
		'd': d_set, 
		'o': o_set,
		'img': data,
	}
	srcFile = settings.PROJECT_ROOT + '/cv/cvjsontest.odt'
	rsltFile = '/tmp/%s.odt' % a['name']
	r = Renderer(srcFile, dict, rsltFile, overwriteExisting=True)
	r.run()
	response = HttpResponse(open(rsltFile, 'rb').read(), mimetype='application/vnd.oasis.opendocument.text')
	response['Content-Disposition'] = 'attachment; filename=%s %s CV.odt' % (a['name'], a['title'])
	return response

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

def odtlist(request):
	all_persons = Person.objects.all()
	return render_to_response('cv/odtlist.html', {'all_persons': all_persons}, context_instance=RequestContext(request))

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

'''
def odt(request):
	t = webodt.ODFTemplate('cvtest.zip')
	c = Context( {'navn':'Sky Lukewalker','tittel':'Champion','photo':'leontest','techs':{1:{'title':'Lang','data':'Java, C'},2:{'title':'Tools','data':'Eclipse, Confluence'}}} )
	d = t.render(c)
	response = HttpResponse(_ifile(d),mimetype='application/vnd.oasis.opendocument.text')
	response['Content-Disposition'] = 'attachment; filename=lol.odt'
	return response'''
	
def pdf(request):
	response = HttpResponse(mimetype='application/pdf')
	response['Content-Disposition'] = 'attachment; filename=test.pdf'
	p = canvas.Canvas(response)
	p.drawString(100, 100, "Hello world")
	p.showPage()
	p.save()
	return response
