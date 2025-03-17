from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.request import Request

from api.serializers import SubscriptionSerializer, PlansSerializer


class subscriptionView(APIView):

    def get(self, request: Request, format=None):
        user = request.user

        if user.has_subscription():
            subscription = user.subscription
            plan = subscription.plan
            plan_serializer = PlansSerializer(plan)
            subscription_serializer = SubscriptionSerializer(subscription)

            data = {
                "plan": plan_serializer.data,
                "subscription": subscription_serializer.data
            }

            return Response(data,status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_402_PAYMENT_REQUIRED)
