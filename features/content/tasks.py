from huey.contrib.djhuey import db_task

from features.content.notifications import ContentCreated


@db_task()
def send_content_notifications(instance):
    ContentCreated.send_all(instance)
