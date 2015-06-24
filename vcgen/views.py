from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

# Create your views here.
def getconds(request):
	print request.body
	return HttpResponse(str(request.body))