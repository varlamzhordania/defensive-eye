from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel
from main.models import ProductRegistered

class StreamingSession(BaseModel):
    camera = models.ForeignKey(
        ProductRegistered,
        on_delete=models.CASCADE,
        related_name='streaming_sessions',
        verbose_name=_('Camera')
    )
    start_time = models.DateTimeField(default=now, verbose_name=_('Start Time'))
    end_time = models.DateTimeField(null=True, blank=True, verbose_name=_('End Time'))
    total_streamed_bytes = models.BigIntegerField(default=0, verbose_name=_('Total Streamed Bytes'))

    def end_session(self):
        """End the session and record the end time."""
        self.end_time = now()
        self.save(update_fields=['end_time'])

    def update_streamed_bytes(self, bytes_count):
        """Update the total bytes streamed during this session."""
        self.total_streamed_bytes += bytes_count
        self.save(update_fields=['total_streamed_bytes'])

    def __str__(self):
        return f"Session for {self.camera.code} from {self.start_time} to {self.end_time or 'Ongoing'}"
