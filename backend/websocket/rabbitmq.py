import pika
import json
import base64
import threading
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.conf import settings


class RabbitMQPublisher:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_rabbitmq()
        return cls._instance

    def _init_rabbitmq(self):
        try:
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=settings.RABBITMQ_HOST,
                    port=settings.RABBITMQ_PORT,
                    credentials=pika.PlainCredentials(
                        settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD
                    ),
                )
            )
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue=settings.RABBITMQ_QUEUE_NAME, durable=True)
        except pika.exceptions.AMQPConnectionError:
            self.connection, self.channel = None, None

    def _ensure_connection(self):
        if self.channel is None or self.channel.is_closed:
            self._init_rabbitmq()

    def publish_frame(self, camera_code, frame_bytes):
        self._ensure_connection()

        if self.channel is None:
            return

        if isinstance(frame_bytes, str):
            frame_bytes = frame_bytes.encode("utf-8")

        encoded_frame = base64.b64encode(frame_bytes).decode("utf-8")
        message = json.dumps({"code": camera_code, "bytes_data": encoded_frame})

        try:
            self.channel.basic_publish(
                exchange="",
                routing_key=settings.RABBITMQ_QUEUE_NAME,
                body=message,
            )
        except pika.exceptions.AMQPError:
            self._init_rabbitmq()


class RabbitMQWorker:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.queue_name = settings.RABBITMQ_QUEUE_NAME
        self.host = settings.RABBITMQ_HOST
        self.port = settings.RABBITMQ_PORT
        self.user = settings.RABBITMQ_USER
        self.password = settings.RABBITMQ_PASSWORD

    def connect(self):
        try:
            credentials = pika.PlainCredentials(self.user, self.password)
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=self.host, port=self.port, credentials=credentials)
            )
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue=self.queue_name, durable=True)
            return True
        except pika.exceptions.AMQPConnectionError:
            return False

    def process_message(self, ch, method, properties, body):
        channel_layer = get_channel_layer()
        camera_code = properties.headers.get("camera_code") if properties and properties.headers else None

        if not camera_code:
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        async_to_sync(channel_layer.group_send)(
            f"stream_{camera_code}",
            {"type": "forward_stream", "bytes_data": body},
        )

        ch.basic_ack(delivery_tag=method.delivery_tag)

    def start_worker(self):
        if not self.connect():
            threading.Timer(5.0, self.start_worker).start()
            return

        try:
            self.channel.basic_qos(prefetch_count=1)
            self.channel.basic_consume(queue=self.queue_name, on_message_callback=self.process_message)
            self.channel.start_consuming()
        except pika.exceptions.AMQPError:
            self.connection.close()
            threading.Timer(5.0, self.start_worker).start()

    def stop_worker(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()
