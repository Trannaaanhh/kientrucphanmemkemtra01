from django.db import models

class Stock(models.Model):
    product_id = models.CharField(max_length=50, unique=True)
    quantity = models.PositiveIntegerField(default=0)
