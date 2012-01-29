import datetime
import random

from django.db import models
from django.contrib.auth.models import User

class SnippetManager(models.Manager):
    def not_expired(self):
        return self.exclude(expires__lte=datetime.datetime.now())

    def recent(self, limit=5):
        return self.not_expired().order_by('-published')[:limit]

class Snippet(models.Model):
    title = models.CharField(max_length=255, blank=True)
    slug = models.CharField(max_length=32, blank=True)
    content = models.TextField()

    author = models.ForeignKey(User, null=True, blank=True)
    private = models.BooleanField(default=True)
    published = models.DateTimeField(blank=True)
    expires = models.DateTimeField(blank=True, null=True)

    objects = SnippetManager()

    def __unicode__(self):
        return self.slug

    def get_absolute_url(self):
        return '/' + self.slug

    def save(self, *args, **kwargs):
        if not self.pk:
            if not self.slug:
                self.generate_slug()

            self.published = datetime.datetime.now()

            if not self.author:
                # Anonymous pastes expire in 2 weeks
                self.expires = self.published + datetime.timedelta(weeks=2)
        super(Snippet, self).save(*args, **kwargs)

    def generate_slug(self, length=6):
        t = 'abcdefghijkmnopqrstuvwwxyzABCDEFGHIJKLOMNOPQRSTUVWXYZ1234567890'
        self.slug = ''.join([random.choice(t) for i in range(length)])

