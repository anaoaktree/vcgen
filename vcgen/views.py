from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

# Create your views here.
def getconds(request):
	print "request mything", request.body
	var objs= request.body
	return HttpResponse("heybi" + type(objs))