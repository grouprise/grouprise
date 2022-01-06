import rules

from grouprise.features.images.models import Image


@rules.predicate
def can_download(user, image: Image):
    # An image might be used
    # - in an image gallery,
    # - as a content image (for preview etc.) or
    # - referenced in any text.
    # It might even be used in more than one of those cases. The image dialog makes all
    # images of the user accessible.
    # Thus, we cannot restrict image permissions.
    return True


@rules.predicate
def is_creator(user, image):
    return user == image.creator.user


rules.add_perm("images.download", can_download)
rules.add_perm("images.view", is_creator)
