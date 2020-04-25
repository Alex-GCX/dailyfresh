# Generated by Django 3.0.3 on 2020-04-24 12:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='是否删除')),
                ('receiver', models.CharField(max_length=120, verbose_name='收货人')),
                ('address', models.CharField(max_length=400, verbose_name='收货地址')),
                ('zip_code', models.CharField(max_length=6, null=True, verbose_name='邮编')),
                ('phone', models.CharField(max_length=11, verbose_name='电话号码')),
                ('is_default', models.BooleanField(default=False, verbose_name='是否默认')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': '地址',
                'verbose_name_plural': '地址',
                'db_table': 'df_address',
            },
        ),
    ]
