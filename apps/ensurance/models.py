from django.conf import settings
from django.db import models
from django_minio_backend import MinioBackend, iso_date_prefix


class Document(models.Model):
    external_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    file = models.FileField(
        storage=MinioBackend(bucket_name=settings.MINIO_MEDIA_FILES_BUCKET), upload_to=iso_date_prefix
    )

    def __str__(self):
        return self.name
