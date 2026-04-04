import uuid
import requests
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Order, OrderItem
from .serializers import OrderSerializer

INVENTORY_URL = os.getenv("INVENTORY_SERVICE_URL", "http://inventory-service:8000")
PAYMENT_URL = os.getenv("PAYMENT_SERVICE_URL", "http://payment-service:8000")
LAPTOP_URL = os.getenv("LAPTOP_SERVICE_URL", "http://laptop-service:8000")
MOBILE_URL = os.getenv("MOBILE_SERVICE_URL", "http://mobile-service:8000")
CART_URL = os.getenv("CART_SERVICE_URL", "http://cart-service:8000")


def _find_product_price(product_id: str) -> int:
    for base_url in (LAPTOP_URL, MOBILE_URL):
        try:
            resp = requests.get(f"{base_url}/products/{product_id}", timeout=3)
            if resp.ok:
                return int(resp.json().get("price", 0))
        except requests.exceptions.RequestException:
            continue
    return 0


def _create_order_from_items(customer_id: str, items: list, total_amount):
    # 1. Create order (PENDING)
    order = Order.objects.create(
        customer_id=customer_id,
        total_amount=total_amount,
        status='PENDING',
        transaction_id=str(uuid.uuid4())
    )
    for item in items:
        OrderItem.objects.create(order=order, product_id=item['product_id'], quantity=item['quantity'])

    # 2. Check stock
    try:
        inv_resp = requests.post(f"{INVENTORY_URL}/inventory/check", json={"items": items}, timeout=3)
        inv_data = inv_resp.json() if inv_resp.ok else {}
        if not inv_resp.ok or "error" in inv_data:
            order.status = 'CANCELLED'
            order.save()
            error_msg = inv_data.get("error", "Stock check failed/Out of stock")
            return Response({"error": error_msg}, status=status.HTTP_400_BAD_REQUEST)
    except requests.exceptions.RequestException:
        order.status = 'CANCELLED'
        order.save()
        return Response({"error": "Inventory service unavailable"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    # 3. Request payment
    try:
        pay_resp = requests.post(
            f"{PAYMENT_URL}/payment/create",
            json={"order_id": order.id, "transaction_id": order.transaction_id, "amount": float(total_amount)},
            timeout=5
        )

        pay_data = pay_resp.json() if pay_resp.ok else {}

        # 4. Success / Fail
        if pay_resp.ok and pay_data.get('status') == 'SUCCESS':
            order.status = 'PAID'
            order.save()
            # 5. Deduct stock upon successful payment
            requests.post(f"{INVENTORY_URL}/inventory/deduct", json={"items": items}, timeout=3)
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

        order.status = 'CANCELLED'
        order.save()
        return Response({"error": "Payment Failed", "details": pay_data}, status=status.HTTP_402_PAYMENT_REQUIRED)

    except requests.exceptions.RequestException as e:
        order.status = 'CANCELLED'
        order.save()
        return Response({"error": f"Payment Service Error: {str(e)}"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


def _fetch_cart_items(customer_id: str):
    try:
        resp = requests.get(
            f"{CART_URL}/cart/",
            headers={"Guest-Id": str(customer_id)},
            timeout=3,
        )
        if not resp.ok:
            return None, Response({"error": "Cannot get cart from cart-service"}, status=status.HTTP_502_BAD_GATEWAY)

        items = resp.json().get("items", [])
        if not items:
            return None, Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)
        return items, None
    except requests.exceptions.RequestException:
        return None, Response({"error": "Cart service unavailable"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


def _clear_cart(customer_id: str):
    try:
        requests.delete(
            f"{CART_URL}/cart/remove",
            headers={"Guest-Id": str(customer_id)},
            timeout=3,
        )
    except requests.exceptions.RequestException:
        return

class OrderCreateView(APIView):
    def get(self, request):
        orders = Order.objects.all().order_by('-created_at')
        return Response(OrderSerializer(orders, many=True).data)

    def post(self, request):
        customer_id = request.headers.get("Guest-Id", "guest")
        items = request.data.get("items", [])
        total_amount = request.data.get("total_amount", 0)

        if not items:
            return Response({"error": "No items"}, status=status.HTTP_400_BAD_REQUEST)

        return _create_order_from_items(str(customer_id), items, total_amount)


class OrderCheckoutView(APIView):
    def post(self, request):
        user_id = request.data.get("user_id")
        payment_method = request.data.get("payment_method", "COD")
        address = request.data.get("address", "")

        if user_id in (None, ""):
            return Response({"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        customer_id = str(user_id)
        cart_items, cart_error = _fetch_cart_items(customer_id)
        if cart_error:
            return cart_error

        total_amount = 0
        normalized_items = []
        for item in cart_items:
            product_id = item.get("product_id")
            quantity = int(item.get("quantity", 1))
            if not product_id or quantity <= 0:
                return Response({"error": "Invalid cart item"}, status=status.HTTP_400_BAD_REQUEST)

            price = _find_product_price(product_id)
            total_amount += price * quantity
            normalized_items.append({"product_id": product_id, "quantity": quantity})

        order_response = _create_order_from_items(customer_id, normalized_items, total_amount)
        if order_response.status_code < 400:
            _clear_cart(customer_id)
            payload = dict(order_response.data)
            payload["payment_method"] = payment_method
            payload["address"] = address
            payload["checkout_from"] = "cart"
            return Response(payload, status=order_response.status_code)

        return order_response

class OrderDetailView(APIView):
    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        return Response(OrderSerializer(order).data)
