from rest_framework import serializers
from accounts.models import Subscription
from main.models import Plans


class ActiveStreamsSerializer(serializers.Serializer):
    active_feeds = serializers.IntegerField()


class PlansSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plans
        fields = '__all__'

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = '__all__'