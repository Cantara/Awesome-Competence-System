from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
import xml.etree.ElementTree as ET
import urllib
import urllib2
import logging
log = logging.getLogger('cv')

class WhydahMiddleware(object):
	def process_request(self, request):
		if request.user.is_authenticated():
			log.info('You are logged in')
			return
		else:
			log.info('You are not logged in - Attempting log in')
			if request.method == 'GET':
				userTokenID = request.COOKIES.get('whydahusertoken')
				if userTokenID is not None:
					appToken = getAppToken('Styrerommet', 'dummy')
					userToken = getUserToken(appToken, userTokenID)
					if userToken:
						userTokenXML = ET.XML(userToken)
						userName = userTokenXML.findtext('uid')
						useremail = userTokenXML.find('email')
						user, created = User.objects.get_or_create(username = userName)
						user.backend = 'django.contrib.auth.backends.ModelBackend'
						request.user = user
						login (request, user)
						return HttpResponseRedirect("http://acs02.cloudapp.net/")

def getAppToken(appID, appPass):
	values = { 'applicationcredential' : getAppCredXML(appID, appPass) }
	data = urllib.urlencode(values)
	request = urllib2.Request('http://acs02.cloudapp.net/tokenservice/logon', data)
	try:
		responsedata = urllib2.urlopen(request)
		return responsedata.read()
	except urllib2.URLError, e:
		log.error('URL-problem:')
		log.error(e)
		return False
	return False

def getUserToken(appToken, userTokenID):
	if appToken:
		appTokenID = appToken[ appToken.find('<applicationtoken>')+len('<applicationtoken>') : appToken.find('</applicationtoken>') ]
		#appid = ET.XML(responsedata).find('applicationtoken')
		path = 'http://acs02.cloudapp.net/tokenservice/iam/%s/getusertokenbytokenid' % appTokenID
		values = { 'apptoken' : appToken, 'usertokenid' : userTokenID }
		data = urllib.urlencode(values)
		request = urllib2.Request(path, data)
		try:
			responsedata = urllib2.urlopen(request)
			return responsedata.read()
		except urllib2.URLError, e:
			log.error('URL-problem:')
			log.error(e)
			return False
	return False

def getAppCredXML(appID, appPass):
	return  '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<applicationcredential>
    <params>
        <applicationID>%s</applicationID>
        <applicationSecret>%s</applicationSecret>
    </params>
</applicationcredential>''' % (appID, appPass)