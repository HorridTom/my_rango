from django.contrib import admin
from rango.models import Category, Page


class PageAdmin(admin.ModelAdmin):
    # fields = ['title', 'category', 'url']
    list_display = ('title', 'category', 'url', 'views')


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(Page, PageAdmin)
admin.site.register(Category, CategoryAdmin)
