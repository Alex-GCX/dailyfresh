from django.db import models
from db.base_model import BaseModel
# from tinymce.models import HTMLField
from ckeditor.fields import RichTextField

# Create your models here.
class Goods(BaseModel):
    '''商品SKU模型类'''
    status_choices = [
        (0, '下线'),
        (0, '上线'),
    ]
    name = models.CharField(verbose_name='商品名称', max_length=100)
    brief = models.CharField(verbose_name='简介', max_length=240)
    price = models.DecimalField(verbose_name='价格', max_digits=10,
                                decimal_places=2)
    uom = models.CharField(verbose_name='单位', max_length=100)
    onhand = models.IntegerField(verbose_name='库存', default=1)
    sales = models.IntegerField(verbose_name='销量', default=0)
    image = models.ImageField(verbose_name='图片', upload_to='goods')
    stauts = models.SmallIntegerField(verbose_name='状态',
                                      choices=status_choices, default=1)
    goodstype = models.ForeignKey('GoodsType', on_delete=models.DO_NOTHING, verbose_name='商品种类')
    goodsspu = models.ForeignKey('GoodsSPU', on_delete=models.DO_NOTHING, verbose_name='商品SPU')

    class Meta:
        '''元数据'''
        db_table = 'df_goods'
        verbose_name = '商品SKU'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

class GoodsSPU(BaseModel):
    '''商品SPU模型类'''
    name = models.CharField(max_length=50, verbose_name='商品SPU名称')
    # 富文本类型：带有格式的文本
    #  detail = HTMLField(blank=True, verbose_name='商品详情')
    detail = RichTextField(blank=True, verbose_name='商品详情')

    class Meta:
        '''元数据'''
        db_table = 'df_goods_spu'
        verbose_name = '商品SPU'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

class GoodsType(BaseModel):
    '''商品类型模型类'''
    name = models.CharField(max_length=100, verbose_name='种类名称')
    logo = models.CharField(max_length=20, verbose_name='标识')
    image = models.ImageField(upload_to='type', verbose_name='商品类型图片')

    class Meta:
        '''元数据'''
        db_table = 'df_goods_type'
        verbose_name = '商品种类'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

class GoodsImage(BaseModel):
    '''商品图片模型类'''
    goods = models.ForeignKey('Goods', on_delete=models.CASCADE, verbose_name='商品')
    image = models.ImageField(upload_to='goods', verbose_name='图片路径')

    class Meta:
        '''元数据'''
        db_table = 'df_goods_image'
        verbose_name = '商品图片'
        verbose_name_plural = verbose_name

class IndexGoodsBanner(BaseModel):
    '''首页轮播商品展示模型类'''
    goods = models.ForeignKey('Goods', on_delete=models.CASCADE,
                              verbose_name='商品')
    image = models.ImageField(upload_to='banner', verbose_name='图片')
    index = models.SmallIntegerField(default=0, verbose_name='展示顺序')

    class Meta:
        '''元数据'''
        db_table = 'df_index_banner'
        verbose_name = '首页轮播商品'
        verbose_name_plural = verbose_name

class IndexTypeGoodsBanner(BaseModel):
    '''首页分类商品展示模型类'''
    DISPLAY_TYPE_CHOICES = [
        (0, '标题'),
        (1, '图片'),
    ]

    goodstype = models.ForeignKey('GoodsType', on_delete=models.CASCADE,
                                  verbose_name='商品类型')
    goods = models.ForeignKey('Goods', on_delete=models.CASCADE,
                              verbose_name='商品SKU')
    display_type = models.SmallIntegerField(default=1,
                                            choices=DISPLAY_TYPE_CHOICES,
                                            verbose_name='展示类型')
    index = models.SmallIntegerField(default=0, verbose_name='展示顺序')

    class Meta:
        '''元数据'''
        db_table = 'df_index_type_goods'
        verbose_name = '首页分类展示商品'
        verbose_name_plural = verbose_name

class IndexPromotionBanner(BaseModel):
    '''首页促销活动模型类'''
    name = models.CharField(max_length=20, verbose_name='活动名称')
    url = models.URLField(verbose_name='活动链接')
    image = models.ImageField(upload_to='banner', verbose_name='活动图片')
    index = models.SmallIntegerField(default=0, verbose_name='展示顺序')

    class Meta:
        '''元数据'''
        db_table = 'df_index_promotion'
        verbose_name = '主页促销活动'
        verbose_name_plural = verbose_name

    def __str__(self):
        self.name
