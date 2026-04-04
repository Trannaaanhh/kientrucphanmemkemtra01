from django.db import models


class LaptopProduct(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=20, default="laptop")
    brand = models.CharField(max_length=120)
    specs = models.TextField()
    price = models.BigIntegerField()
    stock = models.IntegerField(default=0)
    image = models.CharField(max_length=500, blank=True, default="")

    class Meta:
        db_table = "laptop_products"
        ordering = ["id"]

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "brand": self.brand,
            "specs": self.specs,
            "price": self.price,
            "stock": self.stock,
            "image": self.image,
        }
