import difflib
import datetime
import textwrap
import re

from pygments import highlight
from pygments.lexers import *
from pygments.lexers import get_all_lexers
from pygments.formatters import HtmlFormatter

try:
    from markdown import Markdown
except ImportError:
    Markdown = False

try:
    from docutils.core import publish_parts
except ImportError:
    publish_parts = False

from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django.utils.html import escape
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import TemplateView, DetailView, CreateView, DeleteView
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.contrib.auth import logout

from paste.models import Snippet
from paste.forms import SnippetForm

from apikeys.models import Key

PASTE_KEY = 'paste'
VIM_MODELINE_RE = re.compile(r'(vi|vim)\: (set )?(.+)\:?')

def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')

def get_lexer(request, exclude=None):
    keys = request.GET.keys()

    if exclude:
        for x in exclude:
            if x in keys:
                keys.remove(x)

    if len(keys):
        return keys[0].lower()

    return None


class UserView(DetailView):
    model = User
    slug_field = 'username'
    template_name = 'paste/user_detail.html'

class SyntaxView(TemplateView):
    template_name = 'paste/syntax_list.html'

    def get_context_data(self, **kwargs):
        context = super(SyntaxView, self).get_context_data(**kwargs)
        context['syntax_list'] = sorted(
            [(i[1][0], i[0]) for i in get_all_lexers()] +
            [('rrst', 'Restructured Text (Rendered)'),
             ('md', 'Markdown (Rendered)')])
        return context

class DeleteSnippetView(DeleteView):
    success_url = '/'
    model = Snippet

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.author == request.user:
            self.object.delete()
            return HttpResponseRedirect(self.get_success_url())
        return HttpResponseRedirect(self.object.get_absolute_url() + '/')

class AddSnippetView(CreateView):
    template_name = 'paste/paste.html'
    form_class = SnippetForm

    def get_form(self, form_class):
        form = form_class(**self.get_form_kwargs())

        if 'fork' in self.request.GET:
            slug = self.request.GET['fork']

            queryset = Snippet.objects.filter(slug=slug).exclude(expires__lte=datetime.datetime.now())

            try:
                object = queryset.get()
            except ObjectDoesNotExist:
                raise Http404('No snippet named {}'.format(slug))

            form.fields['content'].initial = object.content
            form.fields['parent'].initial = object

        lexer_name = get_lexer(self.request, ['fork'])
        if lexer_name:
            try:
                lexer = get_lexer_by_name(lexer_name)
            except:
                form.fields['lexer'].initial = lexer_name
                return form

            try:
                lexer_name = lexer.aliases[0]
            except:
                pass

            form.fields['lexer'].initial = lexer_name

            for l in form.fields['lexer'].choices:
                if lexer_name == l[0]:
                    return form

            form.fields['lexer'].choices.insert(0, (lexer_name, lexer.name))

        return form

    def form_valid(self, form):
        obj = form.save(commit=False)
        if self.request.user.is_authenticated():
            obj.author = self.request.user
        obj.save()

        if form.cleaned_data.get('lexer') == 'g':
            return HttpResponseRedirect(obj.get_absolute_url() + '/')
        return HttpResponseRedirect(obj.get_absolute_url() + '?' + form.cleaned_data.get('lexer'))

class IndexView(AddSnippetView):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(IndexView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        author = None

        if 'api' in request.GET:
            try:
                author = Key.objects.get(key=request.GET['api']).user
            except ObjectDoesNotExist:
                pass

        if PASTE_KEY not in request.POST:
            return HttpResponse('')

        snippet = Snippet(content=request.POST[PASTE_KEY], author=author)
        snippet.save()

        if 'HTTP_HOST' in request.META:
            return HttpResponse('http://%s/%s\n' % (request.META['HTTP_HOST'], snippet.slug))

        site = Site.objects.get_current()

        return HttpResponse('http://%s/%s\n' % (site.domain, snippet.slug))


class SnippetView(DetailView):
    model = Snippet

    def get_context_data(self, **kwargs):
        context = super(SnippetView, self).get_context_data(**kwargs)
        context['content'] = self.content
        context['processed_content'] = self.get_processed_content()
        context['lexer'] = self.lexer_name
        context['fluid'] = True

        return context

    def get_object(self, slug_field='slug'):
        if slug_field not in self.kwargs:
            slug_field = 'a'
        queryset = self.get_queryset()
        queryset = queryset.filter(slug=self.kwargs.get(slug_field)).exclude(expires__lte=datetime.datetime.now())

        try:
            object = queryset.get()
        except ObjectDoesNotExist:
            raise Http404('No snippet named {}'.format(self.kwargs[slug_field]))

        return object

    def get_content(self):
        content = self.get_object().content

        if 'wrap' in self.request.GET:
            content = '\n'.join(['\n'.join(textwrap.wrap(line, 80)) for line in content.splitlines()])

        return content

    def get_processed_content(self):
        self.lexer_name = get_lexer(self.request, ['wrap'])

        m = VIM_MODELINE_RE.search(self.content)
        if m:
            modes = m.group(3)
            if ':' in modes:
                modes = modes.split(':')
            else:
                modes = modes.split(' ')

            pairs = {}
            for mode in modes:
                if '=' in mode:
                    k,v = mode.split('=')
                    pairs[k] = v
                else:
                    pairs[mode] = None

            if 'syntax' in pairs and (not self.lexer_name or
                    self.lexer_name in ('g', 'guess')):
                self.lexer_name = pairs['syntax']

        if Markdown and self.lexer_name in ('markdown', 'md'):
            return mark_safe(Markdown(safe_mode=True, extensions=('codehilite',)).convert(self.content))

        if publish_parts and self.lexer_name == 'rrst':
            parts = publish_parts(source=self.content, writer_name="html4css1")
            return mark_safe(parts["fragment"])

        try:
            if self.lexer_name in ('g', 'guess'):
                lexer = guess_lexer(self.content)
                self.lexer_name = lexer.name
            elif self.lexer_name:
                lexer = get_lexer_by_name(self.lexer_name)
            else:
                raise Exception
        except:
            try:
                lexer = guess_lexer(self.content)
            except:
                lexer = PythonLexer()

        try:
            return mark_safe(highlight(self.content,  lexer,
                HtmlFormatter(linenos='table', cssclass='table',
                    anchorlinenos=True, lineanchors='l')))
        except:
            return escape(self.content)

    def get(self, request, *args, **kwargs):
        self.content = self.get_content()

        if len(self.request.GET) or request.path.endswith('/'):
            return super(SnippetView, self).get(request, *args, **kwargs)

        return HttpResponse(self.content, content_type='text/plain; charset=UTF-8')


class DiffMixin(object):
    def get_context_data(self, **kwargs):
        context = super(DiffMixin, self).get_context_data(**kwargs)
        context['a'] = self.a
        context['b'] = self.b
        return context

    def get_content(self):
        self.a = self.get_object('a')
        self.b = self.get_object('b')

        if self.a.content == self.b.content:
            return '{} and {} are the same.'.format(self.a, self.b)

        d = difflib.unified_diff(self.a.content.splitlines(), self.b.content.splitlines(), self.a.slug, self.b.slug, lineterm='')

        return '\n'.join(d)


class DiffView(DiffMixin, SnippetView):
    pass

