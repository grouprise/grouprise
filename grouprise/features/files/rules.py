from rules import predicate, add_perm

from grouprise.features.content.rules import can_view_version
from grouprise.features.contributions import rules as contribution_rules
from grouprise.features.files.models import File


@predicate
def can_download(user, file: File):
    # A file should be either linked to a contribution or to a version.
    if file.contribution.first() is not None:
        return contribution_rules.can_access(user, file.contribution.first())
    elif file.version is not None:
        return can_view_version(user, file.version)
    return False


add_perm("files.download", can_download)
