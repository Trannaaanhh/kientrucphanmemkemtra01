from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.shortcuts import get_object_or_404
from .models import Stock

class InventoryCheckView(APIView):
    def post(self, request):
        items = request.data.get("items", [])
        for item in items:
            stock = Stock.objects.filter(product_id=item['product_id']).first()
            if not stock or stock.quantity < int(item['quantity']):
                return Response({"error": f"Out of stock for {item['product_id']}"})
        return Response({"status": "OK"})

class InventoryDeductView(APIView):
    def post(self, request):
        items = request.data.get("items", [])
        try:
            with transaction.atomic():
                for item in items:
                    stock = Stock.objects.select_for_update().get(product_id=item['product_id'])
                    stock.quantity -= int(item['quantity'])
                    stock.save()
            return Response({"status": "DEDUCTED"})
        except Exception as e:
            return Response({"error": "Failed to deduct. " + str(e)}, status=status.HTTP_400_BAD_REQUEST)

class InventoryListView(APIView):
    def get(self, request):
        stocks = Stock.objects.all()
        return Response([{"product_id": s.product_id, "quantity": s.quantity} for s in stocks])

    def post(self, request):
        # Used by staff to mass-update or create stock
        items = request.data.get("items", [])
        for item in items:
            stock, created = Stock.objects.get_or_create(product_id=item['product_id'], defaults={'quantity': 0})
            stock.quantity = int(item['quantity'])
            stock.save()
        return Response({"status": "UPDATED"})

class InventoryDetailView(APIView):
    def get(self, request, product_id):
        stock = get_object_or_404(Stock, product_id=product_id)
        return Response({"product_id": stock.product_id, "quantity": stock.quantity})
    
    def put(self, request, product_id):
        stock, created = Stock.objects.get_or_create(product_id=product_id, defaults={'quantity': 0})
        stock.quantity = int(request.data.get("quantity", stock.quantity))
        stock.save()
        return Response({"product_id": stock.product_id, "quantity": stock.quantity})
