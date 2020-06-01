from django.shortcuts import render
from django.shortcuts import render

# Create your views here.

def index(request):
    context = {}
    return render(request, "walk/index.html", context)

