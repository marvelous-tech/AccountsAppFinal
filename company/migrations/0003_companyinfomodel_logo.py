# Generated by Django 2.1.5 on 2019-02-10 19:05

import company.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0002_auto_20190210_2340'),
    ]

    operations = [
        migrations.AddField(
            model_name='companyinfomodel',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to=company.models.user_directory_path),
        ),
    ]
