from utils import views as utils_views


class GroupMessages(utils_views.List):
    menu = 'group'
    permission_required = 'content.view_content_list'
    sidebar = []
    template_name = 'content/_thread_list.html'
    title = 'Gespräche'

    def get_queryset(self):
        return self.get_group().get_conversations(self.request.user)

    def get_parent(self):
        return self.get_group()

    def get_related_object(self):
        return self.get_group()
