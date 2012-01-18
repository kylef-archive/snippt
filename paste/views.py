import difflib
import datetime

from pygments import highlight
from pygments.lexers import *
from pygments.formatters import HtmlFormatter

from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django.utils.html import escape
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import TemplateView
from django.views.generic import DetailView
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, Http404
from django.contrib.sites.models import Site

from paste.models import Paste

PASTE_KEY = 'paste'

class IndexView(TemplateView):
    template_name = 'paste/index.html'

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(IndexView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        if PASTE_KEY not in request.POST:
            return HttpResponse('')

        paste = Paste(content=request.POST[PASTE_KEY])
        paste.save()

        site = Site.objects.get_current()

        return HttpResponse('http://%s/%s\n' % (site.domain, paste.slug))

class PasteView(DetailView):
    model = Paste

    def get_context_data(self, **kwargs):
        context = super(PasteView, self).get_context_data(**kwargs)
        context['content'] = self.content
        context['pygmented'] = self.get_pygmented()
        context['lexer'] = self.lexer

        print context['pygmented']
        return context

    def get_object(self, slug_field='slug'):
        if slug_field not in self.kwargs:
            slug_field = 'a'
        queryset = self.get_queryset()
        queryset = queryset.filter(slug=self.kwargs.get(slug_field)).exclude(expires__lte=datetime.datetime.now())

        try:
            object = queryset.get()
        except ObjectDoesNotExist:
            raise Http404('No paste named {}'.format(self.kwargs[slug_field]))

        return object

    def get_content(self):
        return self.get_object().content

    def get_lexer(self):
        lexer_name = self.request.GET.keys()[0]

        try:
            if lexer_name:
                lexer = get_lexer_by_name(lexer_name)
            else:
                raise Exception
        except:
            try:
                lexer = guess_lexer(self.content)
            except:
                lexer = PythonLexer()
        return lexer

    def get_pygmented(self):
        self.lexer = self.get_lexer()

        try:
            return mark_safe(highlight(self.content,  self.lexer, HtmlFormatter()))
        except:
            return escape(self.content)

    def get(self, request, *args, **kwargs):
        self.content = self.get_content()

        if len(self.request.GET):
            return super(PasteView, self).get(request, *args, **kwargs)

        return HttpResponse(self.content, content_type='text/plain; charset=UTF-8')

class DiffMixin(object):
    def get_content(self):
        a = self.get_object('a')
        b = self.get_object('b')

        if a.content == b.content:
            return '{} and {} are the same.'.format(self.kwargs.get('a'), self.kwargs.get('b'))

        d = difflib.unified_diff(a.content.splitlines(), b.content.splitlines(), a.slug, b.slug, lineterm='')

        return '\n'.join(d)

class DiffView(DiffMixin, PasteView):
    pass
