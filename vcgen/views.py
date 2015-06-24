from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

# Create your views here.
@POST
def getconds(request,jsontxt):
	return render(request, 'textinterface/index.html', {})
