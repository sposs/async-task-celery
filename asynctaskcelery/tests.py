import json
from django.test import TestCase

# Create your tests here.
from asynctaskcelery.models import Task, Data, RunInstance


def create_task(name, author, t_type, parents=None):
    if not parents:
        parents = []
    task = Task(name=name, author=author, type=t_type)
    task.save()
    if parents:
        task.parents = parents
        task.save()
    return task


def create_data(content, task=None, run_instance=None):
    d = Data(value=content)
    d.save()
    d.task = task
    d.run_instance = run_instance
    d.save()
    return d


def create_run_instance(tasks, main_task):
    ri = RunInstance(main_task=main_task)
    ri.save()
    ri.tasks = tasks
    ri.save()
    return ri


def create_full_story():
    t1 = create_task("test", "me", "scheduled")
    t2 = create_task("test2", "me", "scheduled")
    t3 = create_task("tata", "me", "scheduled", parents=[t1, t2])
    tasks = [t1, t2, t3]
    ri = create_run_instance(tasks, t3)
    create_data({"a": "a"}, t1, ri)
    create_data({"a": "b"}, t2, ri)
    return ri


class TestCreate(TestCase):
    def test_make_data(self):
        data = {"a": 12,
                "b": "c"}
        create_data(data)

    def test_create_task(self):
        create_task("test", "me", "scheduled")

    def test_create_tree(self):
        task = create_task("test", "me", "scheduled")
        create_task("tata", "me", "scheduled", parents=[task])

    def test_create_run_instance(self):
        t1 = create_task("test", "me", "scheduled")
        t2 = create_task("tata", "me", "scheduled", parents=[t1])
        tasks = [t1, t2]
        ri = create_run_instance(tasks, t2)
        create_data({"a": "a"}, t1, ri)
        create_data({"a": "b"}, t1, ri)

    def test_fetch_ri(self):
        ri_created = create_full_story()
        ri = RunInstance.objects.get(pk=1)
        self.assertEqual(ri, ri_created)

    def test_get_data_for_ri(self):
        ri_created = create_full_story()
        task = Task.objects.get(name="test")
        data = Data.objects.filter(task=task, run_instance=ri_created).all()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0].task, task)

    def test_get_tasks(self):
        ri_created = create_full_story()
        tasks = ri_created.get_task()
        self.assertEqual(str(tasks), """asynctaskcelery.tasks.generic_run([asynctaskcelery.tasks.generic_run([u"{'a': 'a'}"], task_name=u'test'), asynctaskcelery.tasks.generic_run([u"{'a': 'b'}"], task_name=u'test2')], task_name='tata')""")
