from django.http.response import HttpResponseForbidden, HttpResponseServerError, Http404, HttpResponse
from django.shortcuts import render_to_response
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
        t.save()
        return HttpResponse("all OK")
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
            task = generic_run.s(request.POST.get("input_data"), request.POST.get("task_id"))
            return task.get()
        except Http404:
            raise
        except Exception as error:
            logging.exception(error)
            return HttpResponseServerError
    else:
        logging.error("Not allowed to GET this")
        raise HttpResponseForbidden


def execute_scheduled(request):
    """
    Use APScheduler to execute later
    :param request:
    :return:
    """
    return
