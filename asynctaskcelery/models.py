from __future__ import unicode_literals

from celery.canvas import chord
from django.db import models
from django.utils.translation import ugettext_lazy as _
from asynctaskcelery.tasks import generic_run
from annoying.fields import JSONField
import logging




class Data(models.Model):
    # value = JSONField(blank=True, null=True)
    value = models.CharField(max_length=255, null=True)

    run_instance = models.ForeignKey("RunInstance", on_delete=models.CASCADE, related_name="data", null=True)
    task = models.ForeignKey("Task", related_name="data", null=True)


class Task(models.Model):
    name = models.CharField(max_length=50, primary_key=True)
    author = models.CharField(max_length=20, blank=True)
    parents = models.ManyToManyField('Task', verbose_name="List of parents, can be one item", blank=True)

    def get_task(self, run_instance):
        """
        Recursive and magic function that creates the full tasks
        :param run_instance: A run instance object
        :return: a celery task object
        """
        parents = self.parents.all()
        if parents:
            l_tasks = []
            for parent in parents:
                l_tasks.append(parent.get_task(run_instance))
            return chord(l_tasks, generic_run.s(task_name=self.name))
        else:
            input_d = Data.objects.filter(task=self, run_instance=run_instance).all()
            return generic_run.si([d.value for d in input_d], task_name=self.name)

    def __unicode__(self):
        return "%s" % self.name


class RunInstance(models.Model):
    PAUSED = "paused"
    RUNNING = "running"
    SCHEDULED = "scheduled"
    DONE = "done"
    FAILED = "failed"
    RUN_INSTANCE_STATES = ((PAUSED, _("Paused")),
                           (SCHEDULED, _("Scheduled")),
                           (RUNNING, _("Running")),
                           (DONE, _("Done")),
                           (FAILED, _("Failed")),
                           )
    IMMEDIATE = "immediate"
    TASKS_CHOICES = ((IMMEDIATE, _("Immediate")),
                     (SCHEDULED, _("Scheduled"))
                     )
    tasks = models.ManyToManyField(Task, verbose_name="List of tasks")
    initiator = models.CharField(max_length=50, blank=True, null=True)
    create_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(blank=True, null=True)
    start_at = models.DateTimeField(blank=True, null=True)
    finished_at = models.DateTimeField(blank=True, null=True)
    last_update = models.DateTimeField(auto_now=True)
    main_task = models.ForeignKey(Task, related_name="run_instances")
    run_type = models.CharField(max_length=20, choices=TASKS_CHOICES, default=IMMEDIATE)
    max_wait_time = models.FloatField(verbose_name="Maximum waiting time for completion", default=100.,
                                      help_text="In seconds")
    state = models.CharField(max_length=20, choices=RUN_INSTANCE_STATES, default=PAUSED)
    state_message = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return "%s run on %s" % (self.task.name, self.due_date)

    def get_task(self):
        """
        Get the task construct for the current run instance
        :return: a celery-compatible task
        """
        return self.main_task.get_task(self)
