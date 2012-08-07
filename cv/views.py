# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, Context
from django.http import HttpResponse
from django import http
from cv.models import Person
from webodt.shortcuts import _ifile
import webodt
from reportlab.pdfgen import canvas

from appy.pod.renderer import Renderer
import requests #get it http://docs.python-requests.org/en/latest/index.html

def index(request):
    return HttpResponse("""
        <html><body>
            <h1>Testing ODF-writing from Django</h1>
            <p><a href="odf/">OpenDocument with Picture-insert - Test</a></p>
        </body></html>
        """)

def odt(request, person_id=1):

	p = get_object_or_404(Person, pk=person_id)
	
	imgUrl = p.photo
	re = requests.get(imgUrl)
	data = re.content
	p.profile = p.profile.replace('\n','<br/>')
	pro = p.profile.encode( "utf-8" )
	p.profile = pro
	t = p.technologies_set.all()
	e = p.experience_set.all()
	w = p.workplaces_set.all()
	d = p.education_set.all()
	dict = {
		'l': {
			'profile': 'Profil',
			'experience': 'Erfaring',
			'workplaces': 'Arbeidsgivere',
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
	return render_to_response('cv/index.html', {'all_persons': all_persons}, context_instance=RequestContext(request))
	
def detail(request, person_id, arg1 = '', arg2 = ''):
	p = get_object_or_404(Person, pk=person_id)
	t = p.technologies_set.all()
	e = p.experience_set.all()
	w = p.workplaces_set.all()
	d = p.education_set.all()
	o = p.others_set.all()
	
	# If they want English, give them English
	if arg1 == 'eng' or arg2 == 'eng':
		p.profile = p.profile_en
		p.title = p.title_en
		
		for te in t:
			te.title = te.title_en
		
		for ex in e:
			ex.title = ex.title_en
			ex.company = ex.company_en
			ex.description = ex.description_en
			
		for wp in w:
			wp.title = wp.title_en
			wp.company = wp.company_en
			
		for du in d:
			du.title = du.title_en
			du.school = du.school_en
		
		for ot in o:
			ot.title = ot.title_en
			ot.data = ot.data_en
		
		# English subheaders
		l = {
			'profile': 'Profile',
			'experience': 'Experience',
			'workplaces': 'Workplaces',
			'education': 'Education',
		}
	else:
		# Norwegian subheaders
		l = {
			'profile': 'Profil',
			'experience': 'Erfaring',
			'workplaces': 'Arbeidsgivere',
			'education': 'Utdanning',
		}
		
	if arg1 == 'doc' or arg2 == 'doc':
		doc = True
	else:
		doc = False
	
	return render_to_response('cv/detail.html', {'person': p, 't': t, 'e': e, 'w': w, 'd': d, 'o': o, 'l': l, 'doc': doc}, context_instance=RequestContext(request))

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