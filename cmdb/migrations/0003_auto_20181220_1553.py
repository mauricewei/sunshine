# Generated by Django 2.1.4 on 2018-12-20 15:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cmdb', '0002_auto_20181220_1534'),
    ]

    operations = [
        migrations.AlterField(
            model_name='business',
            name='lifecycle',
            field=models.CharField(blank=True, choices=[('online', '已上线'), ('testing', '测试中'), ('terminal', '已终止')], max_length=60, verbose_name='生命周期'),
        ),
        migrations.AlterField(
            model_name='host',
            name='business',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='cmdb.Business', verbose_name='所属业务'),
        ),
        migrations.AlterField(
            model_name='host',
            name='cluster',
            field=models.ManyToManyField(blank=True, to='cmdb.Cluster', verbose_name='所属集群'),
        ),
        migrations.AlterField(
            model_name='host',
            name='is_virtual',
            field=models.BooleanField(default=False, verbose_name='是否为虚拟机'),
        ),
        migrations.AlterField(
            model_name='host',
            name='os_type',
            field=models.CharField(blank=True, choices=[('linux', 'Linux'), ('windows', 'Windows')], default='linux', max_length=60, verbose_name='操作系统类型'),
        ),
    ]
