from django.http import HttpResponse
from django.shortcuts import render
# Acts as a controller

def index(request):
    content = {
        "title": "Home",
        "content": "Welcome to the homepage"
    }
    return render(request, "marketing/index.html", content)
