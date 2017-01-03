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

import core.notifications


class ContentAssociated(core.notifications.Notification):
    generate_reply_tokens = True

    def get_message_ids(self):
        return self.object.container.get_unique_id(), None, []

    def get_recipients(self):
        recipients = set(self.object.container.get_authors())
        if self.object.entity.is_group:
            recipients.update(set(self.object.entity.members.all()))
        else:
            recipients.add(self.object.entity)
        return recipients

    def get_sender(self):
        return self.object.container.versions.last().author

    def get_subject(self):
        group = '[{}] '.format(self.object.entity.slug) if self.object.entity.is_group else ''
        return group + self.object.container.subject

    def get_template_name(self):
        if self.object.container.is_gallery:
            name = 'galleries/associated.txt'
        elif self.object.container.is_event:
            name = 'events/associated.txt'
        else:
            name = 'articles/associated.txt'
        return name
