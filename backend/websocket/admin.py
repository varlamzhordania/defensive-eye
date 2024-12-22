from django.contrib import admin
from .models import StreamingSession


# Register your models here.

@admin.register(StreamingSession)
class StreamingSessionAdmin(admin.ModelAdmin):
    list_display = ('camera', 'start_time', 'end_time', 'total_streamed_bytes','created_at','updated_at')
    list_filter = ('camera', 'start_time', 'end_time','created_at','updated_at')
