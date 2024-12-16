from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.request import Request

from shop.models import CartItem


class CartItemApiView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request: Request, item_id: int, *args, **kwargs) -> Response:
        data = request.data.copy()

        action = data.pop('action', None)
        amount = data.pop('amount', None)

        if not action or not amount:
            return Response({"details", "Action and Amount required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            cart_item = CartItem.objects.prefetch_related("product", "product__stock").get(
                cart__user=request.user,
                id=item_id
            )
        except CartItem.DoesNotExist:
            return Response({"details", "Item not found"}, status=status.HTTP_404_NOT_FOUND)

        if action == 'increase':
            if cart_item.product.stock.is_available:
                cart_item.increase_quantity(amount)
        elif action == 'decrease':
            cart_item.decrease_quantity(amount)

            if cart_item.quantity <= 0:
                cart_item.delete()
                return Response(
                    {"details": "Success", "deleted": True, "display_price": cart_item.cart.get_display_price()},
                    status=status.HTTP_200_OK
                    )

        return Response(
            {"details": "Success", "quantity": cart_item.quantity, "display_price": cart_item.cart.get_display_price()},
            status=status.HTTP_200_OK
        )

    def delete(self, request: Request, item_id: int, *args, **kwargs) -> Response:
        try:
            cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
            cart_item.delete()
            return Response({"details": "Item deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except CartItem.DoesNotExist:
            return Response({"details": "Item not found"}, status=status.HTTP_404_NOT_FOUND)
