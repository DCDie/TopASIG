# Generated by Django 5.1.4 on 2025-01-15 21:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0007_rename_qr_type_qrcode_type_remove_qrcode_qr_as_image_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='qrcode',
            options={'verbose_name': 'QR Code', 'verbose_name_plural': 'QR Codes'},
        ),
    ]
