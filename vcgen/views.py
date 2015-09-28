from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
import json, elsa
# Create your views here.

def getconds(request):
	result = elsa.start(request.body)
	print "result type", type(result)
	return HttpResponse(result)