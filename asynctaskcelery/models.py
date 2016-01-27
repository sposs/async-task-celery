from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _


TASKS_CHOICES = (("immediate", _("Immediate")),
                 ("scheduled", _("Scheduled")))


# Create your models here.
class Task(models.Model):
    name = models.CharField(max_length=50)
    author = models.CharField(max_length=20)
    type = models.CharField(max_length=20, choices=TASKS_CHOICES)
