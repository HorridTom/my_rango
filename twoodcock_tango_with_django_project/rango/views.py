from datetime import datetime
from django.shortcuts import render, redirect
from django.http.response import HttpResponse
# from django.core.urlresolvers import reverse
# from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
# Import the necessary models and forms
from rango.models import Category, Page, User, UserProfile
from rango.forms import UserProfileForm, CategoryForm, PageForm
from rango.bing_search import run_query
# import contextlib


# The index view
def index(request):
    request.session.set_test_cookie()
    # Query the database for a list of ALL categories currently stored.
    # Order the categories by no. likes in descending order.
    # Retrieve the top 5 only - or all if less than 5.
    # Place the list in our context_dict dictionary
    # that will be passed to the template engine.

    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    context_dict = {'categories': category_list,
                    'pages': page_list}

    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits']

    response = render(request, 'rango/index.html', context=context_dict)

    # Return response back to the user, updating any cookies that
    # need to be changed.
    return response


# The "about" view
def about(request):
    if request.session.test_cookie_worked():
        print ("TEST COOKIE WORKED!")
        request.session.delete_test_cookie()

    visitor_cookie_handler(request)
    # Construct dictionary to pass variable name to the template
    context_dict = {'name': "Tom",
                    'visits': request.session['visits']}

    # Return a rendered response
    return render(request, 'rango/about.html', context=context_dict)


# The "Show Category" view
def show_category(request, category_name_slug):
    # Create a context dictionary which we can pass
    # to the template rendering engine
    context_dict = {}

    try:
        # Can we find a category name slug with the given name?
        # If we can't, the .get() method raises a DoesNotExist exception.
        # So the .get() method returns one model instance or raises an
        # exception
        category = Category.objects.get(slug=category_name_slug)

        # Retrieve all of the associated pages.
        # Note that filter() will return a list of page objects or
        # an empty list.
        pages = Page.objects.filter(category=category).order_by('-views')

        # Adds our results list to the template context under name pages.
        context_dict['pages'] = pages
        # We also add the category object from
        # the database to the context dictionary.
        # We'll use this in the template to verify that the category exists.
        context_dict['category'] = category

        result_list = []
        query = ""

        if request.method == 'POST':
            query = request.POST.get('query')
            if query:
                query = query.strip()
                # Run our Bing function to get the results list!
                result_list = run_query(query)
                context_dict['query'] = query
            context_dict['result_list'] = result_list
            context_dict['query'] = query

    except Category.DoesNotExist:
        # We get here if we didn't find the specified category.
        # Don't do anything -
        # the template will display the "no category" message for us.
        context_dict['category'] = None
        context_dict['pages'] = None

    # Go render the response and return it to the Client
    return render(request, 'rango/category.html', context_dict)


@login_required
def add_category(request):

    form = CategoryForm()

    # A HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        # Have we been provided with a valid form?
        if form.is_valid():
            # Save the new category to the database.
            form.save(commit=True)
            # Now that the category is saved
            # We could give a confirmation message
            # But since the most recent category added is on the index page
            # then we can redirect the user back to the index page.
            return index(request)
        else:
            # The supplied form contained errors -
            # just print them to the terminal.
            print(form.errors)

    # Will handle the bad form, new form or
    # no form supplied cases.
    # Render the form with error messages (if any).
    return render(request, 'rango/add_category.html', {'form': form})


@login_required
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None
    form = PageForm()
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                return show_category(request, category_name_slug)
        else:
            print (form.errors)

    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context_dict)


@login_required
def register_profile(request):
    form = UserProfileForm()

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid():
            user_profile = form.save(commit=False)
            user_profile.user = request.user
            user_profile.save()

            return redirect('index')
        else:
            print(form.errors)

    context_dict = {'form': form}

    return render(request, 'rango/profile_registration.html', context_dict)


@login_required
def restricted(request):
    return render(request, 'rango/restricted.html')


# @login_required
# def user_logout(request):
#     # Since we know the user is logged in, we can now just log them out.
#     logout(request)
#     # Take the user back to the homepage.
#     return HttpResponseRedirect(reverse('index'))


# Track url view
def track_url(request):
    page_id = None
    url = '/rango/'
    # Check if the request is a GET request
    if request.method == 'GET':
        # Check that the request dictionary contains 'page_id',
        # and store it in the page_id variable
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']

            # Try retrieving the page object from its page_id,
            # increment the views field,
            # then save the page object back to the database.
            try:
                page = Page.objects.get(id=page_id)
                page.views = page.views + 1
                page.save()
                url = page.url
            # If we cannot do that for some reason, do nothing.
            # NOTE: should specify what sort of exception it's OK to ignore.
            except:
                pass

    return redirect(url)


@login_required
def profile(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return redirect('index')

    userprofile = UserProfile.objects.get_or_create(user=user)[0]
    form = UserProfileForm(
        {'website': userprofile.website, 'picture': userprofile.picture})

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES,
                               instance=userprofile)
        if form.is_valid():
            form.save(commit=True)
            return redirect('profile', user.username)
        else:
            print(form.errors)

    return render(request, 'rango/profile.html',
                  {'userprofile': userprofile, 'selecteduser': user,
                   'form': form})


@login_required
def list_profiles(request):
    userprofile_list = UserProfile.objects.all()

    return render(request, 'rango/list_profiles.html',
                  {'userprofile_list': userprofile_list})


@login_required
def like_category(request):
    cat_id = None
    if request.method == 'GET':
        cat_id = request.GET['category_id']
        likes = 0
    if cat_id:
        cat = Category.objects.get(id=int(cat_id))
        if cat:
            likes = cat.likes + 1
            cat.likes = likes
            cat.save()
    return HttpResponse(likes)


def suggest_category(request):
    # cat_list = []
    starts_with = ''

    if request.method == 'GET':
        starts_with = request.GET['suggestion']

    cat_list = get_category_list(8, starts_with)

    return render(request, 'rango/cats.html', {'cats': cat_list})


@login_required
def auto_add_page(request):
    cat_id = None
    url = None
    title = None
    context_dict = {}
    if request.method == 'GET':
        cat_id = request.GET['category_id']
        url = request.GET['url']
        title = request.GET['title']
        if cat_id:
            category = Category.objects.get(id=int(cat_id))
            p = Page.objects.get_or_create(category=category,
                                           title=title, url=url)
            pages = Page.objects.filter(category=category).order_by('-views')
            # Adds our results list to the template context under name 'pages'.
            context_dict['pages'] = pages
    return render(request, 'rango/page_list.html', context_dict)


# Helper functions
def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val


def visitor_cookie_handler(request):
    # Get the number of visits to the site.
    # If the cookie exists, the value returned is casted to an integer.
    # If the cookie doesn't exist, then the default value of 1 is used.
    visits = int(get_server_side_cookie(request, 'visits', '1'))

    last_visit_cookie = get_server_side_cookie(request,
                                               'last_visit',
                                               str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7],
                                        '%Y-%m-%d %H:%M:%S')

    # If it's been more than a day since the last visit...
    if (datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
        # ...update the last visit cookie now that we have updated the count
        request.session['last_visit'] = str(datetime.now())

    else:
        # set the last visit cookie
        request.session['last_visit'] = last_visit_cookie

    # update/set the visits cookie
    request.session['visits'] = visits


def search(request):
    result_list = []
    context_dict = {'result_list': result_list}

    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            # Run our Bing function to get the results list!
            result_list = run_query(query)
            context_dict = {'result_list': result_list, 'query': query}

    return render(request, 'rango/search.html', context=context_dict)


def get_category_list(max_results=0, starts_with=''):
    cat_list = []
    if starts_with:
        cat_list = Category.objects.filter(name__istartswith=starts_with)

    if max_results > 0:
        if len(cat_list) > max_results:
            cat_list = cat_list[:max_results]

    return cat_list
