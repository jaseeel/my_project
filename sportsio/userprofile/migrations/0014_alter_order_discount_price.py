# Generated by Django 5.0.3 on 2024-06-01 08:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0013_remove_cart_discount_price_remove_cart_total_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='discount_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, null=True),
        ),
    ]
