from huey.contrib.djhuey import task

from features.content.notifications import ContentCreated


@task()
def send_content_notifications(instance):
    ContentCreated.send_all(instance)
