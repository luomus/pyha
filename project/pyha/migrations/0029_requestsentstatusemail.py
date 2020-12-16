# Generated by Django 3.0.2 on 2020-12-16 14:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pyha', '0028_auto_20201215_1628'),
    ]

    operations = [
        migrations.CreateModel(
            name='RequestSentStatusEmail',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('accepted_count', models.IntegerField()),
                ('declined_count', models.IntegerField()),
                ('pending_count', models.IntegerField()),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pyha.Request')),
            ],
        ),
    ]
