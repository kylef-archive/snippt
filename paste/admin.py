from django.contrib import admin
from paste.models import Paste

class PasteAdmin(admin.ModelAdmin):
    list_display = ('slug', 'author')

admin.site.register(Paste, PasteAdmin)
