# Generated migration for PcProduct model

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PcProduct',
            fields=[
                ('id', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('category', models.CharField(default='pc', max_length=20)),
                ('brand', models.CharField(max_length=120)),
                ('specs', models.TextField()),
                ('price', models.BigIntegerField()),
                ('stock', models.IntegerField(default=0)),
                ('image', models.CharField(blank=True, default='', max_length=500)),
                ('form_factor', models.CharField(choices=[('desktop', 'Desktop'), ('gaming_pc', 'Gaming PC'), ('mini_pc', 'Mini PC'), ('all_in_one', 'All In One'), ('workstation', 'Workstation')], default='desktop', max_length=20)),
                ('cpu_cores', models.IntegerField(default=0)),
                ('gpu_vram_gb', models.IntegerField(default=0)),
                ('usb_ports', models.IntegerField(default=0)),
                ('hdmi_ports', models.IntegerField(default=0)),
                ('status', models.CharField(choices=[('available', 'Available'), ('out_of_stock', 'Out of Stock')], default='available', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, blank=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True, blank=True)),
            ],
            options={
                'db_table': 'pc_products',
                'ordering': ['id'],
            },
        ),
    ]
