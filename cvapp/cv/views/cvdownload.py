# coding=UTF-8

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from cv.models.cvmodels import Cv, Person, Technology, Experience, Workplace, Education, Other
import json
from collections import OrderedDict
from appy.pod.renderer import Renderer
from webodt.shortcuts import _ifile, render_to, render_to_response as rtr
from webodt.converters import converter
from webodt.helpers import get_mimetype
import settings
from xml.sax.saxutils import escape # escape string to valid xml
import string
from datetime import date

from cvhelper import labels, getTranslatedParts, getPeriod

# For Zip
import os
import zipfile
import StringIO

# Downloading a CV as ODT/DOC/PDF using the JSON submitted from the CVpreview
def download(request, format):
	if(request.method == 'POST' and request.POST['cvjson']):
	
		a = json.loads(request.POST['cvjson'], object_pairs_hook = OrderedDict, strict=False)
					
		cv = Cv(
			title = a['title'],
			profile = a['profile'].encode( "utf-8" ),
		)
		
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
						data		= item['data'].encode( "utf-8", "ignore" )
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
		
		p = get_object_or_404(Person, pk=a['personid'])

		# In case this has changed in the detailview, we change this temporarily (this is not saved)
		# Use case might be if someone wants a different phone number or contact number because the CV is sent via an agency
		p.name = a['name']
		p.phone = a['phone']
		p.mail = a['mail']
		
		try:
			imgUrl = p.image.path.rsplit('.', 1)[0] + '_scale_110x110.jpg'
		except:
			imgUrl = settings.WWW_ROOT + 'static/media/photos/blank.jpg'
		f = open(imgUrl, 'r')
		data = f.read()
		f.close()


		languagecode = p.country()
		if not languagecode or a['lang'] == 'en':
			languagecode = 'en'
			
		l = labels[languagecode]

		info = []
		if a['phone']:
			info.append(l['phone']+': '+a['phone'])
		if a['mail']:
			info.append(l['email']+': '+a['mail'])
		if a['age']: 
			info.append( '%s: %s' % (l['age'], a['age']) )
		infoline = '<text:p text:style-name="P1">' + '<text:line-break></text:line-break>'.join(info) + '</text:p>'

		dictionary = {
			'l': l,
			'a': a, # Contains age (as it is calculated and don't need special encoding - Also, it doesn't exist in the model :-/ )
			'p': p, # Person-related data
			'c': cv, # CV-related data
			't': t_set, 
			'e': e_set,
			'w': w_set, 
			'd': d_set, 
			'o': o_set,
			'infoline': infoline,
			'img': data,
			'acs_datestamp': date.today().isoformat(),
		}

	elif(request.GET['cvid']):
		dictionary = getCvDictionary(request.GET['cvid'])
	
	rsltFile = renderOdt(dictionary)
	filename = dictionary['p'].name.encode('ascii', 'ignore') + ' - ' + dictionary['c'].title.encode('ascii', 'ignore').replace(",","") + "_Altran"

	if format == "odt":
		response = HttpResponse( open(rsltFile, 'rb').read(), mimetype='application/vnd.oasis.opendocument.text' )
		response['Content-Disposition'] = 'attachment; filename=%s.odt' % filename
		return response
	else:
		return rtr('tempcv.odt', filename='%s.%s' % (filename, format), format=format)

def getCvDictionary(cvid, lang=''):
	cv = get_object_or_404(Cv, pk=cvid)
	p = cv.person

	# lang only toggles between English or Native
	# languagecode toggles between Norwegian, Swedish and English for the labels
	
	languagecode = p.country()
	if not languagecode or lang == 'en':
		languagecode = 'en'

	try:
		imgUrl = p.image.path.rsplit('.', 1)[0] + '_scale_110x110.jpg'
	except:
		imgUrl = settings.WWW_ROOT + 'static/media/photos/blank.jpg'
	f = open(imgUrl, 'r')
	data = f.read()
	f.close()

	t, e, w, d, o, l = getTranslatedParts(cv, lang)
	
	cv.profile = cv.profile.encode('utf-8')
	
	for ot in o:
		ot.data = escape( ot.data.encode('utf-8') )
		ot.data = '<ul><li>' + '</li><li>'.join( ot.data_as_list() ) + '</li></ul>'

	for te in t:
		te.data = escape( te.data.encode('utf-8') )

	l = labels[languagecode]

	dictionary = {
		'l': l,
		'p': p,
		'c': cv,
		't': t, 
		'e': e,
		'w': w, 
		'd': d, 
		'o': o,
		'infoline': getInfoLine(p,l),
		'img': data,
		'acs_datestamp': date.today().isoformat(),
	}

	return dictionary

def getInfoLine(p, l):
	info = []
	if p.phone:
		info.append(l['phone']+': '+p.phone)
	if p.mail:
		info.append(l['email']+': '+p.mail)
	if p.age() != "" and p.age() > 0: 
		info.append( '%s: %s' % (l['age'], p.age()) )
	return '<text:p text:style-name="P1">' + '<text:line-break></text:line-break>'.join(info) + '</text:p>'

def renderOdt(dictionary, tempfilename='tempcv'):

	srcFile = settings.PROJECT_ROOT + '/templates/document/altrancvmal-2014-03-18.odt'

	# filename = dictionary['p'].name.encode('ascii', 'ignore') + ' - ' + dictionary['c'].title.encode('ascii', 'ignore').replace(",","").replace('/','') + ".odt"

	rsltFile = '/var/tmp/%s.odt' % tempfilename
	r = Renderer(srcFile, dictionary, rsltFile, overwriteExisting=True)
	r.run()

	return rsltFile

def renderDocPdf(odtfile, format):
	docfile = render_to(format, odtfile)
	return os.path.abspath(docfile.name)

def multicv(request):
	if(request.method == 'GET'):
		
		filenames = []
		
		format = request.GET['format']
		lang = request.GET['language']

		cvids = request.GET.getlist('cvid', False)

		if not cvids:
			return HttpResponseBadRequest('No CVs selected.')

		for cvid in cvids:
			cvdict = getCvDictionary(cvid, lang)
			renderedFile = renderOdt(cvdict, cvid)
			renderedName = format_filename( "%s-%s.%s" % (cvdict['p'].name, cvdict['c'].title, format) )
			if( format != 'odt' ):
				renderedFile = renderDocPdf(renderedFile, format)
			filenames.append( (renderedFile, renderedName) )

		# Folder name in ZIP archive which contains the above files
		# E.g [thearchive.zip]/somefiles/file2.txt
		# FIXME: Set this to something better
		zip_subdir = "altrancv"
		zip_filename = "%s.zip" % zip_subdir

		# Open StringIO to grab in-memory ZIP contents
		s = StringIO.StringIO()

		# The zip compressor
		zf = zipfile.ZipFile(s, "w")

		for fpath in filenames:
			# Calculate path for file in zip
			# fdir, fname = os.path.split(fpath[0])
			fname = fpath[1]
			zip_path = os.path.join(zip_subdir, fname)

			# Add file, at correct path
			zf.write(fpath[0], zip_path)

		# Must close zip for all contents to be written
		zf.close()

		# Grab ZIP file from in-memory, make response with correct MIME-type
		resp = HttpResponse(s.getvalue(), mimetype = "application/x-zip-compressed")
		# ..and correct content-disposition
		resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename

		return resp

def format_filename(s):
	valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
	filename = ''.join(c for c in s if c in valid_chars)
	filename = filename.replace(' ','_') # I don't like spaces in filenames.
	return filename