# -*- coding: utf-8 -*-

# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, Context
from django.http import HttpResponse, HttpResponseRedirect
from django import http
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from cv.models import Cv, Person, Technology, Experience, Workplace, Education, Other, Matrix, Competence, MatrixEntry, CompetenceEntry, Skillgroup
import webodt
import json

import requests #get it http://docs.python-requests.org/en/latest/index.html


def matrix_list(request):
	all_matrices = Matrix.objects.all()
	return render_to_response('competence/matrix_list.html', {'all_matrices': all_matrices}, context_instance=RequestContext(request))

def matrix_edit(request, m_id=False):
	m = {'title':"", 'description':"", 'legend':""}
	groupcount = 1
	comp = addfield('competence',1,groupnum=1)
	fields = addfield('group',1,nestedfields={'fields':comp,'count':1})
	groupcounter = '<input type="hidden" id="groupcounter" value="%d">' % groupcount
	return render_to_response('competence/matrix_edit.html', {'m': m, 'fields': fields,'groupcounter':groupcounter}, context_instance=RequestContext(request))

def matrix_load(request, m_id):
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
	return render_to_response('competence/matrix_edit.html', {'m': m, 'fields': fields,'groupcounter':groupcounter}, context_instance=RequestContext(request))

def matrix_load_bb(request, m_id):
	m = get_object_or_404(Matrix, pk=m_id)
	return render_to_response('competence/editmatrix_bb.html', {'m':m}, context_instance=RequestContext(request))	

def addfield(fieldtype, num, readonly="", groupnum="", title="", description="", existing_id = "", nestedfields=False):
    template = 'competence/groupcompetence.html'
    if existing_id:
    	readonly = 'disabled'
    dictionary = {
    	'fieldtype': fieldtype,
        'num': num,
        'groupnum': groupnum,
        'title': title,
        'description': description,
        'existing_id': existing_id,
        'nestedfields': nestedfields,
        'readonly': readonly
    }
    return render_to_string(template, dictionary)

def addcompetence(request):
	num = request.GET[u'num']
	groupnum = request.GET[u'groupnum']
	readonly = request.GET.get(u'readonly','')
	return HttpResponse(addfield('competence',num,groupnum=groupnum,readonly=readonly))

def addgroup(request):
	num = request.GET[u'num']
	comp = addfield('competence',1,groupnum=num)
	fields = addfield('group',num,nestedfields={'fields':comp,'count':1})
	return HttpResponse(fields)

def matrix_save(request):
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