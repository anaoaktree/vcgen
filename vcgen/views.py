from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
import json, elsa
# Create your views here.

@ensure_csrf_cookie
def getconds(request):
	result = elsa.start(request.body)
	return HttpResponse(result)