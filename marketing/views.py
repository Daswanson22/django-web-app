from django.http import HttpResponse
# Acts as a controller

def index(request):
    return HttpResponse("<h1> Marketing page </h1>")

def pricing(request):
    return HttpResponse("Pricing page")