# Generated by Django 5.1.4 on 2025-03-09 20:20

import apps.ensurance.models
import django_minio_backend.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ensurance', '0007_rcacompany_is_public'),
    ]

    operations = [
        migrations.CreateModel(
            name='MedicalInsuranceCompany',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Company Name')),
                ('idno', models.CharField(max_length=50, unique=True, verbose_name='IDNO')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('is_public', models.BooleanField(default=True, verbose_name='Is Public')),
                ('logo', models.FileField(blank=True, null=True, storage=django_minio_backend.models.MinioBackend(bucket_name='media'), upload_to=apps.ensurance.models.rca_company_logo_path)),
            ],
            options={
                'verbose_name': 'Medical Insurance Company',
                'verbose_name_plural': 'Medical Insurance Companies',
            },
        ),
    ]
