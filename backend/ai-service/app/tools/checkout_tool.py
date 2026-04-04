import os

import requests

ORDER_SERVICE_URL = os.getenv("ORDER_SERVICE_URL", "http://order-service:8000")


def checkout(user_id: str, payment_method: str = "COD", address: str = "Ha Noi"):
    res = requests.post(
        f"{ORDER_SERVICE_URL}/orders/checkout",
        json={
            "user_id": user_id,
            "payment_method": payment_method,
            "address": address,
        },
        timeout=10,
    )
    return {
        "status_code": res.status_code,
        "data": res.json(),
    }
