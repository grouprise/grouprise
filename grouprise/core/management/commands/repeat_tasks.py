from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.module_loading import import_string

from grouprise.core.models import RepeatableTask


def repeat_tasks(task_queryset):
    for task in task_queryset:
        obj = task.task_parameter
        label = obj._meta.label
        method_name = settings.GROUPRISE_REPEATABLE_TASKS[label]
        task_method = import_string(method_name)
        try:
            task_method(obj)
        finally:
            task.delete()


class Command(BaseCommand):
    help = 'Repeat failed tasks'

    def add_arguments(self, parser):
        parser.add_argument('--all', action='store_true')
        parser.add_argument('task_id', nargs='*', type=int)

    def handle(self, *args, **options):
        all_option = options.get('all')
        task_ids = options.get('task_id', [])
        if all_option and task_ids:
            self.stderr.write('Either specify --all or <task_ids>, not both of them.')
            raise SystemExit(1)
        elif all_option:
            repeat_tasks(RepeatableTask.objects.all())
        elif task_ids:
            repeat_tasks(RepeatableTask.objects.filter(id__in=task_ids))
        else:
            # default: list repeatable tasks
            for task in RepeatableTask.objects.all():
                model_name = task.content_type.model
                obj = task.task_parameter
                self.stdout.write('({}) {:%Y-%m-%d %H:%M:%S} {} "{}"'.format(
                    task.id, task.created_time, model_name, obj))
