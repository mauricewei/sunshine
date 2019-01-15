# Generated by Django 2.1.4 on 2019-01-15 17:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmdb', '0026_auto_20190115_1658'),
    ]

    operations = [
        migrations.AlterField(
            model_name='host',
            name='cpu_core_count',
            field=models.IntegerField(blank=True, null=True, verbose_name='CPU逻辑核心数'),
        ),
        migrations.AlterField(
            model_name='host',
            name='cpu_num',
            field=models.IntegerField(blank=True, null=True, verbose_name='CPU个数'),
        ),
        migrations.AlterField(
            model_name='host',
            name='disk_gb',
            field=models.IntegerField(blank=True, null=True, verbose_name='磁盘大小(GB)'),
        ),
        migrations.AlterField(
            model_name='host',
            name='mem_mb',
            field=models.IntegerField(blank=True, null=True, verbose_name='内存大小(MB)'),
        ),
        migrations.AlterField(
            model_name='host',
            name='os_bit',
            field=models.IntegerField(blank=True, null=True, verbose_name='操作系统位数'),
        ),
        migrations.AlterField(
            model_name='host',
            name='service_term',
            field=models.IntegerField(blank=True, max_length=100, null=True, verbose_name='质保年限'),
        ),
    ]