from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
import csv
import localsettings

def reports(request):
	try:
		solrurl = localsettings.SOLRURL
	except:
		solrurl = "/solr/collection1/select"
	return render_to_response('reports/reports.html', {'solrurl': solrurl}, context_instance=RequestContext(request))

def reports_download(request):
	if(request.method == 'POST' and request.POST['data']):
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename="%s.csv' %  request.POST['name']

		writer = csv.writer(response)
		writer.writerow()

		return response