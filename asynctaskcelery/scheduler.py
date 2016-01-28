# coding: utf8
"""
Xample Sarl

author: stephane
date: 28.01.16
"""
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = None


def init_scheduler():
    global scheduler
    scheduler = BackgroundScheduler()
    scheduler.start()
    return
