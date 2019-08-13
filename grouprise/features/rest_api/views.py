import rest_framework


def get_view_description(view, html=False):
    # FIXME: we call rest_frameworks get_view_description here without html support to disable
    # markdown, as we are using markdown < 3 which is incompatible with rest_framework
    return rest_framework.views.get_view_description(view, html=False)
