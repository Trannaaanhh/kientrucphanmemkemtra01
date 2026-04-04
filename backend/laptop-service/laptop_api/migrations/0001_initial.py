from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="LaptopProduct",
            fields=[
                ("id", models.CharField(max_length=10, primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=255)),
                ("category", models.CharField(default="laptop", max_length=20)),
                ("brand", models.CharField(max_length=120)),
                ("specs", models.TextField()),
                ("price", models.BigIntegerField()),
                ("stock", models.IntegerField(default=0)),
                ("image", models.CharField(blank=True, default="", max_length=500)),
            ],
            options={
                "db_table": "laptop_products",
                "ordering": ["id"],
            },
        ),
    ]
