from django.db import models


class PcProduct(models.Model):
    FORM_FACTOR_CHOICES = [
        ('desktop', 'Desktop'),
        ('gaming_pc', 'Gaming PC'),
        ('mini_pc', 'Mini PC'),
        ('all_in_one', 'All In One'),
        ('workstation', 'Workstation'),
    ]

    STATUS_CHOICES = [
        ('available', 'Available'),
        ('out_of_stock', 'Out of Stock'),
    ]

    id = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=20, default="pc")
    brand = models.CharField(max_length=120)
    specs = models.TextField()
    price = models.BigIntegerField()
    stock = models.IntegerField(default=0)
    image = models.CharField(max_length=500, blank=True, default="")
    
    # PC-specific fields
    form_factor = models.CharField(max_length=20, choices=FORM_FACTOR_CHOICES, default='desktop')
    cpu_cores = models.IntegerField(default=0)
    gpu_vram_gb = models.IntegerField(default=0)
    usb_ports = models.IntegerField(default=0)
    hdmi_ports = models.IntegerField(default=0)
    
    # Auto-sync status field
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        db_table = "pc_products"
        ordering = ["id"]

    def save(self, *args, **kwargs):
        # Auto-sync status based on stock
        if self.stock <= 0:
            self.status = 'out_of_stock'
        else:
            self.status = 'available'
        super().save(*args, **kwargs)

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
            "form_factor": self.form_factor,
            "cpu_cores": self.cpu_cores,
            "gpu_vram_gb": self.gpu_vram_gb,
            "usb_ports": self.usb_ports,
            "hdmi_ports": self.hdmi_ports,
            "status": self.status,
        }
