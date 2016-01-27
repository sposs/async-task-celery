from __future__ import unicode_literals

from django.db import models


TASKS_CHOICES = ["immediate", "scheduled"]


# Create your models here.
class Task(models.Model):
    name = models.CharField()
    author = models.CharField()
    type = models.CharField(choices=TASKS_CHOICES)
