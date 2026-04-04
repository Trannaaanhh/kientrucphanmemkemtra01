from django.db.models import Q, F
from django.db import transaction
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .models import PcProduct

PC_ICON_PATH = "/assets/pc-icon.svg"

SEED_PRODUCTS = [
    {
        "id": "PC001",
        "name": "ASUS ROG Strix GA15DK Gaming Desktop",
        "category": "pc",
        "brand": "ASUS",
        "specs": "Intel Core i9-12900K, RTX 4090, 32GB RAM, 1TB SSD",
        "price": 89990000,
        "stock": 10000,
        "image": PC_ICON_PATH,
        "form_factor": "gaming_pc",
        "cpu_cores": 16,
        "gpu_vram_gb": 24,
        "usb_ports": 8,
        "hdmi_ports": 2,
    },
    {
        "id": "PC002",
        "name": "Corsair iCUE 5000T RGB Tempered Glass Case",
        "category": "pc",
        "brand": "Corsair",
        "specs": "Ryzen 9 5900X, RTX 3080 Ti, 64GB RAM, 2TB NVMe SSD",
        "price": 75990000,
        "stock": 10000,
        "image": PC_ICON_PATH,
        "form_factor": "gaming_pc",
        "cpu_cores": 12,
        "gpu_vram_gb": 12,
        "usb_ports": 10,
        "hdmi_ports": 2,
    },
    {
        "id": "PC003",
        "name": "Intel NUC 12 Enthusiast Mini PC",
        "category": "pc",
        "brand": "Intel",
        "specs": "Intel Core i7-12700H, Intel Arc A770, 32GB RAM, 512GB SSD",
        "price": 28990000,
        "stock": 10000,
        "image": PC_ICON_PATH,
        "form_factor": "mini_pc",
        "cpu_cores": 14,
        "gpu_vram_gb": 4,
        "usb_ports": 6,
        "hdmi_ports": 2,
    },
    {
        "id": "PC004",
        "name": "Apple iMac 27-inch M3 Max All-in-One",
        "category": "pc",
        "brand": "Apple",
        "specs": "Apple M3 Max, 36GB Unified Memory, 1TB SSD, 27\" 5K Retina Display",
        "price": 99990000,
        "stock": 10000,
        "image": PC_ICON_PATH,
        "form_factor": "all_in_one",
        "cpu_cores": 12,
        "gpu_vram_gb": 0,
        "usb_ports": 4,
        "hdmi_ports": 1,
    },
    {
        "id": "PC005",
        "name": "Dell Precision 7770 Workstation Laptop",
        "category": "pc",
        "brand": "Dell",
        "specs": "Intel Xeon W-12900, RTX 6000 Ada, 96GB RAM, 4TB SSD, RTX 6000 Professional GPU",
        "price": 199990000,
        "stock": 10000,
        "image": PC_ICON_PATH,
        "form_factor": "workstation",
        "cpu_cores": 24,
        "gpu_vram_gb": 48,
        "usb_ports": 8,
        "hdmi_ports": 1,
    },
    {
        "id": "PC006",
        "name": "HP Omen 45L Gaming Desktop",
        "category": "pc",
        "brand": "HP",
        "specs": "Intel Core i7-14700K, RTX 4070 Ti SUPER, 32GB RAM, 1TB SSD",
        "price": 62990000,
        "stock": 10000,
        "image": PC_ICON_PATH,
        "form_factor": "gaming_pc",
        "cpu_cores": 20,
        "gpu_vram_gb": 16,
        "usb_ports": 9,
        "hdmi_ports": 1,
    },
    {
        "id": "PC007",
        "name": "Lenovo ThinkCentre M90q Gen 4",
        "category": "pc",
        "brand": "Lenovo",
        "specs": "Intel Core i5-13500T, Integrated Graphics, 16GB RAM, 512GB SSD",
        "price": 21990000,
        "stock": 10000,
        "image": PC_ICON_PATH,
        "form_factor": "mini_pc",
        "cpu_cores": 14,
        "gpu_vram_gb": 0,
        "usb_ports": 7,
        "hdmi_ports": 2,
    },
    {
        "id": "PC008",
        "name": "MSI Pro AP272 All-in-One",
        "category": "pc",
        "brand": "MSI",
        "specs": "Intel Core i7-1360P, Integrated Graphics, 16GB RAM, 1TB SSD, 27\" FHD",
        "price": 30990000,
        "stock": 10000,
        "image": PC_ICON_PATH,
        "form_factor": "all_in_one",
        "cpu_cores": 12,
        "gpu_vram_gb": 0,
        "usb_ports": 6,
        "hdmi_ports": 1,
    },
    {
        "id": "PC009",
        "name": "Acer Veriton X Workstation",
        "category": "pc",
        "brand": "Acer",
        "specs": "Intel Core i9-13900, RTX 4060, 64GB RAM, 2TB SSD",
        "price": 48990000,
        "stock": 10000,
        "image": PC_ICON_PATH,
        "form_factor": "workstation",
        "cpu_cores": 24,
        "gpu_vram_gb": 8,
        "usb_ports": 10,
        "hdmi_ports": 2,
    },
    {
        "id": "PC010",
        "name": "ASRock DeskMini X600",
        "category": "pc",
        "brand": "ASRock",
        "specs": "AMD Ryzen 7 8700G, Radeon 780M, 32GB RAM, 1TB SSD",
        "price": 25990000,
        "stock": 10000,
        "image": PC_ICON_PATH,
        "form_factor": "desktop",
        "cpu_cores": 8,
        "gpu_vram_gb": 0,
        "usb_ports": 6,
        "hdmi_ports": 2,
    },
]


def ensure_seed_data():
    existing_ids = set(PcProduct.objects.values_list("id", flat=True))
    missing_items = [item for item in SEED_PRODUCTS if item["id"] not in existing_ids]
    if missing_items:
        PcProduct.objects.bulk_create([PcProduct(**item) for item in missing_items])


def next_product_id() -> str:
    latest = PcProduct.objects.filter(id__startswith="PC").order_by("-id").first()
    if not latest:
        return "PC001"
    try:
        return f"PC{int(latest.id[2:]) + 1:03d}"
    except ValueError:
        return f"PC{PcProduct.objects.count() + 1:03d}"


class HealthView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response({'status': 'ok', 'service': 'pc-service'})


class ServiceInfoView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response({'service': 'pc-service', 'app': 'pc_api'})


class PcProductListCreateView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        ensure_seed_data()
        items = [product.to_dict() for product in PcProduct.objects.all()]
        return Response({"items": items})

    def post(self, request):
        ensure_seed_data()
        required = ["name", "brand", "specs", "price", "stock"]
        missing = [field for field in required if request.data.get(field) in (None, "")]
        if missing:
            return Response({"error": f"Missing fields: {', '.join(missing)}"}, status=status.HTTP_400_BAD_REQUEST)

        item = PcProduct.objects.create(
            id=request.data.get("id") or next_product_id(),
            name=request.data.get("name"),
            category="pc",
            brand=request.data.get("brand"),
            specs=request.data.get("specs"),
            price=int(request.data.get("price")),
            stock=int(request.data.get("stock")),
            image=request.data.get("image", ""),
            form_factor=request.data.get("form_factor", "desktop"),
            cpu_cores=int(request.data.get("cpu_cores", 0)),
            gpu_vram_gb=int(request.data.get("gpu_vram_gb", 0)),
            usb_ports=int(request.data.get("usb_ports", 0)),
            hdmi_ports=int(request.data.get("hdmi_ports", 0)),
        )
        return Response(item.to_dict(), status=status.HTTP_201_CREATED)


class PcProductUpdateView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, product_id: str):
        ensure_seed_data()
        try:
            product = PcProduct.objects.get(id=product_id)
        except PcProduct.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response(product.to_dict())

    def put(self, request, product_id: str):
        ensure_seed_data()
        try:
            product = PcProduct.objects.get(id=product_id)
        except PcProduct.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        for key in ["name", "brand", "specs", "image", "form_factor"]:
            if key in request.data:
                setattr(product, key, request.data.get(key))
        if "price" in request.data:
            product.price = int(request.data.get("price"))
        if "stock" in request.data:
            product.stock = int(request.data.get("stock"))
        if "cpu_cores" in request.data:
            product.cpu_cores = int(request.data.get("cpu_cores"))
        if "gpu_vram_gb" in request.data:
            product.gpu_vram_gb = int(request.data.get("gpu_vram_gb"))
        if "usb_ports" in request.data:
            product.usb_ports = int(request.data.get("usb_ports"))
        if "hdmi_ports" in request.data:
            product.hdmi_ports = int(request.data.get("hdmi_ports"))

        if "category" in request.data:
            product.category = request.data.get("category") or "pc"

        product.save()

        return Response(product.to_dict())


class PcProductSearchView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        ensure_seed_data()
        query = request.query_params.get("q", "").lower().strip()
        if not query:
            items = [product.to_dict() for product in PcProduct.objects.all()]
            return Response({"items": items})

        items = [
            product.to_dict()
            for product in PcProduct.objects.filter(
                Q(name__icontains=query) | Q(brand__icontains=query) | Q(specs__icontains=query)
            )
        ]
        return Response({"items": items})


class InventoryCheckView(APIView):
    """Check if products have sufficient stock"""
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        items = request.data.get("items", [])
        if not items:
            return Response({"error": "No items provided"}, status=status.HTTP_400_BAD_REQUEST)

        results = []
        for item in items:
            product_id = item.get("product_id")
            quantity = item.get("quantity", 0)
            try:
                # Use select_for_update to prevent race conditions
                with transaction.atomic():
                    product = PcProduct.objects.select_for_update().get(id=product_id)
                    has_stock = product.stock >= quantity
                    results.append({
                        "product_id": product_id,
                        "quantity": quantity,
                        "available_stock": product.stock,
                        "can_fulfill": has_stock,
                    })
            except PcProduct.DoesNotExist:
                results.append({
                    "product_id": product_id,
                    "quantity": quantity,
                    "available_stock": 0,
                    "can_fulfill": False,
                    "error": "Product not found",
                })

        return Response({"items": results})


class InventoryDeductView(APIView):
    """Deduct stock from products"""
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        items = request.data.get("items", [])
        if not items:
            return Response({"error": "No items provided"}, status=status.HTTP_400_BAD_REQUEST)

        results = []
        try:
            with transaction.atomic():
                for item in items:
                    product_id = item.get("product_id")
                    quantity = item.get("quantity", 0)
                    try:
                        # Use select_for_update to prevent race conditions
                        product = PcProduct.objects.select_for_update().get(id=product_id)
                        if product.stock >= quantity:
                            product.stock = F('stock') - quantity
                            product.save()
                            product.refresh_from_db()
                            results.append({
                                "product_id": product_id,
                                "quantity": quantity,
                                "remaining_stock": product.stock,
                                "success": True,
                            })
                        else:
                            results.append({
                                "product_id": product_id,
                                "quantity": quantity,
                                "available_stock": product.stock,
                                "success": False,
                                "error": "Insufficient stock",
                            })
                    except PcProduct.DoesNotExist:
                        results.append({
                            "product_id": product_id,
                            "quantity": quantity,
                            "success": False,
                            "error": "Product not found",
                        })
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"items": results})
