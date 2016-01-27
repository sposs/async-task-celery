# coding: utf8
"""
Xample Sarl

author: sposs
date: 27.01.16
"""
import json
from celery.app import shared_task
from django.shortcuts import get_object_or_404

from asynctaskcelery.exceptions import InvalidTask
from asynctaskcelery.models import Task


@shared_task
def generic_run(input_data_list, task_id):
    """
    A celery task that executes code.
    :param input_data_list: a list of input data JSON
    :param task_id: a task ID to fetch it's run time parameters
    :return: a serializable result (for chaining) JSON
    """
    if not isinstance(input_data_list, list):
        input_data_list = [input_data_list]
    task = get_object_or_404(Task, pk=task_id)
    input_data = [json.loads(input_d) for input_d in input_data_list]



    result = {}
    return json.dumps(result)
