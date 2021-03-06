# Generated by Django 3.0.2 on 2020-12-15 16:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pyha', '0027_auto_20201210_1721'),
    ]

    operations = [
        migrations.AddField(
            model_name='collection',
            name='count_list',
            field=models.CharField(default='', max_length=2000),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='historicalcollection',
            name='count_list',
            field=models.CharField(default='', max_length=2000),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='historicalrequestlogentry',
            name='action',
            field=models.CharField(choices=[('VIEW', 'views request'), ('REC', 'receives request'), ('ACC', 'accepts terms of use'), ('POS', 'accepts use of data'), ('POSOV', 'accepted use of data, because decision has been overdue'), ('RESET', 'resets the decision regarding data'), ('NEG', 'declines use of data'), ('NEGOV', 'declines use of data, because decision has been overdue'), ('WITHD', 'withdraws request')], max_length=5),
        ),
        migrations.AlterField(
            model_name='requestlogentry',
            name='action',
            field=models.CharField(choices=[('VIEW', 'views request'), ('REC', 'receives request'), ('ACC', 'accepts terms of use'), ('POS', 'accepts use of data'), ('POSOV', 'accepted use of data, because decision has been overdue'), ('RESET', 'resets the decision regarding data'), ('NEG', 'declines use of data'), ('NEGOV', 'declines use of data, because decision has been overdue'), ('WITHD', 'withdraws request')], max_length=5),
        ),
    ]
