# Generated by Django 2.1.4 on 2018-12-20 15:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmdb', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='host',
            name='is_virtual',
            field=models.BooleanField(default=False),
        ),
    ]
