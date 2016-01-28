from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponseServerError, Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django import forms
import logging
from django.views.decorators.http import require_http_methods
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from asynctaskcelery.models import Task, RunInstance


class TaskForm(forms.ModelForm):
    """
    Generate a form automatically for the Task model
    """
    class Meta:
        model = Task
        fields = ["name", "author", "type", "parents"]


class RegisterTaskView(CreateView):
    form_class = TaskForm
    template_name = "task_form.html"
    success_url = "/tasks/"


class ViewTask(DetailView):
    model = Task
    slug_field = "name"
    template_name = "task_detail.html"

    def get_context_data(self, **kwargs):
        ctx_data = super(ViewTask, self).get_context_data()
        ctx_data["parents"] = []
        parents = self.object.parents.all()
        if parents:
            ctx_data["parents"] = [p.name for p in parents]
        return ctx_data


class ViewTasksView(ListView):
    model = Task


class ChangeTaskView(UpdateView):
    form_class = TaskForm
    model = Task
    template_name = "change_task.html"
    success_url = "/tasks/"
    slug_field = "name"

    def get_context_data(self, **kwargs):
        ctx_data = super(ChangeTaskView, self).get_context_data(**kwargs)
        ctx_data["task_name"] = self.object.name
        return ctx_data


@login_required()
@require_http_methods(["GET", "POST"])
def execute_now(request, id):
    """
    Execute the task now
    :param request:
    :return:
    """
    try:
        run_i = get_object_or_404(RunInstance, pk=id)
        task_run = run_i.get_task()
        res = task_run.apply_async()  # this is where the magic happens
        try:
            result = res.get()
        except Exception as error:
            logging.exception(error)
            return HttpResponseServerError
        return HttpResponse(result)
    except Http404:
        raise
    except Exception as error:
        logging.exception(error)
    return HttpResponseServerError()


@login_required()
@require_http_methods(["GET"])
def execute_scheduled(request, id):
    """
    Use APScheduler to execute later
    :param request:
    :param id: A task ID
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
