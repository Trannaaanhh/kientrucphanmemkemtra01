import os
import re
import requests
import jwt
from urllib.parse import urlparse
from datetime import datetime, timedelta, timezone
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

AUDIT_LOGS = []
STAFF_USERS = {
    "staff@example.com": {
        "password": "staff123",
        "staff_id": "S001",
        "name": "Trần Thị Bình",
        "email": "staff@example.com",
    },
}

JWT_SECRET = os.getenv("JWT_SECRET", "dev-gateway-secret")
JWT_ALGO = "HS256"
LAPTOP_SERVICE_URL = os.getenv("LAPTOP_SERVICE_URL", "http://laptop-service:8000")
MOBILE_SERVICE_URL = os.getenv("MOBILE_SERVICE_URL", "http://mobile-service:8000")
PC_SERVICE_URL = os.getenv("PC_SERVICE_URL", "http://pc-service:8000")
ASSET_STORAGE_DIR = os.getenv("ASSET_STORAGE_DIR", "/shared-assets")

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
        return Response({'status': 'ok', 'service': 'staff-service'})

class ServiceInfoView(APIView):
    authentication_classes = []
    permission_classes = []
    def get(self, request):
        return Response({'service': 'staff-service', 'app': 'staff_api'})

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

class StaffAddProductView(APIView):
    authentication_classes = []
    permission_classes = []
    def get(self, request):
        payload, error_response = require_role(request, "staff")
        if error_response: return error_response
        query = request.query_params.get("q", "")
        category = request.query_params.get("category", "all")
        results = []
        if category in ("all", "laptop"):
            try:
                resp = requests.get(f"{LAPTOP_SERVICE_URL}/products/search", params={"q": query}, timeout=5)
                if resp.ok: results.extend(resp.json().get("items", []))
            except: pass
        if category in ("all", "mobile"):
            try:
                resp = requests.get(f"{MOBILE_SERVICE_URL}/products/search", params={"q": query}, timeout=5)
                if resp.ok: results.extend(resp.json().get("items", []))
            except: pass
        if category in ("all", "pc"):
            try:
                resp = requests.get(f"{PC_SERVICE_URL}/products/search", params={"q": query}, timeout=5)
                if resp.ok: results.extend(resp.json().get("items", []))
            except: pass
        return Response({"staff_id": payload.get("sub"), "items": results})

    def post(self, request):
        payload, error_response = require_role(request, "staff")
        if error_response: return error_response
        outbound = dict(request.data)
        outbound["updated_by"] = payload.get("sub")
        category = outbound.get("category", "laptop")
        
        # Self-log audit
        AUDIT_LOGS.append({"action": "add", "name": outbound.get("name"), "category": category, "updated_by": payload.get("sub")})
        
        if category == "laptop":
            target_url = f"{LAPTOP_SERVICE_URL}/products"
        elif category == "mobile":
            target_url = f"{MOBILE_SERVICE_URL}/products"
        else:
            target_url = f"{PC_SERVICE_URL}/products"
        try:
            resp = requests.post(target_url, json=outbound, timeout=5)
            return Response(resp.json(), status=resp.status_code)
        except requests.RequestException:
            return Response({"error": "Gateway Error"}, status=status.HTTP_502_BAD_GATEWAY)

class StaffUpdateProductView(APIView):
    authentication_classes = []
    permission_classes = []
    def put(self, request, product_id: str):
        payload, error_response = require_role(request, "staff")
        if error_response: return error_response
        outbound = dict(request.data)
        outbound["updated_by"] = payload.get("sub")
        category = outbound.get("category", "laptop")
        
        # Self-log audit
        AUDIT_LOGS.append({"action": "update", "product_id": product_id, "category": category, "updated_by": payload.get("sub")})
        
        if category == "laptop":
            target_url = f"{LAPTOP_SERVICE_URL}/products/{product_id}"
        elif category == "mobile":
            target_url = f"{MOBILE_SERVICE_URL}/products/{product_id}"
        else:
            target_url = f"{PC_SERVICE_URL}/products/{product_id}"
        try:
            resp = requests.put(target_url, json=outbound, timeout=5)
            return Response(resp.json(), status=resp.status_code)
        except requests.RequestException:
            return Response({"error": "Gateway Error"}, status=status.HTTP_502_BAD_GATEWAY)

class StaffImportAssetView(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self, request):
        payload, error_response = require_role(request, "staff")
        if error_response: return error_response
        
        image_url = (request.data.get("image_url") or "").strip()
        product_name = (request.data.get("name") or "product").strip()
        category = (request.data.get("category") or "product").strip().lower()

        if not image_url.startswith("http://") and not image_url.startswith("https://"):
            return Response({"error": "Only http/https"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            upstream = requests.get(image_url, timeout=15)
            if not upstream.ok: return Response({"error": "Failed down"}, status=status.HTTP_400_BAD_REQUEST)
        except requests.RequestException:
            return Response({"error": "Cannot download"}, status=status.HTTP_400_BAD_REQUEST)

        content_type = (upstream.headers.get("Content-Type") or "").split(";")[0].strip().lower()
        if not content_type.startswith("image/"): return Response({"error": "Not image"}, status=status.HTTP_400_BAD_REQUEST)

        path_ext = os.path.splitext(urlparse(image_url).path)[1].lower()
        ext = path_ext if path_ext in {".png", ".jpg", ".jpeg", ".webp", ".gif"} else {
            "image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp", "image/gif": ".gif"
        }.get(content_type, ".png")

        base_name = f"{category}-{re.sub(r'[^a-z0-9]+', '-', product_name.lower()).strip('-') or 'product'}"
        os.makedirs(ASSET_STORAGE_DIR, exist_ok=True)
        filename = f"{base_name}{ext}"
        file_path = os.path.join(ASSET_STORAGE_DIR, filename)

        suffix = 1
        while os.path.exists(file_path):
            filename = f"{base_name}-{suffix}{ext}"
            file_path = os.path.join(ASSET_STORAGE_DIR, filename)
            suffix += 1

        with open(file_path, "wb") as image_file: image_file.write(upstream.content)
        return Response({"staff_id": payload.get("sub"), "image": f"/assets/{filename}"})

class StaffAuditAddView(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self, request):
        event = {"action": "add", "name": request.data.get("name"), "category": request.data.get("category"), "updated_by": request.data.get("updated_by")}
        AUDIT_LOGS.append(event)
        return Response({"message": "Audit add recorded", "event": event})

class StaffAuditUpdateView(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self, request):
        event = {"action": "update", "product_id": request.data.get("product_id"), "category": request.data.get("category", "laptop"), "updated_by": request.data.get("updated_by")}
        AUDIT_LOGS.append(event)
        return Response({"message": "Audit update recorded", "event": event})

class StaffAuditListView(APIView):
    authentication_classes = []
    permission_classes = []
    def get(self, request):
        return Response({"items": AUDIT_LOGS})
