# Generated by Django 4.1 on 2024-12-08 04:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("library_borrow", "0007_alter_payment_session_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="payment",
            name="session_id",
            field=models.CharField(max_length=10000),
        ),
    ]
