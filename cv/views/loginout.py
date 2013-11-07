from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
import xml.etree.ElementTree as ET
import urllib
import urllib2
import logging
log = logging.getLogger("cv")

def mylogin(request):
	if request.method == 'POST':
		redirect_url = request.POST.get('path', '/')
		if not request.user.is_authenticated():
			if request.method == 'POST':
				# Request path gets the current url, not the origin of request
				redirect_url = request.POST.get('path', '/')
				user = authenticate(username=request.POST['username'], password=request.POST['password'])
				if user is not None and user.is_active:
					login(request, user)
					# You are now logged in, dog!
					return HttpResponseRedirect(redirect_url)
				else:
					# This account is stupid! Redirect to a login-page 
					pass
		else:
			logout(request)
	return HttpResponseRedirect(redirect_url)
			

def myRemoteLogin(request):
	if request.method == 'POST':
		redirect_url = 'https://' + request.get_host() + request.POST.get('path', '/')
		log.info(redirect_url)
		if request.user.is_authenticated():
			log.info('logging out')
			logout(request)
			response = HttpResponseRedirect(redirect_url)
			response.delete_cookie(key='whydahusertoken', path='/', domain='aaacs02.cloudapp.net')
			return response
		else:
			return HttpResponseRedirect("http://acs02.cloudapp.net/sso/login?redirectURI=" + redirect_url)
	else:
		return HttpResponseRedirect(redirect_url)
