# coding: utf8
"""
Xample Sarl

author: stephane
date: 27.01.16
"""

from django.conf.urls import url
from asynctaskcelery.views import *
urlpatterns = [
    url(r'^register_task$', login_required(RegisterTaskView.as_view()), name="register_task"),
    url(r'^$', view=login_required(ViewTasksView.as_view(template_name="view_tasks.html")),
        name="view_tasks"),
    url(r'^change/(?P<slug>[-\w]+)$', view=login_required(ChangeTaskView.as_view(template_name="change_task.html")),
        name="change_task"),
    url(r'^task_saved$', view=task_saved, name="task_saved"),
]
