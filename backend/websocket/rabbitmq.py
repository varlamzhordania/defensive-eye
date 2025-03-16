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
        """Ensure a singleton instance is used."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_rabbitmq()
        return cls._instance

    def _init_rabbitmq(self):
        """Initialize the RabbitMQ connection once."""
        try:
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=settings.RABBITMQ_HOST,
                    port=settings.RABBITMQ_PORT,
                    credentials=pika.PlainCredentials(
                        settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD
                    ),
                    heartbeat=600,  # Prevent idle disconnections
                )
            )
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue=settings.RABBITMQ_QUEUE_NAME, durable=True)
            print("RabbitMQ Publisher Connected Successfully")
        except pika.exceptions.AMQPConnectionError as e:
            print(f"RabbitMQ Publisher Connection Error: {e}")
            self.connection, self.channel = None, None

    def _ensure_connection(self):
        """Ensure connection and channel are alive."""
        if self.connection is None or self.connection.is_closed:
            print("Reconnecting to RabbitMQ Publisher...")
            self._init_rabbitmq()
        elif self.channel is None or self.channel.is_closed:
            print("Reopening RabbitMQ Publisher channel...")
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue=settings.RABBITMQ_QUEUE_NAME, durable=True)

    def publish_frame(self, camera_code, frame_bytes):
        """Publish a frame to RabbitMQ."""
        self._ensure_connection()  # Ensure connection before publishing

        if self.channel is None:
            print("RabbitMQ Publisher: Cannot publish frame, channel is None!")
            return

        try:
            encoded_frame = base64.b64encode(frame_bytes).decode("utf-8")
            message = json.dumps({"code": camera_code, "bytes_data": encoded_frame})
            self.channel.basic_publish(
                exchange="",
                routing_key=settings.RABBITMQ_QUEUE_NAME,
                body=message,
            )
        except pika.exceptions.AMQPError as e:
            print(f"RabbitMQ Publisher Error: {e}")
            self._init_rabbitmq()  # Only reinitialize if publishing fails


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
                pika.ConnectionParameters(host=self.host, port=self.port, credentials=credentials,heartbeat=600)
            )
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue=self.queue_name, durable=True)
            print("RabbitMQ Worker Connected Successfully")
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
