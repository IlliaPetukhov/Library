# Generated by Django 4.1 on 2024-12-08 03:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("library_borrow", "0005_alter_borrowing_actual_return_date"),
    ]

    operations = [
        migrations.AlterField(
            model_name="payment",
            name="session_id",
            field=models.CharField(max_length=1000),
        ),
    ]