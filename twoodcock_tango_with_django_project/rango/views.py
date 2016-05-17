from django.http import HttpResponse


# My first view - called "index"
# It takes a HttpResponse "request"
# and returns another HttpResponse
def index(request):
    return HttpResponse("Rango says hey there partner!")
