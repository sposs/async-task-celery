# coding: utf8
"""
Xample Sarl

author: stephane
date: 27.01.16
"""

from django.conf.urls import url

urlpatterns = [
    url(r'^register_task', view="asynctaskcelery.views.register_task", name="register_task")
]
