# Generated by Django 5.0.3 on 2024-05-30 06:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_side', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='wallet_balance',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]