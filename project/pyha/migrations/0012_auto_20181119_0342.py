# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-11-19 03:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pyha', '0011_auto_20181117_0237'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalrequest',
            name='description',
            field=models.CharField(blank=True, max_length=400, null=True),
        ),
        migrations.AlterField(
            model_name='request',
            name='description',
            field=models.CharField(blank=True, max_length=400, null=True),
        ),
    ]
