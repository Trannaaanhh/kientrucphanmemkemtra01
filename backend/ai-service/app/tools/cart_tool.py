import os

import requests

CART_SERVICE_URL = os.getenv("CART_SERVICE_URL", "http://cart-service:8000")


def add_to_cart(user_id: str, product_id: str, quantity: int = 1):
    res = requests.post(
        f"{CART_SERVICE_URL}/cart/add",
        json={
            "user_id": user_id,
            "product_id": product_id,
            "quantity": quantity,
        },
        headers={"Guest-Id": str(user_id)},
        timeout=5,
    )
    return {
        "status_code": res.status_code,
        "data": res.json(),
    }


def get_cart(user_id: str):
    res = requests.get(
        f"{CART_SERVICE_URL}/cart/",
        headers={"Guest-Id": str(user_id)},
        timeout=5,
    )
    return {
        "status_code": res.status_code,
        "data": res.json() if res.headers.get("content-type", "").startswith("application/json") else {},
    }
