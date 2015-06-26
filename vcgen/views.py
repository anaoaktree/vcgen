from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import json, elsa
# Create your views here.
def getconds(request):
	result = elsa.start(request.body)
	return HttpResponse("heybi " + result[0])