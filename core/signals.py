"""
This file is part of stadtgestalten.

stadtgestalten is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

stadtgestalten is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero Public License for more details.

You should have received a copy of the GNU Affero Public License
along with stadtgestalten.  If not, see <http://www.gnu.org/licenses/>.
"""

from django import dispatch
from django.db.models import signals
from django.utils import module_loading


def always(instance):
    return True


def connect_action(signal, action, predicate=always, senders=[]):
    def receiver(sender, **kwargs):
        if predicate(kwargs['instance']):
            action(kwargs['instance'])
    for sender in senders:
        signal.connect(receiver, sender=sender, weak=False)


def connect_notification(
        signal, notification_class, instance=None, predicate=always,
        senders=[]):
    def receiver(sender, **kwargs):
        if predicate(kwargs['instance']):
            notification_class(**{instance: kwargs['instance']}).send()
    for sender in senders:
        signal.connect(receiver, sender=sender, weak=False)


def include(module_name):
    module_loading.import_string(module_name + '.connections')


model_changed = dispatch.Signal()

model_created = dispatch.Signal()

model_deleted = dispatch.Signal()


def model_post_delete(sender, **kwargs):
    model_deleted.send(sender, instance=kwargs['instance'])


signals.post_delete.connect(model_post_delete)


def model_post_save(sender, **kwargs):
    if kwargs['created']:
        model_created.send(sender, instance=kwargs['instance'])
    else:
        model_changed.send(sender, instance=kwargs['instance'])


signals.post_save.connect(model_post_save)
