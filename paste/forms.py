import datetime
from django import forms
from paste.models import Snippet

EXPIRE_CHOICES = (
    (600,        'In 10 minutes'),
    (3600,       'In one hour'),
    (3600*24,    'In one day'),
    (3600*24*7,  'In one week'),
    (3600*24*14, 'In two weeks'),
    (3600*24*30, 'In one month'),
)

EXPIRE_DEFAULT = 3600*24*14

LEXER_LIST = (
    ('g', 'Guess'),
    ('bash', 'Bash'),
    ('c', 'C'),
    ('cpp', 'C++'),
    ('css', 'CSS'),
    ('diff', 'Diff'),
    ('django', 'Django/Jinja'),
    ('html', 'HTML'),
    ('js', 'JavaScript'),
    ('md', 'Markdown (Rendered)'),
    ('objective-c', 'Objective-C'),
    ('php', 'PHP'),
    ('python', 'Python'),
    ('python3', 'Python 3'),
    ('rb', 'Ruby'),
    ('rst', 'Restructured Text'),
    ('rrst', 'Restructured Text (Rendered)'),
    ('sql', 'SQL'),
    ('text', 'Text only'),
    ('vim', 'VimL'),
)
LEXER_DEFAULT = 'g'

class SnippetForm(forms.ModelForm):
    expire_options = forms.ChoiceField(
        choices=EXPIRE_CHOICES,
        initial=EXPIRE_DEFAULT,
        label='Expires',
    )

    lexer = forms.ChoiceField(
        choices=LEXER_LIST,
        initial=LEXER_DEFAULT,
        label='Syntax',
    )

    content = forms.CharField(widget=forms.Textarea(attrs={
        'cols': 40,
        'rows': 15,
        'class': 'input-xxlarge'
    }))

    class Meta:
        model = Snippet
        fields = ('title', 'content', 'private')

    def save(self, *args, **kwargs):
        # Add expire datestamp
        self.instance.expires = datetime.datetime.now() + \
            datetime.timedelta(seconds=int(self.cleaned_data['expire_options']))

        super(SnippetForm, self).save(*args, **kwargs)

        return self.instance
