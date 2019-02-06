# Generated by Django 2.1.5 on 2019-02-05 13:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('base_user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompanyInfoModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('address', models.TextField()),
                ('company_type', models.CharField(choices=[('gr', 'Garment'), ('bh', 'Buying House'), ('as', 'Association'), ('en', 'Enterprise'), ('co', 'Corporation'), ('ps', 'Personal')], default='gr', max_length=45)),
                ('created', models.DateField(blank=True, null=True)),
                ('uuid', models.UUIDField(blank=True)),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('is_approved', models.BooleanField(default=False)),
                ('base_user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='company_user', to='base_user.BaseUserModel')),
            ],
        ),
    ]
