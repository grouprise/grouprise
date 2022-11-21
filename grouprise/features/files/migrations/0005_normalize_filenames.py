import os
import shutil
import sys

from django.db import migrations
from django.urls import reverse

from grouprise.core.utils import add_redirect


class NormalizeFilenameException(Exception):
    """the filename normalization failed somehow"""


def _check_storage_filename_conformity(obj, model):
    storage_path = obj.file.storage.location
    full_path = obj.file.path
    relative_path = full_path.removeprefix(storage_path).removeprefix(os.path.sep)
    # fail if the file is located in a subdirectory
    if os.path.sep in relative_path:
        return False
    # fail if more than one file with this filename exists (we should split them)
    if model.objects.filter(file=obj.file.name).count() > 1:
        return False
    # fail if our storage class uses an incompatible filename schema
    try:
        is_valid_filename = obj.file.storage.is_valid_filename
    except AttributeError:
        # the "is_valid_filename" method is only implemented by "our" storage class
        pass
    else:
        if not is_valid_filename(relative_path):
            return False
    # no test failed - the filename is acceptable
    return True


def _normalize_storage_filename(obj, model, original_base_path, reverse_url_key):
    try:
        preferred_base_filename = obj.filename
    except AttributeError:
        # the "Image" model does not have a "filename" attribute
        preferred_base_filename = None
    if preferred_base_filename is None:
        preferred_base_filename = obj.file.name
    # try to guess the filename extension (if it is missing)
    if os.path.extsep not in preferred_base_filename:
        if os.path.extsep in obj.file.name:
            preferred_base_filename += os.path.splitext(obj.file.name)[1]
    new_filename = obj.file.storage.get_available_name(preferred_base_filename)
    model_count = model.objects.filter(file=obj.file.name).count()
    if model_count > 1:
        # this is not the last object referring to this file - we need to create a copy
        _copy_file_in_storage(obj, new_filename)
    else:
        _rename_file_in_storage(obj, new_filename, original_base_path, reverse_url_key)


def _get_source_and_target(obj, new_filename):
    """return the full filenames of source and target as a tuple"""
    media_directory = obj.file.storage.base_location
    source_filename = os.path.join(media_directory, obj.file.name)
    target_filename = os.path.join(media_directory, new_filename)
    if not os.path.exists(source_filename):
        raise NormalizeFilenameException(f"File does not exist: {source_filename}")
    return source_filename, target_filename


def _copy_file_in_storage(obj, new_filename):
    """copy the obj content to a new file and change the storage location"""
    source_filename, target_filename = _get_source_and_target(obj, new_filename)
    try:
        shutil.copy(source_filename, target_filename)
    except OSError as exc:
        raise NormalizeFilenameException(
            f"Failed to copy file to new location ({source_filename} -> {target_filename}):"
            f" {exc}"
        )
    try:
        obj.file.name = new_filename
        obj.save()
    except Exception as exc:
        try:
            os.remove(target_filename)
        except OSError:
            pass
        raise NormalizeFilenameException(
            f"Failed to change physical location of file object ({obj}): {exc}"
        )
    if not os.path.exists(source_filename):
        raise NotImplementedError("FILE MISSING AFTER COPY", source_filename)


def _rename_file_in_storage(obj, new_filename, original_base_path, reverse_url_key):
    """rename the file, change the storage location and add a redirect"""
    source_filename, target_filename = _get_source_and_target(obj, new_filename)
    try:
        shutil.move(source_filename, target_filename)
    except OSError as exc:
        raise NormalizeFilenameException(
            f"Failed to move file to new location ({source_filename} -> {target_filename}):"
            f" {exc}"
        )
    try:
        obj.file.name = new_filename
        obj.save()
    except Exception as exc:
        raise NormalizeFilenameException(
            f"Failed to change physical location of file object ({obj}): {exc}"
        )
        try:
            shutil.move(target_filename, source_filename)
        except OSError as exc:
            raise NormalizeFilenameException(
                f"Failed to restore file to its original location after failed update:"
                f" {exc}."
                f" You should run the following command manually:"
                f" mv '{target_filename}' '{source_filename}'"
            )
    if original_base_path:
        # the redirect is optional - we do not need to revert anything, if it fails
        source_path = f"{original_base_path}/{source_filename}"
        destination_path = reverse(reverse_url_key, args=[obj.pk])
        try:
            add_redirect(source_path, destination_path)
        except Exception as exc:
            raise NormalizeFilenameException(
                f"Failed to add redirect from '{source_path}' to '{destination_path}':"
                f" {exc}"
            )


def flatten_file_paths(apps, schema_editor):
    for label, model, reverse_url_key in (
        ("file", apps.get_model("files", "File"), "download-file"),
        ("image", apps.get_model("images", "Image"), "download-image"),
    ):
        for obj in model.objects.all():
            if not _check_storage_filename_conformity(obj, model):
                try:
                    _normalize_storage_filename(
                        obj, model, "/stadt/media", reverse_url_key
                    )
                except NormalizeFilenameException as exc:
                    print(
                        f"Failed to normalize filename ({label}): {exc}",
                        file=sys.stderr,
                    )


class Migration(migrations.Migration):

    dependencies = [
        ("files", "0004_auto_20211213_1229"),
        ("redirects", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(flatten_file_paths),
    ]

    # We are moving and renaming real files while going through all "file" objects in the database.
    # Thus, we may not allow a rollback in case of errors.
    atomic = False
