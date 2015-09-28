from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
import json, elsa
# Create your views here.

def getconds(request):
	try:
		result = elsa.start(request.body)
	except TypeError:
		#result = "Something went wrong. \n Please contact me at one of the contact links above to solve this!"
	return HttpResponse(result)