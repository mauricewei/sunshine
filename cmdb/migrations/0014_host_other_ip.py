# Generated by Django 2.1.4 on 2018-12-29 07:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmdb', '0013_auto_20181228_1825'),
    ]

    operations = [
        migrations.AddField(
            model_name='host',
            name='other_ip',
            field=models.CharField(blank=True, max_length=60, verbose_name='其它IP'),
        ),
    ]
