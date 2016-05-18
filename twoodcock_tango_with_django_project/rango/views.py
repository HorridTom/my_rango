from django.http import HttpResponse


# My first view - called "index"
# It takes a HttpResponse "request"
# and returns another HttpResponse
def index(request):
    return HttpResponse("""Rango says: Hey there partner! <br/>
    <a href='/rango/about'>About</a>""")


# The "about" view
def about(request):
    return HttpResponse("""Rango says here is the about page. <br/>
    <a href='/rango'>Back to index<a/>""")
