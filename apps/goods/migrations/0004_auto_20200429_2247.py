# Generated by Django 3.0.3 on 2020-04-29 22:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0003_auto_20200424_1720'),
    ]

    operations = [
        migrations.AlterField(
            model_name='indexpromotionbanner',
            name='url',
            field=models.CharField(max_length=20, verbose_name='活动链接'),
        ),
    ]