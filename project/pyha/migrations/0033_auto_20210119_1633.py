# Generated by Django 3.0.2 on 2021-01-19 16:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pyha', '0032_auto_20210111_1611'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalrequest',
            name='filter_description_list',
            field=models.CharField(max_length=10000),
        ),
        migrations.AlterField(
            model_name='historicalrequest',
            name='private_link',
            field=models.CharField(max_length=10000),
        ),
        migrations.AlterField(
            model_name='historicalrequest',
            name='public_link',
            field=models.CharField(max_length=10000),
        ),
        migrations.AlterField(
            model_name='request',
            name='filter_description_list',
            field=models.CharField(max_length=10000),
        ),
        migrations.AlterField(
            model_name='request',
            name='private_link',
            field=models.CharField(max_length=10000),
        ),
        migrations.AlterField(
            model_name='request',
            name='public_link',
            field=models.CharField(max_length=10000),
        ),
    ]
