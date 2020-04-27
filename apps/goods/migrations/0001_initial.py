# Generated by Django 3.0.3 on 2020-04-24 14:37

from django.db import migrations, models
import django.db.models.deletion
import tinymce.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GoodsSPU',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='是否删除')),
                ('name', models.CharField(max_length=50, verbose_name='商品SPU名称')),
                ('detail', tinymce.models.HTMLField(blank=True, verbose_name='商品详情')),
            ],
            options={
                'verbose_name': '商品SPU',
                'verbose_name_plural': '商品SPU',
                'db_table': 'df_goods_spu',
            },
        ),
        migrations.CreateModel(
            name='GoodsType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='是否删除')),
                ('name', models.CharField(max_length=100, verbose_name='种类名称')),
                ('logo', models.CharField(max_length=20, verbose_name='标识')),
                ('image', models.ImageField(upload_to='type', verbose_name='商品类型图片')),
            ],
            options={
                'verbose_name': '商品种类',
                'verbose_name_plural': '商品种类',
                'db_table': 'df_goods_type',
            },
        ),
        migrations.CreateModel(
            name='Goods',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='是否删除')),
                ('name', models.CharField(max_length=100, verbose_name='商品名称')),
                ('brief', models.CharField(max_length=240, verbose_name='简介')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='价格')),
                ('uom', models.CharField(max_length=100, verbose_name='单位')),
                ('onhand', models.IntegerField(default=1, verbose_name='库存')),
                ('sales', models.IntegerField(default=0, verbose_name='销量')),
                ('image', models.ImageField(upload_to='goods', verbose_name='图片')),
                ('stauts', models.SmallIntegerField(choices=[(0, '下线'), (0, '上线')], default=1, verbose_name='状态')),
                ('goodsspu', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='goods.GoodsSPU', verbose_name='商品SPU')),
                ('goodstype', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='goods.GoodsType', verbose_name='商品种类')),
            ],
            options={
                'verbose_name': '商品SKU',
                'verbose_name_plural': '商品SKU',
                'db_table': 'df_goods',
            },
        ),
    ]