# Generated by Django 4.1 on 2024-12-05 15:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library_borrow', '0002_alter_borrowing_actual_return_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='borrowing',
            name='is_active',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='borrowing',
            name='actual_return_date',
            field=models.DateField(auto_now=True, null=True),
        ),
    ]
