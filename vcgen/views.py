from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import json

# Create your views here.
def getconds(request):
	objs = json.loads(request.body)
	return HttpResponse("heybi " + request.body+ " obj: "+str(type(objs)))