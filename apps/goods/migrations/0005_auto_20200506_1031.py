# Generated by Django 3.0.3 on 2020-05-06 10:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0004_auto_20200429_2247'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goods',
            name='stauts',
            field=models.SmallIntegerField(choices=[(0, '下线'), (1, '上线')], default=1, verbose_name='状态'),
        ),
    ]
