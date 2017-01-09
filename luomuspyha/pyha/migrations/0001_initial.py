# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-01-09 15:45
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
            name='ContactPreset',
            fields=[
                ('user', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('requestPersonName', models.CharField(max_length=100, null=True)),
                ('requestPersonStreetAddress', models.CharField(max_length=100, null=True)),
                ('requestPersonPostOfficeName', models.CharField(max_length=100, null=True)),
                ('requestPersonPostalCode', models.CharField(max_length=100, null=True)),
                ('requestPersonEmail', models.CharField(max_length=100, null=True)),
                ('requestPersonPhoneNumber', models.CharField(max_length=100, null=True)),
                ('requestPersonOrganizationName', models.CharField(max_length=100, null=True)),
                ('requestPersonCorporationId', models.CharField(max_length=100, null=True)),
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
                ('sensComment', models.CharField(max_length=1000, null=True)),
                ('date', models.DateTimeField()),
                ('source', models.CharField(max_length=60)),
                ('user', models.CharField(max_length=100)),
                ('approximateMatches', models.IntegerField()),
                ('downloadFormat', models.CharField(max_length=40)),
                ('downloadIncludes', models.CharField(max_length=1000)),
                ('filter_list', models.CharField(max_length=2000)),
                ('PersonName', models.CharField(max_length=100, null=True)),
                ('PersonStreetAddress', models.CharField(max_length=100, null=True)),
                ('PersonPostOfficeName', models.CharField(max_length=100, null=True)),
                ('PersonPostalCode', models.CharField(max_length=100, null=True)),
                ('PersonEmail', models.CharField(max_length=100, null=True)),
                ('PersonPhoneNumber', models.CharField(max_length=100, null=True)),
                ('PersonOrganizationName', models.CharField(max_length=100, null=True)),
                ('PersonCorporationId', models.CharField(max_length=100, null=True)),
                ('reason', models.CharField(max_length=16000, null=True)),
            ],
            managers=[
                ('requests', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='RequestChatEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('user', models.CharField(max_length=100)),
                ('message', models.CharField(max_length=2000)),
                ('request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pyha.Request')),
            ],
            managers=[
                ('requestChat', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='RequestContact',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('PersonName', models.CharField(max_length=100, null=True)),
                ('PersonStreetAddress', models.CharField(max_length=100, null=True)),
                ('PersonPostOfficeName', models.CharField(max_length=100, null=True)),
                ('PersonPostalCode', models.CharField(max_length=100, null=True)),
                ('PersonEmail', models.CharField(max_length=100, null=True)),
                ('PersonPhoneNumber', models.CharField(max_length=100, null=True)),
                ('PersonOrganizationName', models.CharField(max_length=100, null=True)),
                ('PersonCorporationId', models.CharField(max_length=100, null=True)),
                ('request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pyha.Request')),
            ],
        ),
        migrations.CreateModel(
            name='RequestLogEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('user', models.CharField(max_length=100)),
                ('role', models.CharField(max_length=100)),
                ('action', models.CharField(choices=[('VIEW', 'views request'), ('ACC', 'accepts terms of use'), ('POS', 'accepts use of data'), ('NEG', 'declines use of data')], max_length=5)),
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
