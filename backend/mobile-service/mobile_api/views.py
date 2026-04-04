from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .models import MobileProduct

MOBILE_ICON_PATH = "/assets/mobile-icon.svg"

SEED_PRODUCTS = [
    {
        "id": "M001",
        "name": "iPhone 17 Pro Max 256GB",
        "category": "mobile",
        "brand": "Apple",
        "specs": "A19 Pro, 256GB, 6.9\" OLED",
        "price": 38990000,
        "stock": 10000,
        "image": "/assets/mobile-iphone-17-pro-max-256gb.png",
    },
    {
        "id": "M002",
        "name": "Samsung Galaxy S25 Ultra 12GB 256GB",
        "category": "mobile",
        "brand": "Samsung",
        "specs": "12GB RAM, 256GB, 6.8\" AMOLED",
        "price": 33990000,
        "stock": 10000,
        "image": "/assets/mobile-samsung-galaxy-s25-ultra-12gb-256gb.png",
    },
    {
        "id": "M003",
        "name": "Samsung Galaxy Z Fold7 12GB 256GB",
        "category": "mobile",
        "brand": "Samsung",
        "specs": "12GB RAM, 256GB, Foldable AMOLED",
        "price": 42990000,
        "stock": 10000,
        "image": "/assets/mobile-samsung-galaxy-z-fold7-12gb-256gb.png",
    },
    {
        "id": "M004",
        "name": "Xiaomi 14T Pro 12GB 512GB",
        "category": "mobile",
        "brand": "Xiaomi",
        "specs": "12GB RAM, 512GB, 6.67\" AMOLED",
        "price": 19990000,
        "stock": 10000,
        "image": "/assets/mobile-xiaomi-14t-pro-12gb-512gb.png",
    },
    {
        "id": "M005",
        "name": "iPhone 16 Pro 256GB",
        "category": "mobile",
        "brand": "Apple",
        "specs": "A18 Pro, 256GB, 6.3\" OLED",
        "price": 31990000,
        "stock": 10000,
        "image": MOBILE_ICON_PATH,
    },
    {
        "id": "M006",
        "name": "Samsung Galaxy S24 FE 256GB",
        "category": "mobile",
        "brand": "Samsung",
        "specs": "8GB RAM, 256GB, 6.7\" AMOLED",
        "price": 15990000,
        "stock": 10000,
        "image": MOBILE_ICON_PATH,
    },
    {
        "id": "M007",
        "name": "Xiaomi 15 Ultra 16GB 512GB",
        "category": "mobile",
        "brand": "Xiaomi",
        "specs": "16GB RAM, 512GB, 6.73\" AMOLED",
        "price": 26990000,
        "stock": 10000,
        "image": MOBILE_ICON_PATH,
    },
    {
        "id": "M008",
        "name": "Google Pixel 9 Pro 256GB",
        "category": "mobile",
        "brand": "Google",
        "specs": "Tensor G4, 16GB RAM, 256GB, 6.7\" OLED",
        "price": 24990000,
        "stock": 10000,
        "image": MOBILE_ICON_PATH,
    },
    {
        "id": "M009",
        "name": "OPPO Find X8 Pro 512GB",
        "category": "mobile",
        "brand": "OPPO",
        "specs": "16GB RAM, 512GB, 6.82\" LTPO AMOLED",
        "price": 27990000,
        "stock": 10000,
        "image": MOBILE_ICON_PATH,
    },
    {
        "id": "M010",
        "name": "vivo X200 Pro 512GB",
        "category": "mobile",
        "brand": "vivo",
        "specs": "16GB RAM, 512GB, 6.78\" AMOLED",
        "price": 25990000,
        "stock": 10000,
        "image": MOBILE_ICON_PATH,
    },
    {
        "id": "M011",
        "name": "OnePlus 13 256GB",
        "category": "mobile",
        "brand": "OnePlus",
        "specs": "12GB RAM, 256GB, 6.82\" AMOLED",
        "price": 21990000,
        "stock": 10000,
        "image": MOBILE_ICON_PATH,
    },
    {
        "id": "M012",
        "name": "realme GT 7 Pro 512GB",
        "category": "mobile",
        "brand": "realme",
        "specs": "16GB RAM, 512GB, 6.78\" AMOLED",
        "price": 18990000,
        "stock": 10000,
        "image": MOBILE_ICON_PATH,
    },
    {
        "id": "M013",
        "name": "HONOR Magic7 Pro 512GB",
        "category": "mobile",
        "brand": "HONOR",
        "specs": "16GB RAM, 512GB, 6.8\" OLED",
        "price": 23990000,
        "stock": 10000,
        "image": MOBILE_ICON_PATH,
    },
    {
        "id": "M014",
        "name": "Sony Xperia 1 VI 256GB",
        "category": "mobile",
        "brand": "Sony",
        "specs": "12GB RAM, 256GB, 6.5\" OLED 120Hz",
        "price": 29990000,
        "stock": 10000,
        "image": MOBILE_ICON_PATH,
    },
]


def ensure_seed_data():
    existing_ids = set(MobileProduct.objects.values_list("id", flat=True))
    missing_items = [item for item in SEED_PRODUCTS if item["id"] not in existing_ids]
    if missing_items:
        MobileProduct.objects.bulk_create([MobileProduct(**item) for item in missing_items])


def next_product_id() -> str:
    latest = MobileProduct.objects.filter(id__startswith="M").order_by("-id").first()
    if not latest:
        return "M001"
    try:
        return f"M{int(latest.id[1:]) + 1:03d}"
    except ValueError:
        return f"M{MobileProduct.objects.count() + 1:03d}"

class HealthView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response({'status': 'ok', 'service': 'mobile-service'})

class ServiceInfoView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response({'service': 'mobile-service', 'app': 'mobile_api'})


class MobileProductListCreateView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        ensure_seed_data()
        items = [product.to_dict() for product in MobileProduct.objects.all()]
        return Response({"items": items})

    def post(self, request):
        ensure_seed_data()
        required = ["name", "brand", "specs", "price", "stock"]
        missing = [field for field in required if request.data.get(field) in (None, "")]
        if missing:
            return Response({"error": f"Missing fields: {', '.join(missing)}"}, status=status.HTTP_400_BAD_REQUEST)

        item = MobileProduct.objects.create(
            id=request.data.get("id") or next_product_id(),
            name=request.data.get("name"),
            category="mobile",
            brand=request.data.get("brand"),
            specs=request.data.get("specs"),
            price=int(request.data.get("price")),
            stock=int(request.data.get("stock")),
            image=request.data.get("image", ""),
        )
        return Response(item.to_dict(), status=status.HTTP_201_CREATED)


class MobileProductUpdateView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, product_id: str):
        ensure_seed_data()
        try:
            product = MobileProduct.objects.get(id=product_id)
        except MobileProduct.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response(product.to_dict())

    def put(self, request, product_id: str):
        ensure_seed_data()
        try:
            product = MobileProduct.objects.get(id=product_id)
        except MobileProduct.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        for key in ["name", "brand", "specs", "image"]:
            if key in request.data:
                setattr(product, key, request.data.get(key))
        if "price" in request.data:
            product.price = int(request.data.get("price"))
        if "stock" in request.data:
            product.stock = int(request.data.get("stock"))

        if "category" in request.data:
            product.category = request.data.get("category") or "mobile"

        product.save()

        return Response(product.to_dict())


class MobileProductSearchView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        ensure_seed_data()
        query = request.query_params.get("q", "").lower().strip()
        if not query:
            items = [product.to_dict() for product in MobileProduct.objects.all()]
            return Response({"items": items})

        items = [
            product.to_dict()
            for product in MobileProduct.objects.filter(
                Q(name__icontains=query) | Q(brand__icontains=query) | Q(specs__icontains=query)
            )
        ]
        return Response({"items": items})
