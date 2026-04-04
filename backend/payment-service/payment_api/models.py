from django.db import models

class Payment(models.Model):
    transaction_id = models.CharField(max_length=100, unique=True)
    order_id = models.IntegerField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
