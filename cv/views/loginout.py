from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout

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
			
def mylogout(request):
	logout(request)
	redirect_url = request.POST.get('path', '/')
	return HttpResponseRedirect(redirect_url)