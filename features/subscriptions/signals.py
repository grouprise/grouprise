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

import django.db.models.signals
from django.dispatch import receiver

from features.associations import models as associations
from features.content import models as content
from . import notifications


@receiver(django.db.models.signals.post_save, sender=associations.Association)
def send_content_notification(sender, instance, created, **kwargs):
    if created and instance.container_type == content.Content.content_type and instance.public:
        notifications.ContentPublicallyAssociated(instance=instance).send()
