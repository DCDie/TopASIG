from django.conf import settings
from django.core.files.storage import default_storage
from django.db import models
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from django_minio_backend import MinioBackend, iso_date_prefix

from apps.ensurance.constants import FileTypes


class File(models.Model):
    external_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    file = models.FileField(
        storage=MinioBackend(bucket_name=settings.MINIO_MEDIA_FILES_BUCKET), upload_to=iso_date_prefix
    )
    type = models.CharField(max_length=50, choices=FileTypes.choices, default=FileTypes.OTHER)

    def __str__(self):
        return self.name or self.external_id


@receiver(post_delete, sender=File)
def file_delete(sender, instance, **kwargs):
    if default_storage.exists(instance.file.name):
        default_storage.delete(instance.file.name)


@receiver(pre_save, sender=File)
def update_file_name(sender, instance, **kwargs):
    if instance._state.adding:
        instance.name = instance.file.name.split("/")[-1]
