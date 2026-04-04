import os
import jwt
import requests
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

CARTS = {}
CUSTOMER_USERS = {
    "customer@example.com": {
        "password": "customer123",
        "customer_id": "C001",
        "name": "Nguyễn Văn An",
        "email": "customer@example.com",
    },
}

JWT_SECRET = os.getenv("JWT_SECRET", "dev-gateway-secret")
JWT_ALGO = "HS256"
LAPTOP_SERVICE_URL = os.getenv("LAPTOP_SERVICE_URL", "http://laptop-service:8000")
MOBILE_SERVICE_URL = os.getenv("MOBILE_SERVICE_URL", "http://mobile-service:8000")
PC_SERVICE_URL = os.getenv("PC_SERVICE_URL", "http://pc-service:8000")

def decode_token(auth_header: str):
    if not auth_header or not auth_header.startswith("Bearer "):
        return None, "Missing or invalid Authorization header"
    token = auth_header.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
        return payload, None
    except Exception as e:
        return None, "Invalid token"

def require_role(request, role: str):
    payload, err = decode_token(request.headers.get("Authorization", ""))
    if err:
        return None, Response({"error": err}, status=status.HTTP_401_UNAUTHORIZED)
    if payload.get("role") != role:
        return None, Response({"error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
    return payload, None

from datetime import datetime, timedelta, timezone
def build_token(subject_id: str, role: str, name: str = "", email: str = "") -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject_id,
        "role": role,
        "name": name,
        "email": email,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=1440)).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)

class HealthView(APIView):
    authentication_classes = []
    permission_classes = []
    def get(self, request):
        return Response({'status': 'ok', 'service': 'customer-service'})

class ServiceInfoView(APIView):
    authentication_classes = []
    permission_classes = []
    def get(self, request):
        return Response({'service': 'customer-service', 'app': 'customer_api'})

class CustomerLoginView(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self, request):
        email = request.data.get("email", "")
        password = request.data.get("password", "")
        user = CUSTOMER_USERS.get(email)
        if not user or user["password"] != password:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        token = build_token(user["customer_id"], "customer", user.get("name", ""), user.get("email", email))
        return Response({
            "access_token": token,
            "role": "customer",
            "customer_id": user["customer_id"],
            "name": user.get("name", ""),
            "email": user.get("email", email),
        })

class CatalogSearchView(APIView):
    authentication_classes = []
    permission_classes = []
    def get(self, request):
        customer_id = None
        payload, _ = decode_token(request.headers.get("Authorization", ""))
        if payload:
            customer_id = payload.get("sub")
            
        query = request.query_params.get("q", "")
        category = request.query_params.get("category", "all")
        results = []

        laptop_path = "/products" if not query.strip() else "/products/search"
        mobile_path = "/products" if not query.strip() else "/products/search"
        pc_path = "/products" if not query.strip() else "/products/search"
        laptop_params = None if not query.strip() else {"q": query}
        mobile_params = None if not query.strip() else {"q": query}
        pc_params = None if not query.strip() else {"q": query}

        if category in ("all", "laptop"):
            try:
                resp = requests.get(f"{LAPTOP_SERVICE_URL}{laptop_path}", params=laptop_params, timeout=5)
                if resp.ok: results.extend(resp.json().get("items", []))
            except: pass
        if category in ("all", "mobile"):
            try:
                resp = requests.get(f"{MOBILE_SERVICE_URL}{mobile_path}", params=mobile_params, timeout=5)
                if resp.ok: results.extend(resp.json().get("items", []))
            except: pass
        if category in ("all", "pc"):
            try:
                resp = requests.get(f"{PC_SERVICE_URL}{pc_path}", params=pc_params, timeout=5)
                if resp.ok: results.extend(resp.json().get("items", []))
            except: pass
        return Response({"customer_id": customer_id, "items": results})

class CartCreateView(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self, request):
        customer_id = request.headers.get('Guest-Id')
        payload, _ = decode_token(request.headers.get("Authorization", ""))
        if payload and payload.get("role") == "customer": customer_id = payload.get("sub")
        if not customer_id: return Response({"error": "Auth or Guest-Id required"}, status=status.HTTP_401_UNAUTHORIZED)
        CARTS.setdefault(customer_id, [])
        return Response({"message": "Cart created", "customer_id": customer_id, "items": CARTS[customer_id]})

class CartAddView(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self, request):
        customer_id = request.headers.get('Guest-Id')
        payload, _ = decode_token(request.headers.get("Authorization", ""))
        if payload and payload.get("role") == "customer": customer_id = payload.get("sub")
        if not customer_id: return Response({"error": "Auth or Guest-Id required"}, status=status.HTTP_401_UNAUTHORIZED)
        
        product_id = request.data.get("product_id")
        cart = CARTS.setdefault(customer_id, [])
        quantity = int(request.data.get("quantity", 1))
        existing = next((item for item in cart if item.get("product_id") == product_id or item.get("id") == product_id), None)
        if existing:
            existing["quantity"] += quantity
        else:
            cart.append({
                "product_id": product_id,
                "id": product_id,
                "name": request.data.get("name", ""),
                "category": request.data.get("category", ""),
                "price": request.data.get("price", 0),
                "quantity": quantity,
                "image": request.data.get("image", ""),
                "brand": request.data.get("brand", ""),
                "specs": request.data.get("specs", ""),
            })
        return Response({"message": "Item added", "customer_id": customer_id, "items": cart})

class CartGetView(APIView):
    authentication_classes = []
    permission_classes = []
    def get(self, request, customer_id=None):
        cid = request.headers.get('Guest-Id', 'guest')
        payload, _ = decode_token(request.headers.get("Authorization", ""))
        if payload and payload.get("role") == "customer": cid = payload.get("sub")
        
        return Response({"customer_id": cid, "items": CARTS.get(cid, [])})

class CartClearView(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self, request):
        customer_id = request.headers.get('Guest-Id')
        payload, _ = decode_token(request.headers.get("Authorization", ""))
        if payload and payload.get("role") == "customer": customer_id = payload.get("sub")
        if not customer_id: return Response({"error": "Auth or Guest-Id required"}, status=status.HTTP_401_UNAUTHORIZED)
            
        CARTS[customer_id] = []
        return Response({"message": "Cart cleared", "customer_id": customer_id, "items": []})

class CustomerCheckoutView(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self, request):
        payload, error_response = require_role(request, "customer")
        if error_response: return error_response
        items = request.data.get("items") or []
        if not items: return Response({"error": "Checkout items are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        prepared_updates = []
        total_amount = 0
        for item in items:
            product_id = item.get("id") or item.get("product_id")
            category = item.get("category")
            quantity = int(item.get("quantity", 0))
            if not product_id or category not in ("laptop", "mobile", "pc"):
                return Response({"error": "Invalid checkout item data"}, status=status.HTTP_400_BAD_REQUEST)
            
            if category == "laptop":
                service_url = LAPTOP_SERVICE_URL
            elif category == "mobile":
                service_url = MOBILE_SERVICE_URL
            else:
                service_url = PC_SERVICE_URL
            try:
                product_resp = requests.get(f"{service_url}/products/{product_id}", timeout=5)
                if not product_resp.ok: return Response({"error": f"Product not found: {product_id}"}, status=status.HTTP_404_NOT_FOUND)
                product = product_resp.json()
                current_stock = int(product.get("stock", 0))
                if current_stock < quantity:
                    return Response({"error": f"Not enough stock for {product.get('name', product_id)}"}, status=status.HTTP_400_BAD_REQUEST)
                prepared_updates.append((service_url, product_id, current_stock - quantity, category))
                total_amount += int(product.get("price", 0)) * quantity
            except requests.RequestException:
                return Response({"error": f"Failed contacting {category} service"}, status=status.HTTP_502_BAD_GATEWAY)

        for service_url, product_id, new_stock, category in prepared_updates:
            requests.put(f"{service_url}/products/{product_id}", json={"stock": new_stock, "category": category}, timeout=5)
        
        CARTS[payload.get("sub")] = []
        return Response({"message": "Thanh toán thành công", "customer_id": payload.get("sub"), "total_amount": total_amount, "item_count": len(items)})
