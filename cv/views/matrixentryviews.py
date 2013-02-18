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

def matrix_entry_get(request, m_id):
	matrix = get_object_or_404(Matrix, pk=m_id)
	all_persons = Person.objects.all()
	if request.user.is_authenticated():
		current_person = get_object_or_404(Person, user=request.user)
	else:
		current_person = {}
	return render_to_response('competence/matrix_entry.html', {'matrix': matrix, 'all_persons': all_persons, 'current_person': current_person}, context_instance=RequestContext(request))
	#return HttpResponse("Hello, world. competencematrixentry: " + matrix.name + lol)

def matrix_entry_save(request):
	
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
			c = Competence.objects.get( pk=int(c_id) )
			competenceentry = CompetenceEntry.objects.get( person=p, competence=c )
			competenceentry.rating = int( a['competence'][c_id] )
			competenceentry.save()
		except CompetenceEntry.DoesNotExist:
			c = Competence.objects.get( pk = int(c_id) )
			competenceentry = CompetenceEntry( person=p, competence=c, rating=int( a['competence'][c_id]) )
			competenceentry.save()

	message = ""

	try:
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
	except KeyError:
		pass

	return HttpResponse( message )

def matrix_entry_load(request):

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
