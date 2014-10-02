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
				userTicket = request.GET.get('userticket', False)
				# tokenid = request.COOKIES.get('whydahusertoken_sso', False)
				userToken = False

				if userTicket:
					log.info('You are not logged in - Attempting log in')
					log.info('Userticket:')
					log.info(userTicket)
					if userTicket == 'test' and DEBUG:
						log.info('Initiating test-token')
						userToken = TESTTOKEN
					elif userTicket == 'test2' and DEBUG:
						log.info('Initiating test-token2')
						userToken = TESTTOKEN2
					else:
						appToken = getAppToken(APP_NAME, APP_SECRET)
						log.info('Getting usertoken:')
						userToken = getUserToken(appToken, userTicket, 'userticket')
						log.info(userToken)
	
				if userToken:
					logged_in = loginUserWithToken(userToken, request)
					log.info('logged in: ')
					log.info(logged_in)
					if logged_in:
						return None
					else:
						log.info("Can't log in with your token :(")
						#response = redirect('cv.views.myRemoteLogout')
						#response['Location'] += '?path=https://' + request.get_host()
						return unauthorizedResponse(request)
		return None

	def process_view(self, request, view_func, view_args, view_kwargs):
		viewFunctionName = view_func.__name__
		log.info(viewFunctionName)
		if not request.user.is_authenticated() and not viewFunctionName in ['myRemoteLogin','myRemoteLogout','error401']:
			log.info('User not authenticated, redirecting to login-page...')
			log.info('Escaped path:')
			escaped_path = urllib.quote(request.get_full_path())
			log.info(escaped_path)
			escaped_path = urllib.quote(escaped_path)
			log.info(escaped_path)
			return redirect( '/login/?path='+escaped_path )

def unauthorizedResponse(request):
	logout(request)
	response = HttpResponseRedirect('https://' + request.get_host())
	response.delete_cookie(key='whydahusertoken_sso')
	response.delete_cookie(key='whydahusertoken_sso', path='/', domain=request.get_host() )
	response.set_cookie('whydahusertoken_sso','')
	response.status_code = 401
	if request.method == 'GET':
		redirect_url = 'https://' + request.get_host() + request.POST.get('path', '/')
	else:
		redirect_url = 'https://' + request.get_host()
	return HttpResponseRedirect('error401')

def loginUserWithToken(userToken, request):

	userToken = ET.XML(userToken)

	useremail = False
	is_superuser = False
	firstname = userToken.findtext('firstname')
	lastname = userToken.findtext('lastname')

	tokengroups = []

	for application in userToken.iter('application'):
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

	if not useremail and 'Manager' in tokengroups:
		useremail = userToken.findtext('username')
		log.info('Manager username bypass')
		log.info(useremail)

	if useremail:
		user, created = User.objects.get_or_create(username__iexact = useremail, defaults={'username': useremail, 'email': useremail, 'first_name': firstname, 'last_name': lastname, 'is_staff': True})
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
		log.info('Trying to get appToken')
		log.info(values)
		responsedata = urllib2.urlopen(request)
		return responsedata.read()
	except urllib2.URLError, e:
		log.error('URL-problem:')
		log.error(e)
		return False
	return False

def getUserToken(appToken, idvalue, idtype):
	if appToken:
		appTokenID = appToken[ appToken.find('<applicationtokenID>')+len('<applicationtokenID>') : appToken.find('</applicationtokenID>') ]
		#appid = ET.XML(responsedata).find('applicationtoken')
		path = SSO_URL+'tokenservice/user/%s/get_usertoken_by_%s' % (appTokenID, idtype) 
		values = { 'apptoken' : appToken, 'userticket' : idvalue }
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
