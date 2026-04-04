from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .models import LaptopProduct

LAPTOP_ICON_PATH = "/assets/laptop-icon.svg"

SEED_PRODUCTS = [
    {
        "id": "L001",
        "name": "ASUS ROG Strix G18 G815LM S9088W",
        "category": "laptop",
        "brand": "ASUS",
        "specs": "Intel Core i9, 32GB RAM, 1TB SSD",
        "price": 65990000,
        "stock": 10000,
        "image": "/assets/laptop-asus-rog-strix-g18-g815lm-s9088w.png",
    },
    {
        "id": "L002",
        "name": "ASUS ROG Strix G18 G815LR S9211W",
        "category": "laptop",
        "brand": "ASUS",
        "specs": "Intel Core i9, 32GB RAM, 1TB SSD",
        "price": 63990000,
        "stock": 10000,
        "image": "/assets/laptop-asus-rog-strix-g18-g815lr-s9211w.png",
    },
    {
        "id": "L003",
        "name": "ASUS ROG Strix SCAR 18 G835LW",
        "category": "laptop",
        "brand": "ASUS",
        "specs": "Intel Core Ultra 9, 32GB RAM, 1TB SSD",
        "price": 72990000,
        "stock": 10000,
        "image": "/assets/laptop-asus-rog-strix-scar-18-g835lw.png",
    },
    {
        "id": "L004",
        "name": "ASUS ROG Zephyrus G14 GA403WM",
        "category": "laptop",
        "brand": "ASUS",
        "specs": "Ryzen 9, 16GB RAM, 1TB SSD",
        "price": 45990000,
        "stock": 10000,
        "image": "/assets/laptop-asus-rog-zephyrus-g14-ga403wm.png",
    },
    {
        "id": "L005",
        "name": "ASUS ROG Strix G16 G615JPR S5107W",
        "category": "laptop",
        "brand": "ASUS",
        "specs": "Intel Core i9, 16GB RAM, 1TB SSD",
        "price": 48990000,
        "stock": 10000,
        "image": "/assets/laptop-asus-rog-strix-g16-g615jpr-s5107w.png",
    },
    {
        "id": "L006",
        "name": "ROG Strix SCAR 18 (2025) G835LW-SA172W",
        "category": "laptop",
        "brand": "ASUS",
        "specs": "Intel Core Ultra 9 275HX, RTX 5080, 64GB RAM, 4TB SSD, 18\" 2.5K 240Hz Mini LED",
        "price": 81990000,
        "stock": 10000,
        "image": "/assets/laptop-asus-rog-strix-scar-18-g835lw-sa172w.png",
    },
    {
        "id": "L007",
        "name": "Lenovo Legion Pro 7i Gen 9",
        "category": "laptop",
        "brand": "Lenovo",
        "specs": "Intel Core i9-14900HX, RTX 4080, 32GB RAM, 1TB SSD",
        "price": 69990000,
        "stock": 10000,
        "image": LAPTOP_ICON_PATH,
    },
    {
        "id": "L008",
        "name": "MSI Raider GE78 HX",
        "category": "laptop",
        "brand": "MSI",
        "specs": "Intel Core i9-14900HX, RTX 4090, 32GB RAM, 2TB SSD",
        "price": 85990000,
        "stock": 10000,
        "image": LAPTOP_ICON_PATH,
    },
    {
        "id": "L009",
        "name": "Acer Predator Helios 18",
        "category": "laptop",
        "brand": "Acer",
        "specs": "Intel Core i9-14900HX, RTX 4070, 32GB RAM, 1TB SSD",
        "price": 57990000,
        "stock": 10000,
        "image": LAPTOP_ICON_PATH,
    },
    {
        "id": "L010",
        "name": "Dell XPS 16 9640",
        "category": "laptop",
        "brand": "Dell",
        "specs": "Intel Core Ultra 9, RTX 4060, 32GB RAM, 1TB SSD, 4K OLED",
        "price": 74990000,
        "stock": 10000,
        "image": LAPTOP_ICON_PATH,
    },
    {
        "id": "L011",
        "name": "HP Omen Transcend 16",
        "category": "laptop",
        "brand": "HP",
        "specs": "Intel Core i7-14700HX, RTX 4070, 16GB RAM, 1TB SSD",
        "price": 46990000,
        "stock": 10000,
        "image": LAPTOP_ICON_PATH,
    },
    {
        "id": "L012",
        "name": "ASUS Zenbook Pro 14 OLED",
        "category": "laptop",
        "brand": "ASUS",
        "specs": "Intel Core Ultra 7, RTX 4050, 16GB RAM, 1TB SSD",
        "price": 39990000,
        "stock": 10000,
        "image": LAPTOP_ICON_PATH,
    },
    {
        "id": "L013",
        "name": "Apple MacBook Pro 16 M4 Pro",
        "category": "laptop",
        "brand": "Apple",
        "specs": "Apple M4 Pro, 36GB Unified Memory, 1TB SSD",
        "price": 82990000,
        "stock": 10000,
        "image": LAPTOP_ICON_PATH,
    },
    {
        "id": "L014",
        "name": "Gigabyte AORUS 17X",
        "category": "laptop",
        "brand": "Gigabyte",
        "specs": "Intel Core i9-14900HX, RTX 4080, 32GB RAM, 2TB SSD",
        "price": 71990000,
        "stock": 10000,
        "image": LAPTOP_ICON_PATH,
    },
    {
        "id": "L015",
        "name": "Razer Blade 16",
        "category": "laptop",
        "brand": "Razer",
        "specs": "Intel Core i9-14900HX, RTX 4090, 32GB RAM, 2TB SSD",
        "price": 96990000,
        "stock": 10000,
        "image": LAPTOP_ICON_PATH,
    },
    {
        "id": "L016",
        "name": "LG Gram Pro 16",
        "category": "laptop",
        "brand": "LG",
        "specs": "Intel Core Ultra 7, RTX 3050, 32GB RAM, 1TB SSD",
        "price": 42990000,
        "stock": 10000,
        "image": LAPTOP_ICON_PATH,
    },
]


def ensure_seed_data():
    existing_ids = set(LaptopProduct.objects.values_list("id", flat=True))
    missing_items = [item for item in SEED_PRODUCTS if item["id"] not in existing_ids]
    if missing_items:
        LaptopProduct.objects.bulk_create([LaptopProduct(**item) for item in missing_items])


def next_product_id() -> str:
    latest = LaptopProduct.objects.filter(id__startswith="L").order_by("-id").first()
    if not latest:
        return "L001"
    try:
        return f"L{int(latest.id[1:]) + 1:03d}"
    except ValueError:
        return f"L{LaptopProduct.objects.count() + 1:03d}"

class HealthView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response({'status': 'ok', 'service': 'laptop-service'})

class ServiceInfoView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response({'service': 'laptop-service', 'app': 'laptop_api'})


class LaptopProductListCreateView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        ensure_seed_data()
        items = [product.to_dict() for product in LaptopProduct.objects.all()]
        return Response({"items": items})

    def post(self, request):
        ensure_seed_data()
        required = ["name", "brand", "specs", "price", "stock"]
        missing = [field for field in required if request.data.get(field) in (None, "")]
        if missing:
            return Response({"error": f"Missing fields: {', '.join(missing)}"}, status=status.HTTP_400_BAD_REQUEST)

        item = LaptopProduct.objects.create(
            id=request.data.get("id") or next_product_id(),
            name=request.data.get("name"),
            category="laptop",
            brand=request.data.get("brand"),
            specs=request.data.get("specs"),
            price=int(request.data.get("price")),
            stock=int(request.data.get("stock")),
            image=request.data.get("image", ""),
        )
        return Response(item.to_dict(), status=status.HTTP_201_CREATED)


class LaptopProductUpdateView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, product_id: str):
        ensure_seed_data()
        try:
            product = LaptopProduct.objects.get(id=product_id)
        except LaptopProduct.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response(product.to_dict())

    def put(self, request, product_id: str):
        ensure_seed_data()
        try:
            product = LaptopProduct.objects.get(id=product_id)
        except LaptopProduct.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        for key in ["name", "brand", "specs", "image"]:
            if key in request.data:
                setattr(product, key, request.data.get(key))
        if "price" in request.data:
            product.price = int(request.data.get("price"))
        if "stock" in request.data:
            product.stock = int(request.data.get("stock"))

        if "category" in request.data:
            product.category = request.data.get("category") or "laptop"

        product.save()

        return Response(product.to_dict())


class LaptopProductSearchView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        ensure_seed_data()
        query = request.query_params.get("q", "").lower().strip()
        if not query:
            items = [product.to_dict() for product in LaptopProduct.objects.all()]
            return Response({"items": items})

        items = [
            product.to_dict()
            for product in LaptopProduct.objects.filter(
                Q(name__icontains=query) | Q(brand__icontains=query) | Q(specs__icontains=query)
            )
        ]
        return Response({"items": items})
