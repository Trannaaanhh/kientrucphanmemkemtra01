import redis
import json
import os
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

redis_conn = redis.Redis(host=os.getenv('REDIS_HOST', 'redis-db'), port=6379, db=0)
BEHAVIOR_SERVICE_URL = os.getenv('BEHAVIOR_SERVICE_URL', 'http://behavior-service:8000')


def _infer_category(product_id: str | None):
    if not product_id:
        return "unknown"
    pid = str(product_id).lower()
    if pid.startswith("l"):
        return "laptop"
    if pid.startswith("m"):
        return "mobile"
    if pid.startswith("p"):
        return "pc"
    return "unknown"


def _emit_behavior_event(user_id: str, event_type: str, product_id: str | None = None, quantity: int = 1):
    payload = {
        "user_id": str(user_id),
        "event_type": event_type,
        "product_id": product_id,
        "product_category": _infer_category(product_id),
        "quantity": max(int(quantity or 1), 1),
        "metadata": {"source": "cart-service"},
    }
    try:
        requests.post(f"{BEHAVIOR_SERVICE_URL}/behavior/events", json=payload, timeout=2)
    except requests.RequestException:
        return

def get_cart_key(request):
    token = request.headers.get("Authorization")
    guest_id = request.headers.get("Guest-Id")
    return f"cart:{guest_id or 'anonymous'}"


def get_user_id(request):
    guest_id = request.headers.get("Guest-Id")
    return str(guest_id or "anonymous")

class CartGetView(APIView):
    def get(self, request):
        try:
            key = get_cart_key(request)
            data = redis_conn.get(key)
            items = json.loads(data) if data else []
            return Response({"items": items})
        except redis.RedisError:
            return Response({"error": "Redis unavailable"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

class CartAddView(APIView):
    def post(self, request):
        key = get_cart_key(request)
        user_id = get_user_id(request)
        product_id = request.data.get("product_id")
        quantity = int(request.data.get("quantity", 1))

        if not product_id:
            return Response({"error": "Missing product_id"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            current = redis_conn.get(key)
            items = json.loads(current) if current else []

            found = False
            for it in items:
                if it["product_id"] == product_id:
                    it["quantity"] += quantity
                    found = True
                    break
            if not found:
                items.append({"product_id": product_id, "quantity": quantity})

            redis_conn.set(key, json.dumps(items), ex=86400)
            _emit_behavior_event(user_id, "add_cart", product_id=product_id, quantity=quantity)
            return Response({"message": "Added to cart", "items": items}, status=status.HTTP_201_CREATED)
        except redis.RedisError:
            return Response({"error": "Redis unavailable"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

class CartUpdateView(APIView):
    def put(self, request):
        key = get_cart_key(request)
        product_id = request.data.get("product_id")
        quantity = int(request.data.get("quantity", 0))

        try:
            current = redis_conn.get(key)
            items = json.loads(current) if current else []
            for it in items:
                if it["product_id"] == product_id:
                    it["quantity"] = quantity
                    break
            redis_conn.set(key, json.dumps(items), ex=86400)
            return Response({"message": "Updated cart", "items": items})
        except redis.RedisError:
            return Response({"error": "Redis unavailable"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

class CartRemoveView(APIView):
    def delete(self, request):
        key = get_cart_key(request)
        user_id = get_user_id(request)
        try:
            data = redis_conn.get(key)
            items = json.loads(data) if data else []
            redis_conn.delete(key)
            for item in items:
                _emit_behavior_event(
                    user_id,
                    "remove_cart",
                    product_id=item.get("product_id"),
                    quantity=int(item.get("quantity", 1)),
                )
            return Response({"message": "Cart cleared"}, status=status.HTTP_204_NO_CONTENT)
        except redis.RedisError:
            return Response({"error": "Redis unavailable"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
