from django.contrib import admin
from goods.models import *
from utils.tasks import generate_static_index
from django.core.cache import cache
# Register your models here.

class BaseModelAdmin(admin.ModelAdmin):
    '''模型管理站点'''
    def save_model(self, request, obj, form, change):
        # 继承父类方法
        super().save_model(request, obj, form, change)
        # 调用celery重新生成静态首页文件
        generate_static_index.delay()
        # 清除缓存
        cache.delete('index_data')


    def delete_model(self, request, obj):
        # 继承父类方法
        super().delete_model(request, obj)
        # 调用celery重新生成静态首页文件
        generate_static_index.delay()
        # 清除缓存
        cache.delete('index_data')

admin.site.register(Goods, BaseModelAdmin)
admin.site.register(GoodsSPU, BaseModelAdmin)
admin.site.register(GoodsType, BaseModelAdmin)
admin.site.register(GoodsImage, BaseModelAdmin)
admin.site.register(IndexGoodsBanner, BaseModelAdmin)
admin.site.register(IndexTypeGoodsBanner, BaseModelAdmin)
admin.site.register(IndexPromotionBanner, BaseModelAdmin)
