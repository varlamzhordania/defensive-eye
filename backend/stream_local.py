import cv2
import asyncio
import websockets
import environ

env = environ.Env()

# WebSocket URL
CODE = "abcdefg"
STREAM_HOST = env("STREAM_DOMAIN",default="127.0.0.1:8001")
STREAM_PROTOCOL = "ws"
WEBSOCKET_URL = f"{STREAM_PROTOCOL}://{STREAM_HOST}/ws/camera_stream/?code={CODE}"

async def stream_camera():
    async with websockets.connect(WEBSOCKET_URL) as websocket:
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("Error: Could not open the camera.")
            return

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                # Resize the frame
                frame = cv2.resize(frame, (640, 480))

                # Encode the frame as JPEG
                _, buffer = cv2.imencode('.jpg', frame)

                # Send the encoded frame as binary data
                await websocket.send(buffer.tobytes())

                # Display the frame locally for testing
                cv2.imshow('Live Stream (Press Q to Quit)', frame)

                # Exit on 'q' key press
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        finally:
            cap.release()
            cv2.destroyAllWindows()

# Run the streaming function
asyncio.run(stream_camera())
