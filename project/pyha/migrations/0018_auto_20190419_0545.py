# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-04-19 05:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pyha', '0017_auto_20190415_0349'),
    ]

    operations = [
        migrations.RenameField(
            model_name='handlerinrequest',
            old_name='address',
            new_name='user',
        ),
        migrations.RenameField(
            model_name='historicalhandlerinrequest',
            old_name='address',
            new_name='user',
        ),
        migrations.AddField(
            model_name='adminusersettings',
            name='changedBy',
            field=models.CharField(default=None, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='handlerinrequest',
            name='changedBy',
            field=models.CharField(default=None, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='historicaladminusersettings',
            name='changedBy',
            field=models.CharField(default=None, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='historicalhandlerinrequest',
            name='changedBy',
            field=models.CharField(default=None, max_length=100),
            preserve_default=False,
        ),
    ]