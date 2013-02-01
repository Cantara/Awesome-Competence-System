# -*- coding: utf-8 -*-

# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, Context
from django.http import HttpResponse, HttpResponseRedirect
from django import http
from django.template.loader import render_to_string
from cv.models import Cv, Person, Technology, Experience, Workplace, Education, Other, Style, Matrix, Competence, MatrixEntry, CompetenceEntry, Skillgroup
from webodt.shortcuts import _ifile, render_to_response as rtr
from webodt.converters import converter
import webodt
# import simplejson as json
import json
import settings
from collections import OrderedDict
from django.contrib.auth import authenticate, login, logout

from appy.pod.renderer import Renderer
import requests #get it http://docs.python-requests.org/en/latest/index.html

# Downloading a CV as ODT/DOC/PDF using the JSON submitted from the CVpreview
def download(request, format):
	
	if(request.POST['cvjson']):
	
		a = json.loads(request.POST['cvjson'], object_pairs_hook = OrderedDict, strict=False)
			
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
			imgUrl = settings.PROJECT_ROOT + '/static/media/photos/blank.jpg'
			f = open(imgUrl, 'r')
			data = f.read()
			f.close()
			#imgUrl = "http://www.freecode.no/wp-content/uploads/2012/03/FreeCode-black-300px.jpg"
			#re = requests.get(imgUrl)
			#data = re.content
		
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
		#get cvid from url and render the entire set of stuff from cv?
	
	doc=""
	if format != "odt": doc = "doc"
	
	srcFile = settings.PROJECT_ROOT + '/cv/cvjsontest%s.odt' % doc
	
	rsltFile = '/tmp/%s.odt' % p.name.encode('ascii', 'ignore')
	r = Renderer(srcFile, dict, rsltFile, overwriteExisting=True)
	r.run()
	if format == "odt":
		response = HttpResponse(open(rsltFile, 'rb').read(), mimetype='application/vnd.oasis.opendocument.text')
		response['Content-Disposition'] = 'attachment; filename=%s %s Altran CV.odt' % (p.name.encode('ascii', 'ignore'), c.title.encode('ascii', 'ignore').replace(" ", "_"))
		return response
	else:
		return rtr(p.name.encode('ascii', 'ignore')+'.odt', filename='%s %s Freecode CV.%s' % (p.name.encode('ascii', 'ignore'), c.title.encode('ascii', 'ignore').replace(" ", "_"), format), format=format) 
		# Works with GoogleDocs backend, but not pretty. Try OpenOffice backend instead.

def cvlist(request):
	all_persons = Person.objects.all()
	# style = Style.objects.get(id=1)
	return render_to_response('cv/cvlist.html', {'all_persons': all_persons, 'style': ''}, context_instance=RequestContext(request))

def cvlisted(request):
	all_persons = Person.objects.all()
	# style = Style.objects.get(id=1)
	return render_to_response('cv/cvlisted.html', {'all_persons': all_persons}, context_instance=RequestContext(request))
	
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
		
	# style = Style.objects.get(id=1)
	
	return render_to_response('cv/cvpre.html', {'cv': cv, 'p': p, 't': t, 'e': e, 'w': w, 'd': d, 'o': o, 'l': l, 'style': ''}, context_instance=RequestContext(request))

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

def matrices(request):
	all_matrices = Matrix.objects.all()
	return render_to_response('competence/matrices_list.html', {'all_matrices': all_matrices}, context_instance=RequestContext(request))
	#return HttpResponse("Hello, world. MANY MANTRICEX.")

def editmatrix(request, m_id=False):
	m = {'title':"", 'description':"", 'legend':""}
	if not m_id:
		groupcount = 1
		comp = addfield('competence',1,groupnum=1)
		fields = addfield('group',1,nestedfields={'fields':comp,'count':1})
		groupcounter = '<input type="hidden" id="groupcounter" value="%d">' % groupcount
	else:
		groupcount = 1
		comp = addfield('competence',1,groupnum=1)
		fields = addfield('group',1,nestedfields={'fields':comp,'count':1})
		groupcounter = '<input type="hidden" id="groupcounter" value="%d">' % groupcount
		groupcounter += '<input type="hidden" id="m_id" value="%s">' % m_id
	return render_to_response('competence/editmatrix.html', {'m': m, 'fields': fields,'groupcounter':groupcounter}, context_instance=RequestContext(request))

def addfield(fieldtype, num, groupnum="", title="", description="", nestedfields=False):
    template = 'competence/groupcompetence.html'
    dictionary = {
    	'fieldtype': fieldtype,
        'num': num,
        'groupnum': groupnum,
        'title': title,
        'description': description,
        'nestedfields': nestedfields
    }
    return render_to_string(template, dictionary)

def addcompetence(request):
	num = request.GET[u'num']
	groupnum = request.GET[u'groupnum']
	return HttpResponse(addfield('competence',num,groupnum=groupnum))

def addgroup(request):
	num = request.GET[u'num']
	comp = addfield('competence',1,groupnum=num)
	fields = addfield('group',num,nestedfields={'fields':comp,'count':1})
	return HttpResponse(fields)

def savematrix(request):
	data = json.loads(request.raw_post_data)
	if 'm_id' in data:
		message = "Overwrite existing not implemented"
	else:
		m = Matrix(
			title = data['title'],
			description = data['description'],
			legend = data['legend']
			)
		m.save()
		message = m.id
		if 'group' in data:
			for x, group in data['group'].items():
				s = Skillgroup( 
					matrix = m,
					title = data['group'][x]['title'], 
					description = data['group'][x]['description']
					)
				s.save()
				if 'competence' in data['group'][x]:
					for y, comp in data['group'][x]['competence'].items():
						if data['group'][x]['competence'][y]['existing_id']:
							# check if it has existing id
							try:
								e_id = int( data['group'][x]['competence'][y]['existing_id'] )
								# Should try to see if the ID returns a valid entry
								c = Competence.objects.get( id = e_id )
								c.skillgroup.add(s)
								c.save()
							except ValueError:
								pass
						else:
							c = Competence(
								label = data['group'][x]['competence'][y]['label'],
								description = data['group'][x]['competence'][y]['description'],
								)
							c.save()
							c.skillgroup.add(s)
							c.save()
	return HttpResponse(m.id)

def matrixentry(request, m_id):
	matrix = get_object_or_404(Matrix, pk=m_id)
	all_persons = Person.objects.all()
	return render_to_response('competence/matrix.html', {'matrix': matrix, 'all_persons': all_persons}, context_instance=RequestContext(request))
	#return HttpResponse("Hello, world. competencematrixentry: " + matrix.name + lol)

def addentry(request):
	
	a = json.loads(request.body)
	p_id = a['person_id']
	m_id = a['matrix_id']
	e_id = ""

	# Check if there's already an existing entry with person_id and matrix_id
	try:
		entry = CompetenceMatrixEntry.objects.get(person=p_id, matrix = m_id)
		# get the id
		e_id = entry.id
	except CompetenceMatrixEntry.DoesNotExist:
	# ELSE Create new entry with person_id and matrix_id
		p = Person.objects.get(pk=p_id)
		m = CompetenceMatrix.objects.get(pk=m_id)
		entry = CompetenceMatrixEntry(person=p, matrix=m)
		entry.save()
		# get the entry_id
		e_id = entry.id
	
	# create fieldentries with field_id + entry_id
	for f_id in a['field'].keys():
		try:
			fieldentry = CompetenceFieldEntry.objects.get(competencematrixentry=e_id, competencefield=f_id)
			fieldentry.competencerating = int(a['field'][f_id])
			fieldentry.save()
		except CompetenceFieldEntry.DoesNotExist:
			f_id_int=int(f_id)
			cfield = CompetenceField.objects.get(pk=f_id_int)
			fieldentry = CompetenceFieldEntry(competencematrixentry=entry, competencefield=cfield, competencerating=int(a['field'][f_id]))
			fieldentry.save()

	return HttpResponse(e_id)

def loadentry(request):

	a = json.loads(request.body)
	p_id = a['person_id']
	m_id = a['matrix_id']

	# Check if there's already an existing entry with person_id and matrix_id
	try:
		entry = MatrixEntry.objects.get(person=p_id, matrix = m_id)
		# get the id
		e_id = entry.id

		for c_id in a['field'].keys():
			try:
				fieldentry = CompetenceEntry.objects.get(matrixentry=e_id, competence=c_id)
				a['field'][f_id] = fieldentry.competencerating
			except CompetenceEntry.DoesNotExist:
				pass

		return HttpResponse( json.dumps(a) )

	except MatrixEntry.DoesNotExist:
		return HttpResponse("No entry found")
	# entry = CompetenceMatrixEntry.get(person=person_id)
	# Get person_id and matrix_id from json data
	# Get cmatrixentry from m_id and p_id
	# return cmatrixentrydata with cfieldentries OR return empty (no entries)
