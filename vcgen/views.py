from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

# Create your views here.
def getconds(request):
	print "request mything", request.body
	objs = request.body
	return HttpResponse("heybi" + str(type(objs)))