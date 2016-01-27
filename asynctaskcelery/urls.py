# coding: utf8
"""
Xample Sarl

author: stephane
date: 27.01.16
"""

from django.conf.urls import url
from asynctaskcelery.views import *
urlpatterns = [
    url(r'^register_task$', view=register_task, name="register_task"),
    url(r'^task_saved$', view=task_saved, name="task_saved"),
]
