from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.utils.timezone import now
from asgiref.sync import sync_to_async

from main.models import ProductRegistered

from .models import StreamingSession


class UserStreamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Extract camera code from query string
        self.code = self.scope['query_string'].decode('utf-8').split('=')[1]
        try:
            self.camera = await sync_to_async(ProductRegistered.objects.get)(code=self.code)
        except ProductRegistered.DoesNotExist:
            await self.close(code=4001)
            return

        # Add user to the group for the camera stream
        await self.channel_layer.group_add(f"stream_{self.camera.code}", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        """Handle disconnection."""
        await self.channel_layer.group_discard(f"stream_{self.camera.code}", self.channel_name)

    async def forward_stream(self, event):
        """Receive forwarded stream bytes and send to user."""
        await self.send(bytes_data=event['bytes_data'])


class CameraStreamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Extract and validate the camera code
        self.code = self.scope['query_string'].decode('utf-8').split('=')[1]
        try:
            self.camera = await sync_to_async(ProductRegistered.objects.get)(code=self.code)
        except ProductRegistered.DoesNotExist:
            await self.close(code=4001)
            return

        # Start a new streaming session
        self.session = await sync_to_async(StreamingSession.objects.create)(camera=self.camera)
        await self.accept()

    async def receive(self, bytes_data):
        """Handle incoming byte data and update session stats."""
        streamed_bytes = len(bytes_data)

        # Update session with streamed data
        await sync_to_async(self.session.update_streamed_bytes)(streamed_bytes)

        await self.channel_layer.group_send(
            f"stream_{self.camera.code}",
            {
                "type": "forward_stream",
                "bytes_data": bytes_data,
            },
        )

    async def disconnect(self, close_code):
        """Handle disconnection and end the session."""
        if self.session:
            await sync_to_async(self.session.end_session)()
        await super().disconnect(close_code)

    async def forward_stream(self, event):
        """Forward byte data to a connected client."""
        await self.send(bytes_data=event['bytes_data'])


@login_required
def live_stream_view(request, code):
    product = get_object_or_404(ProductRegistered, code=code, claimed_user=request.user)

    return render(request, 'cameras/live_stream.html', {
        'product': product,
        'stream_url': f"/ws/view_stream/?code={code}",
        'location':settings.STREAM_DOMAIN,
    })
