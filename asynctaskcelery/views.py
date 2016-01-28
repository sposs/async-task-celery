from celery.canvas import chord
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import get_urlconf, reverse
from django.http.response import HttpResponseForbidden, HttpResponseServerError, Http404, HttpResponse, \
    HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django import forms
import logging
from django.template.context import RequestContext
from django.views.decorators.http import require_http_methods
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from asynctaskcelery.models import Task
from asynctaskcelery.tasks import generic_run


class TaskForm(forms.ModelForm):
    """
    Generate a form automatically for the Task model
    """
    class Meta:
        model = Task
        fields = ["name", "author", "type"]


class RegisterTaskView(View):
    form_class = TaskForm

    def get(self, request, *args, **kwargs):
        return render_to_response("task_form.html", {"task": self.form_class()},
                                  context_instance=RequestContext(request))

    def post(self, request, *args, **kwargs):
        t = TaskForm(request.POST)
        if t.is_valid():
            t.save()
            return HttpResponseRedirect(reverse("task_saved"))
        else:
            return render_to_response("task_form.html", {"task": t},
                                      context_instance=RequestContext(request))


class ViewTasksView(ListView):
    model = Task


class ChangeTaskView(DetailView):
    slug_field = "name"
    model = Task


@login_required()
@require_http_methods(["POST"])
def execute_now(request):
    """
    Execute the task now
    :param request:
    :return:
    """
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


@login_required()
@require_http_methods(["GET"])
def execute_scheduled(request):
    """
    Use APScheduler to execute later
    :param request:
    :return:
    """
    return


@require_http_methods(["GET"])
def task_saved(request):
    """
    only print a friendly message
    :param request:
    :return:
    """
    return HttpResponse("Task created")
