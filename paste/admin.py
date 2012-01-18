from django.contrib import admin
from paste.models import Paste

class PasteAdmin(admin.ModelAdmin):
    pass

admin.site.register(Paste, PasteAdmin)
