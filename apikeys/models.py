import hashlib

from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User


class Key(models.Model):
    key = models.CharField(unique=True, max_length=32, blank=True)
    user = models.ForeignKey(User)
    comment = models.CharField(max_length=255, blank=True, null=True)

    def __unicode__(self):
        return self.key

    def save(self, *args, **kwargs):
        if not self.pk and not self.key:
            self.generate_key()

        super(Key, self).save(*args, **kwargs)

    def generate_key(self, length=12, allowed_chars='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
        import random

        try:
            random = random.SystemRandom()
        except NotImplementedError:
            pass

        self.key = hashlib.sha1(''.join([random.choice(allowed_chars) for i in range(length)])).hexdigest()[32:]


admin.site.register(Key)
