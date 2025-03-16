import cv2
import numpy as np
import pika
import time
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from asgiref.sync import sync_to_async

from main.models import ProductRegistered
from core.utils import fancy_message

from .models import StreamingSession
from .rabbitmq import RabbitMQPublisher


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
    last_frame_time = 0
    last_frame = None
    max_fps = 10
    session = None

    async def connect(self):
        self.code = self.scope['query_string'].decode('utf-8').split('=')[1]

        try:
            self.camera = await sync_to_async(
                ProductRegistered.objects.select_related("claimed_user", "claimed_user__subscription").get
            )(code=self.code)
            user = self.camera.claimed_user
            has_subscription = await sync_to_async(user.has_subscription)()

            if not has_subscription:
                print(f"Camera {self.code} owner has no subscription. connection refused.")
                await self.close(code=4001)  # Reject connection if no subscription
                return

            plan = await sync_to_async(lambda: user.subscription.plan)()
            self.max_fps = plan.max_fps
            self.quality = plan.quality


        except ProductRegistered.DoesNotExist:
            await self.close(code=4001)
            return

        self.session = await sync_to_async(StreamingSession.objects.create)(camera=self.camera)
        self.publisher = RabbitMQPublisher()
        await self.accept()

    async def receive(self, bytes_data):
        """Process, compress, and publish frames efficiently."""
        current_time = time.time()
        min_time_between_frames = 1.0 / self.max_fps
        if current_time - self.last_frame_time < min_time_between_frames:  # Throttle to 10 FPS
            return

        self.last_frame_time = current_time

        streamed_bytes = len(bytes_data)
        await sync_to_async(self.session.update_streamed_bytes)(streamed_bytes)

        # Convert bytes to OpenCV image
        np_arr = np.frombuffer(bytes_data, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if frame is not None and self.detect_motion(frame):
            frame = self.optimize_frame(frame)

            success, buffer = cv2.imencode('.webp', frame, [cv2.IMWRITE_WEBP_QUALITY, 50])
            if not success:
                print("⚠️ Error encoding frame to webp")
                return

            self.publisher.channel.basic_publish(
                exchange="",
                routing_key=settings.RABBITMQ_QUEUE_NAME,
                body=buffer.tobytes(),
                properties=pika.BasicProperties(headers={"camera_code": self.camera.code}),
            )

    def optimize_frame(self, frame):
        """Resize and compress frame based on user's subscription quality."""

        resolution_map = {
            "Low": (480, 320),  # 320p
            "Medium": (854, 480),  # 480p
            "HD": (1280, 720),  # 720p
            "Full-HD": (1920, 1080),  # 1080p
            "Ultra-HD": (3840, 2160)  # 4K
        }
        target_resolution = resolution_map.get(self.quality, (854, 480))
        frame = cv2.resize(frame, target_resolution, interpolation=cv2.INTER_AREA)

        return frame

    def detect_motion(self, frame):
        """Detect motion by comparing frames."""
        if self.last_frame is None:
            self.last_frame = frame
            return True

        gray1 = cv2.cvtColor(self.last_frame, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        diff = cv2.absdiff(gray1, gray2)
        non_zero_count = np.count_nonzero(diff)

        if non_zero_count < 5000:
            return False  # Drop frame if no significant motion

        self.last_frame = frame
        return True

    async def disconnect(self, close_code):
        """End streaming session, but DO NOT close RabbitMQ (singleton)."""
        if self.session and self.session is not None:
            await sync_to_async(self.session.end_session)()

        print(f"❌ Camera {self.camera.code} disconnected")

        await super().disconnect(close_code)


@login_required
def live_stream_view(request, code):
    if not request.user.has_subscription():
        fancy_message(request, "You need to have a subscription first to access this page.", "error")
        return redirect("main:cameras_list")
    product = get_object_or_404(ProductRegistered, code=code, claimed_user=request.user)

    return render(request, 'cameras/live_stream.html', {
        'product': product,
        'stream_url': f"/ws/view_stream/?code={code}",
        'location': settings.STREAM_DOMAIN,
    })
