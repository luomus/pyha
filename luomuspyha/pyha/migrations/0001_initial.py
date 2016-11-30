# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-30 13:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=500)),
                ('count', models.IntegerField()),
                ('status', models.IntegerField()),
                ('taxonSecured', models.IntegerField(default=0)),
                ('customSecured', models.IntegerField(default=0)),
                ('downloadRequestHandler', models.CharField(max_length=500, null=True)),
                ('decisionExplanation', models.CharField(max_length=1000, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('lajiId', models.CharField(max_length=200)),
                ('description', models.CharField(max_length=400)),
                ('status', models.IntegerField()),
                ('sensstatus', models.IntegerField()),
                ('sensDecisionExplanation', models.CharField(max_length=1000, null=True)),
                ('date', models.DateTimeField()),
                ('source', models.CharField(max_length=60)),
                ('user', models.CharField(max_length=100)),
                ('approximateMatches', models.IntegerField()),
                ('downloadFormat', models.CharField(max_length=40)),
                ('downloadIncludes', models.CharField(max_length=1000)),
                ('filter_list', models.CharField(max_length=2000)),
                ('reason', models.CharField(max_length=1000, null=True)),
            ],
            managers=[
                ('requests', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='RequestLogEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('user', models.CharField(max_length=100)),
                ('role', models.CharField(max_length=100)),
                ('action', models.CharField(choices=[('VIEW', 'views request'), ('DEL_S', 'deletes sensitive sightings'), ('DEL_C', 'deletes sightings secured by data provider'), ('ACC', 'accepts terms of use'), ('POS', 'accepts use of data'), ('NEG', 'declines use of data')], max_length=5)),
                ('collection', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='pyha.Collection')),
                ('request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pyha.Request')),
            ],
            managers=[
                ('requestLog', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AddField(
            model_name='collection',
            name='request',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pyha.Request'),
        ),
    ]
