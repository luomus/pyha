# Generated by Django 3.0.2 on 2020-12-18 10:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pyha', '0029_requestsentstatusemail'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalrequest',
            name='filter_description_list',
            field=models.CharField(default='', max_length=6000),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='request',
            name='filter_description_list',
            field=models.CharField(default='', max_length=6000),
            preserve_default=False,
        ),
    ]