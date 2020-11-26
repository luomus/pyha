# Generated by Django 3.0.2 on 2020-11-26 13:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pyha', '0024_auto_20191203_0929'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalrequestlogentry',
            name='action',
            field=models.CharField(choices=[('VIEW', 'views request'), ('REC', 'receives request'), ('ACC', 'accepts terms of use'), ('POS', 'accepts use of data'), ('POSOV', 'accepted use of data, because decision has been overdue'), ('RESET', 'resets the decision regarding data'), ('NEG', 'declines use of data'), ('NEGOV', 'declines use of data, because decision has been overdue')], max_length=5),
        ),
        migrations.AlterField(
            model_name='requestlogentry',
            name='action',
            field=models.CharField(choices=[('VIEW', 'views request'), ('REC', 'receives request'), ('ACC', 'accepts terms of use'), ('POS', 'accepts use of data'), ('POSOV', 'accepted use of data, because decision has been overdue'), ('RESET', 'resets the decision regarding data'), ('NEG', 'declines use of data'), ('NEGOV', 'declines use of data, because decision has been overdue')], max_length=5),
        ),
    ]
