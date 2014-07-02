from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
import xml.etree.ElementTree as ET
import urllib
import urllib2
import logging
from localsettings import SSO_URL
log = logging.getLogger("cv")

def myRemoteLogin(request):
	if request.method == 'GET':
		redirect_url = 'https://' + request.get_host() + request.GET.get('path', '/')
		if request.user.is_authenticated():
			return HttpResponseRedirect( SSO_URL + "sso/logoutaction?redirectURI=" + redirect_url)
		else:
			return HttpResponseRedirect( SSO_URL + "sso/login?redirectURI=" + redirect_url)
	else:
		return HttpResponseRedirect('https://' + request.get_host() )

def myRemoteLogout(request):
	logout(request)
	response = HttpResponseRedirect('https://' + request.get_host())
	response.delete_cookie(key='whydahusertoken_sso')
	response.delete_cookie(key='whydahusertoken_sso', path='/', domain=request.get_host() )
	response.set_cookie('whydahusertoken_sso','')
	if request.method == 'GET':
		redirect_url = 'https://' + request.get_host() + request.POST.get('path', '/')
	else:
		redirect_url = 'https://' + request.get_host()
	return HttpResponseRedirect( SSO_URL + "sso/logoutaction?redirectURI=" + redirect_url)