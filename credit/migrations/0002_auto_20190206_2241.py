# Generated by Django 2.1.5 on 2019-02-06 16:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('credit', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='creditfundsourcehistorymodel',
            name='credit_fund_source',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='all_histories', to='credit.CreditFundSourceModel'),
        ),
    ]