from django.http import HttpResponse
from cv.models.cvmodels import Cv, Person, Technology, Experience, Workplace, Education, Other
import json
from collections import OrderedDict
from appy.pod.renderer import Renderer
from webodt.shortcuts import _ifile, render_to, render_to_response as rtr
from webodt.converters import converter
from webodt.helpers import get_mimetype
import settings

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
			imgUrl = settings.WWW_ROOT + a['photo']
			f = open(imgUrl, 'r')
			data = f.read()
			f.close()
		except:
			imgUrl = settings.WWW_ROOT + '/static/media/photos/blank.jpg'
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
	filename = p.name.encode('ascii', 'ignore')
	rsltFile = '/var/tmp/%s.odt' % filename
	r = Renderer(srcFile, dict, rsltFile, overwriteExisting=True)
	r.run()
	if format == "odt":
		response = HttpResponse(open(rsltFile, 'rb').read(), mimetype='application/vnd.oasis.opendocument.text')
		response['Content-Disposition'] = 'attachment; filename=%s %s Altran CV.odt' % (filename, c.title.encode('ascii', 'ignore').replace(" ", "_"))
		return response
	else:
		return rtr(filename+'.odt', filename='%s %s CV.%s' % (filename, c.title.encode('ascii', 'ignore').replace(" ", "_"), format), format=format) 
		# Works with GoogleDocs backend, but not pretty. Try OpenOffice backend instead.
