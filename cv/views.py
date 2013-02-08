# -*- coding: utf-8 -*-

# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, Context
from django.http import HttpResponse, HttpResponseRedirect
from django import http
from django.core.exceptions import ObjectDoesNotExist
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
		redirect_url = request.POST['redirect_url']
		user = authenticate(username=request.POST['username'], password=request.POST['password'])
		if user is not None:
			if user.is_active:
				login(request, user)
				# You are now logged in, dog!
				return HttpResponseRedirect(redirect_url)
			else:
				# This account is stupid!
				return HttpResponseRedirect(redirect_url)
		else:
			# This didn't work lol
			return HttpResponseRedirect(redirect_url)
			
def mylogout(request):
	logout(request)
	return HttpResponseRedirect('/')

def matrices(request):
	all_matrices = Matrix.objects.all()
	return render_to_response('competence/matrices_list.html', {'all_matrices': all_matrices}, context_instance=RequestContext(request))
	#return HttpResponse("Hello, world. MANY MANTRICEX.")

def editmatrix(request, m_id=False):
	m = {'title':"", 'description':"", 'legend':""}
	groupcount = 1
	comp = addfield('competence',1,groupnum=1)
	fields = addfield('group',1,nestedfields={'fields':comp,'count':1})
	groupcounter = '<input type="hidden" id="groupcounter" value="%d">' % groupcount
	return render_to_response('competence/editmatrix.html', {'m': m, 'fields': fields,'groupcounter':groupcounter}, context_instance=RequestContext(request))

def loadmatrix(request, m_id):
	m = get_object_or_404(Matrix, pk=m_id)
	groupcount = m.skillgroup_set.count()
	# For each group
	fields = ''
	for x, g in enumerate( m.skillgroup_set.all().order_by('title') ):
		comps = ''
		compcount = g.competence_set.count()
		for y, c in enumerate( g.competence_set.all().order_by('title') ):
			comps += addfield('competence', y, groupnum=x, title=c.title, description=c.description, existing_id=c.id)
		fields += addfield('group', x, nestedfields={'fields':comps,'count': compcount}, title=g.title, description=g.description, existing_id=g.id)
	groupcounter = '<input type="hidden" id="groupcounter" value="%d">' % groupcount
	groupcounter += '<input type="hidden" id="m_id" value="%s">' % m_id
	return render_to_response('competence/editmatrix.html', {'m': m, 'fields': fields,'groupcounter':groupcounter}, context_instance=RequestContext(request))

def addfield(fieldtype, num, groupnum="", title="", description="", existing_id = "", nestedfields=False):
    template = 'competence/groupcompetence.html'
    dictionary = {
    	'fieldtype': fieldtype,
        'num': num,
        'groupnum': groupnum,
        'title': title,
        'description': description,
        'existing_id': existing_id,
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
	response_data = {}
	
	m_id = data['m_id']

	if m_id:
		response_data['action'] = 'saveOld'
		response_data['message'] = 'Old matrix saved'
	else:
		response_data['action'] = 'saveNew'
		response_data['message'] = 'New Matrix saved'
		m_id = 0

	try:
		m = Matrix.objects.get(pk=m_id)
	except (ObjectDoesNotExist, ValueError) as e:
		m = Matrix( title='M' )
	m.title = data['title']
	m.description = data['description']
	m.legend = data['legend']
	m.save()

	response_data['m_id'] = m.id

	if 'group' in data:
		for x, group in data['group'].iteritems():
			s_id = data['group'][x].get('existing_id')
			try:
				s = Skillgroup.objects.get(pk=int(s_id))
			except (ObjectDoesNotExist, ValueError) as e:
				s = Skillgroup( matrix=m, title='S' )
			s.title = data['group'][x].get('title')
			s.description = data['group'][x].get('description')
			s.save()

			if 'competence' in data['group'][x]:
				for y, comp in data['group'][x]['competence'].iteritems():
					c_id = data['group'][x]['competence'][y]['existing_id']
					try:
						c = Competence.objects.get( pk= int(c_id) )
					except (ObjectDoesNotExist, ValueError) as e:
						c = Competence( title='C' )
						c.save()
					c.title = data['group'][x]['competence'][y].get('title')
					c.description = data['group'][x]['competence'][y].get('description')
					c.skillgroup.add(s)
					c.save()

	return HttpResponse(json.dumps(response_data), mimetype="application/json")

def matrixentry(request, m_id):
	matrix = get_object_or_404(Matrix, pk=m_id)
	all_persons = Person.objects.all()
	return render_to_response('competence/matrix.html', {'matrix': matrix, 'all_persons': all_persons}, context_instance=RequestContext(request))
	#return HttpResponse("Hello, world. competencematrixentry: " + matrix.name + lol)

def saveentry(request):
	
	a = json.loads(request.body)
	p_id = a['person_id']
	m_id = a['matrix_id']
	me_id = ""

	p = Person.objects.get(pk=p_id)
	m = Matrix.objects.get(pk=m_id)

	# Check if there's already an existing entry with person_id and matrix_id
	try:
		entry = MatrixEntry.objects.get(person=p_id, matrix = m_id)
		# get the id
		me_id = entry.id
	except MatrixEntry.DoesNotExist:
	# ELSE Create new entry with person_id and matrix_id
		entry = MatrixEntry(person=p, matrix=m)
		entry.save()
		# get the entry_id
		me_id = entry.id

	# create fieldentries with field_id + entry_id
	for c_id in a['competence'].keys():
		try:
			competenceentry = CompetenceEntry.objects.get( person=p_id, competence=c_id )
			competenceentry.competencerating = int( a['competence'][c_id] )
			competenceentry.save()
		except CompetenceEntry.DoesNotExist:
			c_id_int = int(c_id)
			competence = Competence.objects.get( pk = c_id_int )
			competenceentry = CompetenceEntry( person=p, competence=competence, rating=int( a['competence'][c_id]) )
			competenceentry.save()

	message = ""
	for c_id in a['compexp'].keys():
		# 1. get a list of all exp
		# 2. get a list of all checked exp
		# 3. get the current competence ID
		# 4. For all exp
		#    - Check if a link exists between the comp and exp
		#    - If it exists, and is not in 'checked'
		#      - Delete
		#    - Elif it doesn't exist and is in "checked"
		#    - Create it

		for checked_exp in a['compexp'][c_id]:
			message += "HEI" + checked_exp
		for e_id in p.experience_set.all():
			pass

	return HttpResponse( message )

def loadentry(request):

	a = json.loads(request.body)
	p_id = a['person_id']
	m_id = a['matrix_id']

	# Check if there's already an existing entry with person_id and matrix_id
	try:
		entry = MatrixEntry.objects.get(person=p_id, matrix = m_id)
		# get the id
		me_id = entry.id
	except MatrixEntry.DoesNotExist:
		pass

	# Need to add some rating of the matrix and comment

	for c_id in a['competence'].keys():
		try:
			centry = CompetenceEntry.objects.get(person=p_id, competence=c_id)
			a['competence'][c_id] = centry.rating
		except CompetenceEntry.DoesNotExist:
			a['competence'][c_id] = 0

	return HttpResponse( json.dumps(a) )

def addexppicker(request):
	if request.method == 'POST':
		j = json.loads( request.raw_post_data )
		p = get_object_or_404( Person, pk=j.get('p_id') )
	return render_to_response('competence/exppicker.html', {'p': p, 'hidden': j.get('hidden'), 'c_id': j.get('c_id')})

def ajaxcompetencelist(request):
	q = request.GET['term']
	try:
		result = Competence.objects.filter(title__icontains=q)
		c_set = []
		for c in result:
			c_set.append({
				'value': c.title,
				'data': {
					'description': c.description,
					'id': c.id
				}
				})
		result = c_set
	except ObjectDoesNotExist:
		result = {}
	return HttpResponse( json.dumps(result), mimetype="application/json" )