from celery.canvas import chord
from django.core.urlresolvers import get_urlconf, reverse
from django.http.response import HttpResponseForbidden, HttpResponseServerError, Http404, HttpResponse, \
    HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django import forms
import logging
from django.template.context import RequestContext
from asynctaskcelery.models import Task
from asynctaskcelery.tasks import generic_run


class TaskForm(forms.ModelForm):
    """
    Generate a form automatically for the Task model
    """
    class Meta:
        model = Task
        fields = ["name", "author", "type"]


def register_task(request):
    """
    Register a task
    :param request:
    :return:
    """
    if request.method == "POST":
        t = TaskForm(request.POST)
        if t.is_valid():
            t.save()
            return HttpResponseRedirect(reverse("task_saved"))

    else:
        t = TaskForm()
    return render_to_response("task_form.html", {"task": t}, context_instance=RequestContext(request))


def execute_now(request):
    """
    Execute the task now
    :param request:
    :return:
    """
    if request.method == "POST":
        try:
            task = get_object_or_404(Task, name=request.POST.get("task_name"))
            task_run = task.get_task()
            res = task_run.apply_async()  # this is where the magic happens
            return res.get()
        except Http404:
            raise
        except Exception as error:
            logging.exception(error)
            return HttpResponseServerError()
    else:
        logging.error("Not allowed to GET this")
        return HttpResponseForbidden()


def execute_scheduled(request):
    """
    Use APScheduler to execute later
    :param request:
    :return:
    """
    return


def task_saved(request):
    """
    only print a friendly message
    :param request:
    :return:
    """
    return HttpResponse("Task created")
