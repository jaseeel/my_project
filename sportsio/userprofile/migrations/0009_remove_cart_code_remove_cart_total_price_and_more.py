# Generated by Django 5.0.3 on 2024-05-21 10:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0008_cart_total_price'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cart',
            name='code',
        ),
        migrations.RemoveField(
            model_name='cart',
            name='total_price',
        ),
        migrations.AddField(
            model_name='cart',
            name='coupon_discount_amount',
            field=models.IntegerField(default=0, null=True),
        ),
    ]