from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import logout
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
	redirect_url = 'https://' + request.get_host()
	return HttpResponseRedirect( SSO_URL + "sso/logout?redirectURI=" + redirect_url)