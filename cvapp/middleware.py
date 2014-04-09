from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.shortcuts import redirect
from localsettings import APP_NAME, APP_SECRET, DEBUG, SSO_URL, TESTTOKEN, TESTTOKEN2
import xml.etree.ElementTree as ET
import urllib
import urllib2
import logging
log = logging.getLogger('Middleware')

ACCESSROLES = [
	'ReadOnly',
	'Employee',
	'Manager',
	'Administrator',
]

class WhydahMiddleware(object):
	def process_request(self, request):
		if request.user.is_authenticated():
			return None
		else:
			if request.method == 'GET':
				# log.info("HOST:%s; FOR:%s; SERVER:%s;" % (request.META['HTTP_X_FORWARDED_HOST'],request.META['HTTP_X_FORWARDED_FOR'],request.META['HTTP_X_FORWARDED_SERVER']) )
				ticket = request.GET.get('userticket', False)
				# tokenid = request.COOKIES.get('whydahusertoken_sso', False)
				userToken = False

				if ticket:
					log.info('You are not logged in - Attempting log in')
					log.info('Ticket:')
					log.info(ticket)
					if ticket == 'test' and DEBUG:
						log.info('Initiating test-token')
						userToken = TESTTOKEN
					elif ticket == 'test2' and DEBUG:
						log.info('Initiating test-token2')
						userToken = TESTTOKEN2
					else:
						appToken = getAppToken(APP_NAME, APP_SECRET)
						log.info('Getting usertoken:')
						userToken = getUserToken(appToken, ticket, 'ticket')
						log.info(userToken)
				'''
				elif tokenid:
					log.info('You are not logged in - Attempting log in')
					log.info('Tokenid:')
					log.info(tokenid)
					appToken = getAppToken(APP_NAME, APP_SECRET)
					log.info('Getting usertoken:')
					userToken = getUserToken(appToken, tokenid, 'tokenid')
					log.info(userToken)
				'''

				if userToken:
					logged_in = loginUserWithToken(userToken, request)
					log.info('logged in: ')
					log.info(logged_in)
					if logged_in:
						return None
					else:
						log.info('cant log in with your token :( ')
						response = redirect('cv.views.myRemoteLogout')
						response['Location'] += '?path=https://' + request.get_host()
						return response
		return None

	def process_view(self, request, view_func, view_args, view_kwargs):
		viewFunctionName = view_func.__name__
		if not request.user.is_authenticated() and not viewFunctionName in ['myRemoteLogin','myRemoteLogout']:
			log.info('User not authenticated, redirecting to login-page...')
			return redirect('cv.views.myRemoteLogin')

def loginUserWithToken(token, request):

	token = ET.XML(token)

	useremail = False
	is_superuser = False
	firstname = token.findtext('firstname')
	lastname = token.findtext('lastname')

	tokengroups = []

	for application in token.iter('application'):
		if application.find('applicationName').text == 'ACS':
			for role in application.iter('role'):
				rolename = role.get('name')
				log.info('Role:')
				log.info(rolename)
				if rolename in ACCESSROLES:
					if rolename == 'Employee':
						if role.get('value') not in ['none', 'None', '']:
							useremail = role.get('value')
					if rolename == 'Administrator' or rolename == 'Manager':
						is_superuser = True
					tokengroups.append(rolename)

	if useremail:
		user, created = User.objects.get_or_create(username__iexact = useremail, defaults={'email': useremail, 'first_name': firstname, 'last_name': lastname, 'is_staff': True})
		currentgroups = user.groups.values_list('name', flat=True)
		for groupname in tokengroups:
			if groupname not in currentgroups:
				group, created = Group.objects.get_or_create(name=groupname)
				user.groups.add(group)
		for groupname in currentgroups:
			if groupname not in tokengroups:
				group, created = Group.objects.get_or_create(name=groupname)
				user.groups.remove(group)
		user.first_name = firstname
		user.last_name = lastname
		user.is_superuser = is_superuser
		user.is_staff = True
		user.save()
		user.backend = 'django.contrib.auth.backends.ModelBackend'
		request.user = user
		login (request, user)
		return True
	else:
		return False

def getAppToken(appID, appPass):
	values = { 'applicationcredential' : getAppCredXML(appID, appPass) }
	data = urllib.urlencode(values)
	request = urllib2.Request(SSO_URL+'tokenservice/logon', data)
	try:
		responsedata = urllib2.urlopen(request)
		return responsedata.read()
	except urllib2.URLError, e:
		log.error('URL-problem:')
		log.error(e)
		return False
	return False

def getUserToken(appToken, idvalue, idtype):
	if appToken:
		appTokenID = appToken[ appToken.find('<applicationtoken>')+len('<applicationtoken>') : appToken.find('</applicationtoken>') ]
		#appid = ET.XML(responsedata).find('applicationtoken')
		path = SSO_URL+'tokenservice/iam/%s/getusertokenby%s' % (appTokenID, idtype) # URL to be changed to 'getusertokenbyticket'
		values = { 'apptoken' : appToken, 'ticket' : idvalue, 'tokenid': idvalue } # ticketid-parameter to be changed to 'ticket'
		data = urllib.urlencode(values)
		request = urllib2.Request(path, data)
		try:
			responsedata = urllib2.urlopen(request)
			return responsedata.read()
		except urllib2.URLError, e:
			log.error('URL-problem:')
			log.error(e)
			log.error(path)
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
