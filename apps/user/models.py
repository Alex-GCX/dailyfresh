from django.db import models
from django.contrib.auth.models import AbstractUser
from db.base_model import BaseModel

# Create your models here.
class User(AbstractUser, BaseModel):
    '''用户模型类'''

    class Meta:
        '''元数据'''
        db_table = 'df_user'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username

class AddressManager(models.Manager):
    '''用户地址模型管理器类'''
    # 自定义模型管理器类，用来修改原有方法或者新增方法
    def get_default_address(self, user):
        '''获取用户默认收货地址'''
        try:
            address = self.get(user=user, is_default=True)
        except Address.DoesNotExist:
            address = None
        return address

class Address(BaseModel):
    '''地址模型类'''
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    receiver = models.CharField(verbose_name='收货人', max_length=120)
    address = models.CharField(verbose_name='收货地址', max_length=400)
    zip_code = models.CharField(verbose_name='邮编', max_length=6, null=True)
    phone = models.CharField(verbose_name='电话号码', max_length=11)
    is_default = models.BooleanField(verbose_name='是否默认', default=False)

    objects = AddressManager()

    class Meta:
        '''元数据'''
        db_table = 'df_address'
        verbose_name = '地址'
        verbose_name_plural = verbose_name
