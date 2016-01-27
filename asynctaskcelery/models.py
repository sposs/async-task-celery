from __future__ import unicode_literals

from celery.canvas import chord
from django.db import models
from django.utils.translation import ugettext_lazy as _

from asynctaskcelery.tasks import generic_run

TASKS_CHOICES = (("immediate", _("Immediate")),
                 ("scheduled", _("Scheduled")))


class Data(models.Model):
    value = models.TextField()

# Create your models here.
class Task(models.Model):
    name = models.CharField(max_length=50, unique=True)
    author = models.CharField(max_length=20)
    type = models.CharField(max_length=20, choices=TASKS_CHOICES)
    parents = models.ManyToManyField('Task', verbose_name="List of parents, can be one item")

    def get_task(self):
        """
        Recursive and magic function that creates the full tasks
        :return:
        """
        if self.parents:
            l_tasks = []
            for parent in self.parents:
                l_tasks.append(parent.get_task())
            return chord(l_tasks, generic_run.s(task_name=self.task_name))
        else:
            return generic_run.si(self.input_data, task_name=self.task_name)
