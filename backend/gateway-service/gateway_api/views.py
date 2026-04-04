import os
import re
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

import jwt
import requests
from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

JWT_SECRET = os.getenv("JWT_SECRET", "dev-gateway-secret")
JWT_ALGO = "HS256"
JWT_EXP_MINUTES = int(os.getenv("JWT_EXP_MINUTES", "1440"))  # 24 hours for dev (prod: 120 min)

CUSTOMER_SERVICE_URL = os.getenv("CUSTOMER_SERVICE_URL", "http://customer-service:8000")
STAFF_SERVICE_URL = os.getenv("STAFF_SERVICE_URL", "http://staff-service:8000")
LAPTOP_SERVICE_URL = os.getenv("LAPTOP_SERVICE_URL", "http://laptop-service:8000")
MOBILE_SERVICE_URL = os.getenv("MOBILE_SERVICE_URL", "http://mobile-service:8000")
PC_SERVICE_URL = os.getenv("PC_SERVICE_URL", "http://pc-service:8000")
INVENTORY_SERVICE_URL = os.getenv("INVENTORY_SERVICE_URL", "http://inventory-service:8000")
ORDER_SERVICE_URL = os.getenv("ORDER_SERVICE_URL", "http://order-service:8000")
PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL", "http://payment-service:8000")
ASSET_STORAGE_DIR = os.getenv("ASSET_STORAGE_DIR", "/shared-assets")

CUSTOMER_USERS = {
    "customer@example.com": {
        "password": "customer123",
        "customer_id": "C001",
        "name": "Nguyễn Văn An",
        "email": "customer@example.com",
    },
}

STAFF_USERS = {
    "staff@example.com": {
        "password": "staff123",
        "staff_id": "S001",
        "name": "Trần Thị Bình",
        "email": "staff@example.com",
    },
}


def build_token(subject_id: str, role: str, name: str = "", email: str = "") -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject_id,
        "role": role,
        "name": name,
        "email": email,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=JWT_EXP_MINUTES)).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)


def decode_token(auth_header: str):
    if not auth_header or not auth_header.startswith("Bearer "):
        return None, "Missing or invalid Authorization header"
    token = auth_header.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
        return payload, None
    except jwt.ExpiredSignatureError:
        return None, "Token expired"
    except jwt.InvalidTokenError:
        return None, "Invalid token"


def require_role(request, role: str):
    payload, err = decode_token(request.headers.get("Authorization", ""))
    if err:
        return None, Response({"error": err}, status=status.HTTP_401_UNAUTHORIZED)
    if payload.get("role") != role:
        return None, Response({"error": "Forbidden for this role"}, status=status.HTTP_403_FORBIDDEN)
    return payload, None


def proxy_get(url: str, params=None):
    response = requests.get(url, params=params, timeout=5)
    return Response(response.json(), status=response.status_code)


def proxy_post(url: str, payload):
    response = requests.post(url, json=payload, timeout=5)
    return Response(response.json(), status=response.status_code)


def proxy_put(url: str, payload):
    response = requests.put(url, json=payload, timeout=5)
    return Response(response.json(), status=response.status_code)


def _slugify_filename(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "product"


def _guess_extension(image_url: str, content_type: str) -> str:
    path_ext = os.path.splitext(urlparse(image_url).path)[1].lower()
    if path_ext in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
        return path_ext

    content_map = {
        "image/png": ".png",
        "image/jpeg": ".jpg",
        "image/jpg": ".jpg",
        "image/webp": ".webp",
        "image/gif": ".gif",
    }
    return content_map.get(content_type.lower(), ".png")


class RootView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        if "text/html" in request.headers.get("Accept", ""):
            return HttpResponse(
                """
                <!doctype html>
                <html lang=\"en\">
                <head>
                    <meta charset=\"utf-8\" />
                    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
                    <title>Kiemtra01 API Gateway</title>
                    <style>
                        body { font-family: Arial, sans-serif; margin: 0; background: #f4f7fb; color: #102030; }
                        .wrap { max-width: 860px; margin: 40px auto; background: #fff; padding: 24px; border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,.08); }
                        h1 { margin-top: 0; }
                        code { background: #eef3ff; padding: 2px 6px; border-radius: 6px; }
                        li { margin: 8px 0; }
                    </style>
                </head>
                <body>
                    <main class=\"wrap\">
                        <h1>Kiemtra01 API Gateway</h1>
                        <p>Gateway is running successfully.</p>
                        <p>Base URL: <code>http://localhost:8000</code></p>
                        <h2>Available Endpoints</h2>
                        <ul>
                            <li><code>/health</code></li>
                            <li><code>/info</code></li>
                            <li><code>/auth/customer/login</code></li>
                            <li><code>/auth/staff/login</code></li>
                            <li><code>/catalog/search?q=...&category=all|laptop|mobile|pc</code></li>
                            <li><code>/customer/cart/create</code></li>
                            <li><code>/customer/cart/add</code></li>
                            <li><code>/customer/cart</code></li>
                            <li><code>/staff/products</code></li>
                            <li><code>/staff/products/{product_id}</code></li>
                            <li><code>/pc/products</code> (public GET, staff POST/PUT)</li>
                            <li><code>/pc/products/{product_id}</code> (staff only)</li>
                            <li><code>/pc/inventory/check</code> (internal only)</li>
                            <li><code>/pc/inventory/deduct</code> (internal only)</li>
                        </ul>
                    </main>
                </body>
                </html>
                """
            )

        return Response(
            {
                "service": "gateway-service",
                "status": "ok",
                "message": "Kiemtra01 API Gateway is running",
                "endpoints": {
                    "health": "/health",
                    "info": "/info",
                    "customer_login": "/auth/customer/login",
                    "staff_login": "/auth/staff/login",
                    "catalog_search": "/catalog/search?q=...&category=all|laptop|mobile|pc",
                    "cart_create": "/customer/cart/create",
                    "cart_add": "/customer/cart/add",
                    "cart_get": "/customer/cart",
                    "staff_add_product": "/staff/products",
                    "staff_update_product": "/staff/products/{product_id}",
                    "pc_list_products": "GET /pc/products",
                    "pc_create_product": "POST /pc/products (staff only)",
                    "pc_update_product": "PUT /pc/products/{product_id} (staff only)",
                    "pc_inventory_check": "POST /pc/inventory/check (internal only)",
                    "pc_inventory_deduct": "POST /pc/inventory/deduct (internal only)",
                },
            }
        )

class HealthView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response({'status': 'ok', 'service': 'gateway-service'})

class ServiceInfoView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response({'service': 'gateway-service', 'app': 'gateway_api'})


class CustomerLoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        email = request.data.get("email", "")
        password = request.data.get("password", "")

        user = CUSTOMER_USERS.get(email)
        if not user or user["password"] != password:
            return Response({"error": "Invalid customer credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        token = build_token(user["customer_id"], "customer", user.get("name", ""), user.get("email", email))
        return Response({
            "access_token": token,
            "role": "customer",
            "customer_id": user["customer_id"],
            "name": user.get("name", ""),
            "email": user.get("email", email),
        })


class StaffLoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        email = request.data.get("email", "")
        password = request.data.get("password", "")

        user = STAFF_USERS.get(email)
        if not user or user["password"] != password:
            return Response({"error": "Invalid staff credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        token = build_token(user["staff_id"], "staff", user.get("name", ""), user.get("email", email))
        return Response({
            "access_token": token,
            "role": "staff",
            "staff_id": user["staff_id"],
            "name": user.get("name", ""),
            "email": user.get("email", email),
        })


class CatalogSearchView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        payload, error_response = require_role(request, "customer")
        if error_response:
            return error_response

        query = request.query_params.get("q", "")
        category = request.query_params.get("category", "all")

        results = []
        if category in ("all", "laptop"):
            laptop_resp = requests.get(f"{LAPTOP_SERVICE_URL}/products/search", params={"q": query}, timeout=5)
            if laptop_resp.ok:
                results.extend(laptop_resp.json().get("items", []))
        if category in ("all", "mobile"):
            mobile_resp = requests.get(f"{MOBILE_SERVICE_URL}/products/search", params={"q": query}, timeout=5)
            if mobile_resp.ok:
                results.extend(mobile_resp.json().get("items", []))
        if category in ("all", "pc"):
            pc_resp = requests.get(f"{PC_SERVICE_URL}/products/search", params={"q": query}, timeout=5)
            if pc_resp.ok:
                results.extend(pc_resp.json().get("items", []))

        return Response({"customer_id": payload.get("sub"), "items": results})


class CartCreateView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        payload, error_response = require_role(request, "customer")
        if error_response:
            return error_response

        return proxy_post(f"{CUSTOMER_SERVICE_URL}/customer/cart/create", {"customer_id": payload.get("sub")})


class CartAddView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        payload, error_response = require_role(request, "customer")
        if error_response:
            return error_response

        outbound = {
            "customer_id": payload.get("sub"),
            "product_id": request.data.get("product_id"),
            "name": request.data.get("name"),
            "category": request.data.get("category"),
            "price": request.data.get("price"),
            "quantity": request.data.get("quantity", 1),
            "image": request.data.get("image", ""),
            "brand": request.data.get("brand", ""),
            "specs": request.data.get("specs", ""),
        }
        return proxy_post(f"{CUSTOMER_SERVICE_URL}/customer/cart/add", outbound)


class CartGetView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        payload, error_response = require_role(request, "customer")
        if error_response:
            return error_response
        customer_id = payload.get("sub")
        return proxy_get(f"{CUSTOMER_SERVICE_URL}/customer/cart/{customer_id}")


class CustomerCheckoutView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        payload, error_response = require_role(request, "customer")
        if error_response:
            return error_response

        items = request.data.get("items") or []
        if not isinstance(items, list) or len(items) == 0:
            return Response({"error": "Checkout items are required"}, status=status.HTTP_400_BAD_REQUEST)

        prepared_updates = []
        total_amount = 0

        for item in items:
            product_id = item.get("id") or item.get("product_id")
            category = item.get("category")
            quantity = int(item.get("quantity", 0))

            if not product_id or category not in ("laptop", "mobile") or quantity <= 0:
                return Response({"error": "Invalid checkout item data"}, status=status.HTTP_400_BAD_REQUEST)

            service_url = LAPTOP_SERVICE_URL if category == "laptop" else MOBILE_SERVICE_URL
            product_resp = requests.get(f"{service_url}/products/{product_id}", timeout=5)
            if not product_resp.ok:
                return Response({"error": f"Product not found: {product_id}"}, status=status.HTTP_404_NOT_FOUND)

            product = product_resp.json()
            current_stock = int(product.get("stock", 0))
            if current_stock < quantity:
                return Response(
                    {
                        "error": f"Not enough stock for {product.get('name', product_id)}",
                        "product_id": product_id,
                        "current_stock": current_stock,
                        "requested": quantity,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            prepared_updates.append((service_url, product_id, current_stock - quantity, category))
            total_amount += int(product.get("price", 0)) * quantity

        for service_url, product_id, new_stock, category in prepared_updates:
            update_resp = requests.put(
                f"{service_url}/products/{product_id}",
                json={"stock": new_stock, "category": category},
                timeout=5,
            )
            if not update_resp.ok:
                return Response({"error": f"Failed to update stock for {product_id}"}, status=status.HTTP_502_BAD_GATEWAY)

        clear_resp = requests.post(
            f"{CUSTOMER_SERVICE_URL}/customer/cart/clear",
            json={"customer_id": payload.get("sub")},
            timeout=5,
        )
        if not clear_resp.ok:
            return Response({"error": "Payment captured but failed to clear cart"}, status=status.HTTP_502_BAD_GATEWAY)

        return Response(
            {
                "message": "Thanh toán thành công",
                "customer_id": payload.get("sub"),
                "total_amount": total_amount,
                "item_count": len(items),
            }
        )


class StaffAddProductView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        payload, error_response = require_role(request, "staff")
        if error_response:
            return error_response

        query = request.query_params.get("q", "")
        category = request.query_params.get("category", "all")

        results = []
        if category in ("all", "laptop"):
            laptop_resp = requests.get(f"{LAPTOP_SERVICE_URL}/products/search", params={"q": query}, timeout=5)
            if laptop_resp.ok:
                results.extend(laptop_resp.json().get("items", []))

        if category in ("all", "mobile"):
            mobile_resp = requests.get(f"{MOBILE_SERVICE_URL}/products/search", params={"q": query}, timeout=5)
            if mobile_resp.ok:
                results.extend(mobile_resp.json().get("items", []))

        return Response({"staff_id": payload.get("sub"), "items": results})

    def post(self, request):
        payload, error_response = require_role(request, "staff")
        if error_response:
            return error_response

        outbound = dict(request.data)
        outbound["updated_by"] = payload.get("sub")
        category = outbound.get("category", "laptop")

        staff_record = proxy_post(f"{STAFF_SERVICE_URL}/staff/audit/add", outbound)
        if staff_record.status_code >= 400:
            return staff_record

        target_url = f"{LAPTOP_SERVICE_URL}/products" if category == "laptop" else f"{MOBILE_SERVICE_URL}/products"
        return proxy_post(target_url, outbound)


class StaffUpdateProductView(APIView):
    authentication_classes = []
    permission_classes = []

    def put(self, request, product_id: str):
        payload, error_response = require_role(request, "staff")
        if error_response:
            return error_response

        outbound = dict(request.data)
        outbound["updated_by"] = payload.get("sub")
        category = outbound.get("category", "laptop")

        staff_record = proxy_post(f"{STAFF_SERVICE_URL}/staff/audit/update", {"product_id": product_id, **outbound})
        if staff_record.status_code >= 400:
            return staff_record

        target_url = f"{LAPTOP_SERVICE_URL}/products/{product_id}" if category == "laptop" else f"{MOBILE_SERVICE_URL}/products/{product_id}"
        return proxy_put(target_url, outbound)


# ── Inventory proxy ──────────────────────────────────────────
class InventoryProxyView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        payload, err = decode_token(request.headers.get("Authorization", ""))
        if err:
            return Response({"error": err}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            resp = requests.get(f"{INVENTORY_SERVICE_URL}/inventory/", timeout=5)
            return Response(resp.json(), status=resp.status_code)
        except requests.RequestException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

    def post(self, request):
        payload, err = decode_token(request.headers.get("Authorization", ""))
        if err:
            return Response({"error": err}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            resp = requests.post(f"{INVENTORY_SERVICE_URL}/inventory/", json=request.data, timeout=5)
            return Response(resp.json(), status=resp.status_code)
        except requests.RequestException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)


class InventoryCheckProxyView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        payload, err = decode_token(request.headers.get("Authorization", ""))
        if err:
            return Response({"error": err}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            resp = requests.post(f"{INVENTORY_SERVICE_URL}/inventory/check", json=request.data, timeout=5)
            return Response(resp.json(), status=resp.status_code)
        except requests.RequestException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)


# ── Order proxy ───────────────────────────────────────────────
class OrderProxyView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        payload, err = decode_token(request.headers.get("Authorization", ""))
        if err:
            return Response({"error": err}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            resp = requests.get(f"{ORDER_SERVICE_URL}/orders/", timeout=5)
            return Response(resp.json(), status=resp.status_code)
        except requests.RequestException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

    def post(self, request):
        payload, err = decode_token(request.headers.get("Authorization", ""))
        if err:
            return Response({"error": err}, status=status.HTTP_401_UNAUTHORIZED)
        customer_id = payload.get("sub", "guest")
        outbound = dict(request.data)
        try:
            resp = requests.post(
                f"{ORDER_SERVICE_URL}/orders/",
                json=outbound,
                headers={"Guest-Id": customer_id},
                timeout=10,
            )
            return Response(resp.json(), status=resp.status_code)
        except requests.RequestException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)


# ── PC Service routing ────────────────────────────────────────
class PcProductView(APIView):
    """
    GET /pc/products - Public access to list PC products
    POST /pc/products - Staff only access to create PC product
    """
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        try:
            resp = requests.get(f"{PC_SERVICE_URL}/products", timeout=5)
            return Response(resp.json(), status=resp.status_code)
        except requests.RequestException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

    def post(self, request):
        payload, error_response = require_role(request, "staff")
        if error_response:
            return error_response

        outbound = dict(request.data)
        outbound["updated_by"] = payload.get("sub")

        staff_record = proxy_post(f"{STAFF_SERVICE_URL}/staff/audit/add", outbound)
        if staff_record.status_code >= 400:
            return staff_record

        return proxy_post(f"{PC_SERVICE_URL}/products", outbound)


class PcProductDetailView(APIView):
    """PUT /pc/products/<product_id> - Staff only access to update PC product"""
    authentication_classes = []
    permission_classes = []

    def put(self, request, product_id: str):
        payload, error_response = require_role(request, "staff")
        if error_response:
            return error_response

        outbound = dict(request.data)
        outbound["updated_by"] = payload.get("sub")

        staff_record = proxy_post(f"{STAFF_SERVICE_URL}/staff/audit/update", {"product_id": product_id, **outbound})
        if staff_record.status_code >= 400:
            return staff_record

        return proxy_put(f"{PC_SERVICE_URL}/products/{product_id}", outbound)


class PcInventoryCheckView(APIView):
    """POST /pc/inventory/check - Internal only access to check PC inventory"""
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        # Internal only - check for internal caller header
        internal_token = request.headers.get("X-Internal-Service", "")
        if not internal_token or internal_token != os.getenv("INTERNAL_SECRET", "internal-secret"):
            return Response({"error": "Internal service access only"}, status=status.HTTP_403_FORBIDDEN)

        try:
            resp = requests.post(f"{PC_SERVICE_URL}/inventory/check", json=request.data, timeout=5)
            return Response(resp.json(), status=resp.status_code)
        except requests.RequestException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)


class PcInventoryDeductView(APIView):
    """POST /pc/inventory/deduct - Internal only access to deduct PC inventory"""
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        # Internal only - check for internal caller header
        internal_token = request.headers.get("X-Internal-Service", "")
        if not internal_token or internal_token != os.getenv("INTERNAL_SECRET", "internal-secret"):
            return Response({"error": "Internal service access only"}, status=status.HTTP_403_FORBIDDEN)

        try:
            resp = requests.post(f"{PC_SERVICE_URL}/inventory/deduct", json=request.data, timeout=5)
            return Response(resp.json(), status=resp.status_code)
        except requests.RequestException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)


# ── Payment proxy ─────────────────────────────────────────────
class PaymentProxyView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        payload, err = decode_token(request.headers.get("Authorization", ""))
        if err:
            return Response({"error": err}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            resp = requests.get(f"{PAYMENT_SERVICE_URL}/payment/", timeout=5)
            return Response(resp.json(), status=resp.status_code)
        except requests.RequestException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)


class PaymentCreateProxyView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        payload, err = decode_token(request.headers.get("Authorization", ""))
        if err:
            return Response({"error": err}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            resp = requests.post(f"{PAYMENT_SERVICE_URL}/payment/create", json=request.data, timeout=5)
            return Response(resp.json(), status=resp.status_code)
        except requests.RequestException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)


class StaffImportAssetView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        payload, error_response = require_role(request, "staff")
        if error_response:
            return error_response

        image_url = (request.data.get("image_url") or "").strip()
        product_name = (request.data.get("name") or "product").strip()
        category = (request.data.get("category") or "product").strip().lower()

        if not image_url.startswith("http://") and not image_url.startswith("https://"):
            return Response({"error": "Only http/https image URLs are supported"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            upstream = requests.get(image_url, timeout=15)
        except requests.RequestException:
            return Response({"error": "Cannot download image from URL"}, status=status.HTTP_400_BAD_REQUEST)

        if not upstream.ok:
            return Response({"error": "Image URL responded with an error"}, status=status.HTTP_400_BAD_REQUEST)

        content_type = (upstream.headers.get("Content-Type") or "").split(";")[0].strip().lower()
        if not content_type.startswith("image/"):
            return Response({"error": "URL is not an image resource"}, status=status.HTTP_400_BAD_REQUEST)

        ext = _guess_extension(image_url, content_type)
        base_name = f"{category}-{_slugify_filename(product_name)}"

        os.makedirs(ASSET_STORAGE_DIR, exist_ok=True)
        filename = f"{base_name}{ext}"
        file_path = os.path.join(ASSET_STORAGE_DIR, filename)

        suffix = 1
        while os.path.exists(file_path):
            filename = f"{base_name}-{suffix}{ext}"
            file_path = os.path.join(ASSET_STORAGE_DIR, filename)
            suffix += 1

        with open(file_path, "wb") as image_file:
            image_file.write(upstream.content)

        return Response({
            "staff_id": payload.get("sub"),
            "image": f"/assets/{filename}",
        })
