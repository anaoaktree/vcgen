from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

# Create your views here.
def getconds(request):
	print "request mything", request.body
	return HttpResponse("heybi" + request.read().code + "+  body:"+ request.body)