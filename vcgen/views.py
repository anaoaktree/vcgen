from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import json

# Create your views here.
def getconds(request):
	return HttpResponse("heybi " + str(request.body))