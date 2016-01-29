import time
from apscheduler.triggers.cron import CronTrigger
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponseServerError, Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django import forms
import logging

from django.utils.timezone import now
from django.views.decorators.http import require_http_methods
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from asynctaskcelery.models import Task, RunInstance
from asynctaskcelery.scheduler import scheduler


class TaskForm(forms.ModelForm):
    """
    Generate a form automatically for the Task model
    """
    class Meta:
        model = Task
        fields = ["name", "author", "parents"]


class RunInstanceForm(forms.ModelForm):
    class Meta:
        model = RunInstance
        fields = ["tasks", "initiator", "main_task", "run_type", "max_wait_time"]


class RegisterTaskView(CreateView):
    form_class = TaskForm
    template_name = "task_form.html"
    success_url = "/tasks/"


class RegisterRunInstance(CreateView):
    form_class = RunInstanceForm
    template_name = "run_instance.html"
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


def get_and_run(run_instance_id):
    """
    From a run instance ID, get and run the tasks
    :param run_instance_id:
    :return: the task result
    """
    run_i = get_object_or_404(RunInstance, pk=run_instance_id)
    task_run = run_i.get_task()
    run_i.state = RunInstance.RUNNING
    run_i.start_at = now()
    run_i.save()
    res = task_run.apply_async()  # this is where the magic happens
    max_wait_time = run_i.max_wait_time
    while not res.ready() and max_wait_time > 0:
        time.sleep(10)
        max_wait_time -= 10
    try:
        result = res.get()
        run_i.state = RunInstance.DONE
    except Exception as error:
        logging.exception(error)
        run_i.state = RunInstance.FAILED
        run_i.state_message = str(error)
        raise
    finally:
        run_i.finished_at = now()
        run_i.save()
    return result


@login_required()
@require_http_methods(["GET", "POST"])
def execute_now(request, id):
    """
    Execute the task now
    :param request:
    :return:
    """
    try:
        result = get_and_run(id)
    except Http404:
        raise
    except Exception as error:
        logging.exception(error)
        return HttpResponseServerError
    return HttpResponse(result)


@login_required()
@require_http_methods(["GET"])
def execute_scheduled(request, id):
    """
    Use APScheduler to execute later
    :param request:
    :param id: A task ID
    :return:
    """
    run_i = None
    try:
        run_i = get_object_or_404(RunInstance, pk=id)

        trigger = CronTrigger()
        scheduler.add_job(get_and_run, trigger, id, id=id, replace_existing=True)
        run_i.state = RunInstance.SCHEDULED

    except Http404:
        raise
    except Exception as error:
        logging.exception(error)
        return HttpResponseServerError
    finally:
        if run_i:
            run_i.save()
    return HttpResponse("Task Scheduled")


@login_required()
@require_http_methods(["GET"])
def cancel_scheduled(request, id):
    """
    Use APScheduler to execute later
    :param request:
    :param id: A run instance ID
    :return:
    """
    run_i = None
    try:
        run_i = get_object_or_404(RunInstance, pk=id)
        if run_i.state == RunInstance.PAUSED:
            return HttpResponse("Nothing to cancel")
        if run_i.state in [RunInstance.RUNNING, RunInstance.FAILED, RunInstance.DONE]:
            return HttpResponse("Can't cancel a job running or done or failed")
        scheduler.remove_job(id)
        run_i.state = RunInstance.PAUSED
    except Http404:
        raise
    except Exception as error:
        logging.exception(error)
        return HttpResponseServerError
    finally:
        if run_i:
            run_i.save()
    return HttpResponse("OK")


@require_http_methods(["GET"])
def task_saved(request):
    """
    only print a friendly message
    :param request:
    :return:
    """
    return HttpResponse("Task created")
