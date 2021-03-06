# This module populates the database
# TODO: Write a script to output the data in the database
# so that any changes you make can be saved out into a file that can be
# read in later (exercise at end of section 6.3).


import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tango_with_django_project.set\
                        tings')

import django
django.setup()
from rango.models import Category, Page


def populate():
    # Create lists of dictionaries containing the pages we want to add into
    # each category. Then create a dictionary of these dictionaries.
    python_pages = [
                    {"title": "Official Python Tutorial",
                     "url": "http://docs.python.org/2/tutorial/",
                     "views": 150},
                    {"title": "How to Think like a Computer Scientist",
                     "url": "http://www.greenteapress.com/thinkpython/",
                     "views": 120},
                    {"title": "Learn Python in 10 Minutes",
                     "url": "http://www.korokithakis.net/tutorials/python/",
                     "views": 130}]

    django_pages = [
                    {"title": "Official Django Tutorial",
                     "url": "https://docs.djangoproject.com/en/1.9/intro/tutorial01/",
                     "views": 100},
                    {"title": "Django Rocks",
                     "url": "http://www.djangorocks.com/",
                     "views": 70},
                    {"title": "How to Tango with Django",
                     "url": "http://www.tangowithdjango.com/",
                     "views": 85}]

    other_pages = [
                   {"title": "Bottle",
                    "url": "http://bottlepy.org/docs/dev/",
                    "views": 50},
                   {"title": "Flask",
                    "url": "http://flask.pocoo.org",
                    "views": 30}]

    cats = {"Python": {"pages": python_pages,
                       "views": 128,
                       "likes": 64},
            "Django": {"pages": django_pages,
                       "views": 64,
                       "likes": 32},
            "Other Frameworks": {"pages": other_pages,
                                 "views": 32,
                                 "likes": 16}}
    # Go through the cats dictionary, then adds each category, then adds all
    # the associated pages for that category.

    for cat, cat_data in cats.items():
        c = add_cat(cat)
        c.views = cat_data["views"]
        c.likes = cat_data["likes"]
        c.save()
        for p in cat_data["pages"]:
            add_page(c, p["title"], p["url"], p["views"])

    # Print out what we have added to the User
    for c in Category.objects.all():
        for p in Page.objects.filter(category=c):
            print("- {0} - {1}".format(str(c), str(p)))


def add_page(cat, title, url, views=0):
    p = Page.objects.get_or_create(category=cat, title=title)[0]
    p.url = url
    p.views = views
    p.save()
    return p


def add_cat(name):
    c = Category.objects.get_or_create(name=name)[0]
    return c

# Start execution here!
if __name__ == '__main__':
    print("Starting Rango population script...")
    populate()
