# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-12-03 10:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pyha', '0012_auto_20181119_0342'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalrequestlogentry',
            name='action',
            field=models.CharField(choices=[('VIEW', 'views request'), ('ACC', 'accepts terms of use'), ('POS', 'accepts use of data'), ('POSOVER', 'accepted use of data, because decision has been overdue'), ('RESET', 'resets the decision regarding data'), ('NEG', 'declines use of data')], max_length=5),
        ),
        migrations.AlterField(
            model_name='requestlogentry',
            name='action',
            field=models.CharField(choices=[('VIEW', 'views request'), ('ACC', 'accepts terms of use'), ('POS', 'accepts use of data'), ('POSOVER', 'accepted use of data, because decision has been overdue'), ('RESET', 'resets the decision regarding data'), ('NEG', 'declines use of data')], max_length=5),
        ),
    ]
