from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client
from django.conf import settings

class FdfsStorage(Storage):

    def __init__(self, client_conf=settings.FDFS_CLIENT_CONF,
                 base_url=settings.NGINX_URL):
        '''新增属性client_conf和base_url'''
        self.client_conf = client_conf
        self.base_url = base_url

    '''自定义存储类'''
    def _open(self, name, mode='rb'):
        '''文件打开'''
        pass

    def _save(self, name, content):
        '''文件保存, name为上传文件名，content为文件内容'''
        # name:选择上传文件的名字
        # content:包含上传文件内容的File对象

        # 创建client对象
        client = Fdfs_client(self.client_conf)
        # 上传文件,获取返回信息
        res = client.upload_by_buffer(content.read())
         #  {'Group name':'group1',
		 #  'Status':'Upload successed.',
		 #  'Remote file_id':'group1/M00/00/00/wKjzh0_xaR63RExnAAAaDqbNk5E1398.py',
		 #  'Uploaded size':'6.0KB',
		 #  'Local file name':'test',
		 #  'Storage IP':'192.168.243.133'}
        # 判断是否上传成功
        if res['Status'] != 'Upload successed.':
            raise Exception('上传失败！')
        filename = res['Remote file_id']
        # 即返回的文件名为：group1/M00/00/00/wKi3gV6pIcWACYB-AAA3sZPrVzQ3331212
        return filename

    def exists(self, name):
        '''判断文件名是否已存在'''
        return False

    def url(self, name):
        '''返回访问文件的url路径'''
        # name为group1/M00/00/00/wKi3gV6pIcWACYB-AAA3sZPrVzQ3331212
        # url应该为Nginx地址/group1/M00/00/00/wKi3gV6pIcWACYB-AAA3sZPrVzQ3331212
        return self.base_url+name
