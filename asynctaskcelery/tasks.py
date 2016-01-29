# coding: utf8
"""
Xample Sarl

author: sposs
date: 27.01.16
"""
import json
from celery.app import shared_task
from django.shortcuts import get_object_or_404
import logging

# from asynctaskcelery.models import Task


@shared_task(bind=True)
def generic_run(self, input_data_list, task_name):
    """
    A celery task that executes code.
    :param self: a instance of the celery Task
    :param input_data_list: a list of input data JSON
    :param task_id: a task ID to fetch it's run time parameters
    :return: a serializable result (for chaining) JSON
    """
    if not isinstance(input_data_list, list):
        input_data_list = [input_data_list]
    #task = get_object_or_404(Task, name=task_name)
    # input_data = [json.loads(input_d) for input_d in input_data_list]

    retry_task = True  # this should be obtained from the task properties

    try:
        a = 1+1
    except Exception as error:
        if retry_task:
            raise self.retry(error)
        else:
            logging.exception(error)
            raise

    result = {"prev": input_data_list} if input_data_list else {"toto": 23}
    return json.dumps(result)
