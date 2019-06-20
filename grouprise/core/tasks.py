from django.conf import settings
from django.utils.module_loading import import_string
from huey.contrib.djhuey import db_task

from grouprise.core.models import RepeatableTask


@db_task()
def auto_task(model):
    task = RepeatableTask.objects.create(
            content_type=model.content_type, object_id=model.id)

    model_class_label = model._meta.label
    task_method_name = settings.GROUPRISE_REPEATABLE_TASKS[model_class_label]
    task_method = import_string(task_method_name)
    task_method(model)

    task.delete()
