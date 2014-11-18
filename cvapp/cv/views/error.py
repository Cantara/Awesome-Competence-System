from django.shortcuts import render_to_response
from django.template import RequestContext
from localsettings import SSO_URL

def error401(request):
	return render_to_response('401.html', {'SSO_URL': SSO_URL}, context_instance=RequestContext(request))

def error503(request):
	return render_to_response('503.html', {'SSO_URL': SSO_URL}, context_instance=RequestContext(request))