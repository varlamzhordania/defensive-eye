from django.db import models
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class BaseModel(models.Model):
    is_active = models.BooleanField(verbose_name=_('Active'), default=True)
    created_at = models.DateTimeField(verbose_name=_('Created at'), auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(verbose_name=_('Updated at'), auto_now=True, blank=True, null=True)

    class Meta:
        abstract = True


@deconstructible
class UploadPath:
    def __init__(self, folder, sub_path):
        self.folder = folder
        self.sub_path = sub_path

    def __call__(self, instance, filename):
        timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
        extension = filename.split(".")[-1]
        return f"{self.folder}/{self.sub_path}/{timestamp}.{extension}"
