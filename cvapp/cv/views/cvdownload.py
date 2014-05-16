# coding=UTF-8

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from cv.models.cvmodels import Cv, Person, Technology, Experience, Workplace, Education, Other, Template
import json
from collections import OrderedDict
from appy.pod.renderer import Renderer
from webodt.shortcuts import _ifile, render_to, render_to_response as rtr
from webodt.converters import converter
from webodt.helpers import get_mimetype
import settings
from xml.sax.saxutils import escape # escape string to valid xml
import string
from datetime import datetime

from cvhelper import labels, getTranslatedParts, getPeriod
from cv.templatetags.image_tags import scale

# For Zip
import os
import zipfile
import StringIO

# Default template
DEFAULT_TEMPLATE = settings.PROJECT_ROOT + '/templates/document/altrancvmal-2014-05-05.odt' 

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
            for x in a['technology']:
                t_set.append( 
                    Technology( 
                        title       = x['title'], 
                        data        = x['data'].encode( "utf-8", "ignore" )
                    ) 
                )
        
        if 'experience' in a:
            for x in a['experience']:
                e_set.append( 
                    Experience( 
                        title       = x['title'], 
                        from_year   = x['years'], # Must fix this later
                        company     = x['company'],
                        description = x['description'].encode( "utf-8" ),
                        techs       = x['techs'],
                    ) 
                )
        
        if 'workplace' in a:
            for x in a['workplace']:
                w_set.append( 
                    Workplace( 
                        title       = x['title'], 
                        from_year   = x['years'], # Must fix this later
                        company     = x['company'],
                        description = x['description'].encode( "utf-8" ),
                    ) 
                )
        
        if 'education' in a:
            for x in a['education']:
                d_set.append( 
                    Education( 
                        title       = x['title'], 
                        from_year   = x['years'], # Must fix this later
                        school      = x['school'],
                        description = x['description'].encode( "utf-8" ),
                    ) 
                )
        
        if 'other' in a:
            for x in a['other']:
                datalist = "<ul><li>" + x['data'].replace('<br/>','</li><li>') + "</li></ul>"
                o_set.append( 
                    Other( 
                        title       = x['title'], 
                        data        = datalist.encode( "utf-8", "ignore" )
                    ) 
                )
        
        p = get_object_or_404(Person, pk=a['personid'])

        # In case this has changed in the detailview, we change this temporarily (this is not saved)
        # Use case might be if someone wants a different phone number or contact number because the CV is sent via an agency
        p.name = a['name']
        p.phone = a['phone']
        p.mail = a['mail']
    
        imgdata, imgsizecm = getImgData(p.image)

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
            'img': imgdata,
            'imgsizecm': imgsizecm,
            'acs_datestamp': datetime.today().strftime('%Y-%m-%d'),
        }

        templateId = a.get('template', 'default')

    elif(request.GET['cvid']):
        dictionary = getCvDictionary(request.GET['cvid'])
        templateId = request.GET.get('template', 'default')

    if templateId != 'default':
        template = get_object_or_404(Template, pk=templateId)
        template = template.template.path
    else:
        template = DEFAULT_TEMPLATE
    
    rsltFile = renderOdt(dictionary, template=template)
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

    imgdata, imgsizecm = getImgData(p.image)

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
        'img': imgdata,
        'imgsizecm': imgsizecm,
        'acs_datestamp': datetime.today().strftime('%Y-%m-%d'),
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

def getImgData(img):

    # Get the imgdata
    try:
        imgpath = img.path.rsplit('.', 1)[0] + '_scale_300x300.jpg'
        f = open(imgpath, 'r')
        imgdata = f.read()
        f.close()
    except:
        try:
            scale(img, '300x300', dpi=(300,300))
            imgpath = img.path.rsplit('.', 1)[0] + '_scale_300x300.jpg'
            f = open(imgpath, 'r')
            imgdata = f.read()
            f.close()
        except:
            # Return empty jpg 1x1 bytestream
            return '\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xff\xe1\x00ZExif\x00\x00MM\x00*\x00\x00\x00\x08\x00\x05\x03\x01\x00\x05\x00\x00\x00\x01\x00\x00\x00J\x03\x03\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00Q\x10\x00\x01\x00\x00\x00\x01\x01\x00\x00\x00Q\x11\x00\x04\x00\x00\x00\x01\x00\x00\x0e\xc3Q\x12\x00\x04\x00\x00\x00\x01\x00\x00\x0e\xc3\x00\x00\x00\x00\x00\x01\x86\xa0\x00\x00\xb1\x8f\xff\xdb\x00C\x00\x02\x01\x01\x02\x01\x01\x02\x02\x02\x02\x02\x02\x02\x02\x03\x05\x03\x03\x03\x03\x03\x06\x04\x04\x03\x05\x07\x06\x07\x07\x07\x06\x07\x07\x08\t\x0b\t\x08\x08\n\x08\x07\x07\n\r\n\n\x0b\x0c\x0c\x0c\x0c\x07\t\x0e\x0f\r\x0c\x0e\x0b\x0c\x0c\x0c\xff\xdb\x00C\x01\x02\x02\x02\x03\x03\x03\x06\x03\x03\x06\x0c\x08\x07\x08\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x03\x01"\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa\x07"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\t\n\x16\x17\x18\x19\x1a%&\'()*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xc4\x00\x1f\x01\x00\x03\x01\x01\x01\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x11\x00\x02\x01\x02\x04\x04\x03\x04\x07\x05\x04\x04\x00\x01\x02w\x00\x01\x02\x03\x11\x04\x05!1\x06\x12AQ\x07aq\x13"2\x81\x08\x14B\x91\xa1\xb1\xc1\t#3R\xf0\x15br\xd1\n\x16$4\xe1%\xf1\x17\x18\x19\x1a&\'()*56789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00?\x00\xfd\xfc\xa2\x8a(\x03\xff\xd9', (0,0)

    # Get the imgwidth and height
    try:
        import Image
    except ImportError:
        try:
            from PIL import Image
        except ImportError:
            raise ImportError('Cannot import the Python Image Library.')
    try:
        image = Image.open(imgpath)
        imagesizecm =  [ (float(i)/300)*2.54 for i in image.size ]
    except:
        imagesizecm = (0,0)

    return imgdata, imagesizecm

def renderOdt(dictionary, tempfilename='tempcv', template=DEFAULT_TEMPLATE):

    # filename = dictionary['p'].name.encode('ascii', 'ignore') + ' - ' + dictionary['c'].title.encode('ascii', 'ignore').replace(",","").replace('/','') + ".odt"

    rsltFile = '/var/tmp/%s.odt' % tempfilename
    r = Renderer(template, dictionary, rsltFile, overwriteExisting=True)
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
        templateId = request.GET.get('template', DEFAULT_TEMPLATE)

        if templateId != 'default':
            template = get_object_or_404(Template, pk=templateId)
            template = template.template.path
        else:
            template = DEFAULT_TEMPLATE

        cvids = request.GET.getlist('cvid', False)

        if not cvids:
            return HttpResponseBadRequest('No CVs selected.')

        for cvid in cvids:
            cvdict = getCvDictionary(cvid, lang)
            renderedFile = renderOdt(cvdict, cvid, template)
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