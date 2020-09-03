
from qiniu import Auth, put_file, etag, put_data
import qiniu.config

# 需要填写你的 Access Key 和 Secret Key
access_key = 'h_ts5-pEgljsRVknsxK4sm5ZBGPac81S8xY2nFGJ'
secret_key = 'Gu7S_jviEIp_30dt9Pq5VSSSnwkKIFQNgkgDB_rg'

def image_storage(image_data):

    # 构建鉴权对象
    q = Auth(access_key, secret_key)

    # 要上传的空间
    bucket_name = 'info-36'

    # 上传后保存的文件名
    key = None

    # 生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, key, 3600)

    ret, info = put_data(token, key, image_data)

    if info.status_code==200:

        print(info)
        print(ret)
        return ret.get('key')
    else:
        return None

