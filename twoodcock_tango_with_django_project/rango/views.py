from django.http import HttpResponse
from django.shortcuts import render


# My first view - called "index"
# It takes a HttpResponse "request"
# and returns another HttpResponse
def index(request):
    # Construct a dictionary to pass the template engine as its context.
    # Note the key boldmessage is the same as {{ boldmessage }} in the template
    context_dict = {'boldmessage': "Crunchy, creamy, cookie, candy, cupcake!"}
    # Return a rendered response to send to the client.
    # We use the shortcut function to make our lives easier.
    # Note that the first parameter is the template we wish to use.
    return render(request, 'rango/index.html', context=context_dict)


# The "about" view
def about(request):
    # Construct dictionary to pass variable name to the template
    context_dict = {'name': "Tom"}
    # Returna rendered response
    return render(request, 'rango/about.html', context=context_dict)
