from django.contrib import admin
from paste.models import Snippet

class SnippetAdmin(admin.ModelAdmin):
    list_display = ('slug', 'author')

admin.site.register(Snippet, SnippetAdmin)
