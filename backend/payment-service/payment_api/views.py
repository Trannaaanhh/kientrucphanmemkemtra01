from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError
from .models import Payment

class PaymentListView(APIView):
    def get(self, request):
        payments = Payment.objects.all().order_by('-created_at')
        from django.core.serializers.json import DjangoJSONEncoder
        import json
        return Response([
            {
                "id": p.id,
                "transaction_id": p.transaction_id,
                "order_id": p.order_id,
                "amount": str(p.amount),
                "status": p.status,
                "created_at": p.created_at.isoformat()
            } for p in payments
        ])

class PaymentCreateView(APIView):
    def post(self, request):
        transaction_id = request.data.get("transaction_id")
        amount = request.data.get("amount")
        order_id = request.data.get("order_id")

        if not transaction_id:
            return Response({"error": "Requires transaction_id for idempotency"}, status=status.HTTP_400_BAD_REQUEST)

        existing_payment = Payment.objects.filter(transaction_id=transaction_id).first()
        if existing_payment:
            return Response({
                "message": "Payment already processed", 
                "status": existing_payment.status
            }, status=status.HTTP_200_OK)

        payment_status = 'SUCCESS' if float(amount) > 0 else 'FAILED'

        try:
            payment = Payment.objects.create(
                transaction_id=transaction_id,
                order_id=order_id,
                amount=amount,
                status=payment_status
            )
            return Response({"status": payment.status, "transaction_id": transaction_id})
        except IntegrityError:
            return Response({"error": "Concurrent request detected"}, status=status.HTTP_409_CONFLICT)

class PaymentConfirmView(APIView):
    def post(self, request):
        return Response({"status": "SUCCESS"})
