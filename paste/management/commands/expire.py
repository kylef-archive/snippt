from django.core.management.base import BaseCommand
from paste.models import Snippet

class Command(BaseCommand):
    def handle(self, *args, **options):
        snippets = Snippet.objects.expired()
        print 'Deleting %s snippets' % snippets.count()
        snippets.delete()

