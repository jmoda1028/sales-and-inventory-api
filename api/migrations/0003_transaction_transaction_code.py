# Generated by Django 4.1 on 2022-09-09 06:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_alter_transaction_customer_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='transaction_code',
            field=models.IntegerField(null=True, unique=True),
        ),
    ]