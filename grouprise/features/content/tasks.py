from huey.contrib.djhuey import db_task

from grouprise.core.models import RepeatableTask
from grouprise.features.content.notifications import ContentCreated


@db_task()
def send_content_notifications(instance):
    # we save this task's parameter as long as the task runs
    task = RepeatableTask.objects.create(
            content_type=instance.content_type, object_id=instance.id)
    # send notifications (the actual task)
    ContentCreated.send_all(instance, use_async_email_backend=True)
    # remove the saved parameter on success (no exception)
    task.delete()
