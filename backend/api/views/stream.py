from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.request import Request
from django.utils.timezone import now
from datetime import timedelta

from websocket.models import StreamingSession
from api.serializers import ActiveStreamsSerializer


class ActiveStreamsView(APIView):

    def get(self, request: Request, format=None):
        user = request.user

        active_feeds = StreamingSession.objects.filter(camera__claimed_user=user, end_time__isnull=True).count()
        data = {"active_feeds": active_feeds}
        serializer = ActiveStreamsSerializer(data)

        return Response(serializer.data, status=status.HTTP_200_OK)


class StreamSessionTimeAnalyticsView(APIView):

    def get(self, request):
        user = request.user
        today = now()

        # Get streaming sessions for the past 6 months
        six_months_ago = today - timedelta(days=180)
        sessions = StreamingSession.objects.filter(camera__claimed_user=user, start_time__gte=six_months_ago)

        # Calculate total streamed time (convert seconds to hours)
        total_session_streamed_time_seconds = sum(
            (session.end_time - session.start_time).total_seconds()
            for session in sessions if session.end_time
        )

        total_session_streamed_time_hours = round(total_session_streamed_time_seconds / 3600, 2)

        # Calculate average streamed time per session
        session_count = sessions.count()
        average_session_streamed_time_hours = round(
            (total_session_streamed_time_hours / session_count) if session_count else 0, 2)

        # Prepare data for last 6 months
        session_stream_time_data = {}
        for session in sessions:
            month = session.start_time.strftime("%b %Y")  # Example: "Jan 2024"
            duration = (session.end_time - session.start_time).total_seconds() / 3600 if session.end_time else 0
            session_stream_time_data[month] = session_stream_time_data.get(month, 0) + duration

        # Convert to sorted list format
        sorted_months = sorted(session_stream_time_data.keys(), key=lambda x: today.strftime("%Y-%m"))
        watch_time_series = [round(session_stream_time_data[month], 2) for month in sorted_months]

        data = {
            "total_stream_time": total_session_streamed_time_hours,
            "average_stream_time": average_session_streamed_time_hours,
            "months": sorted_months,
            "stream_time_series": watch_time_series,
        }
        return Response(data, status=status.HTTP_200_OK)


class BandwidthUsageAnalyticsView(APIView):

    def get(self, request):
        user = request.user
        today = now()
        this_month_start = today.replace(day=1)

        # Get the user's subscription plan (to check bandwidth limit)
        bandwidth_limit_gb = None
        if user.has_subscription():
            subscription = user.subscription
            bandwidth_limit_gb = subscription.plan.bandwidth_limit_gb if subscription and subscription.plan else None

        # Get all streaming sessions for the last 6 months
        six_months_ago = today - timedelta(days=180)
        sessions = StreamingSession.objects.filter(camera__claimed_user=user, start_time__gte=six_months_ago)

        # Calculate total bandwidth used (Convert bytes to GB)
        total_bandwidth_bytes = sum(session.total_streamed_bytes for session in sessions)
        total_bandwidth_gb = round(total_bandwidth_bytes / (1024 ** 3), 2)  # Convert bytes to GB

        # Calculate average bandwidth per session
        session_count = sessions.count()
        average_bandwidth_gb = round((total_bandwidth_gb / session_count) if session_count else 0, 2)

        # Prepare data for last 6 months
        bandwidth_data = {}
        for session in sessions:
            month = session.start_time.strftime("%b %Y")  # Example: "Jan 2024"
            bandwidth = session.total_streamed_bytes / (1024 ** 3)  # Convert bytes to GB
            bandwidth_data[month] = bandwidth_data.get(month, 0) + bandwidth

        # Convert to sorted list format
        sorted_months = sorted(bandwidth_data.keys(), key=lambda x: today.strftime("%Y-%m"))
        bandwidth_series = [round(bandwidth_data[month], 2) for month in sorted_months]

        # Check if the user is exceeding their bandwidth limit
        alert = None
        if bandwidth_limit_gb and total_bandwidth_gb > bandwidth_limit_gb:
            alert = f"⚠️ You have exceeded your monthly bandwidth limit of {bandwidth_limit_gb} GB!"

        data = {
            "total_bandwidth": total_bandwidth_gb,
            "average_bandwidth": average_bandwidth_gb,
            "months": sorted_months,
            "bandwidth_series": bandwidth_series,
            "bandwidth_limit": bandwidth_limit_gb,
            "alert": alert,
        }
        return Response(data, status=status.HTTP_200_OK)
