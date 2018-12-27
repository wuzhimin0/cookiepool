# -*- coding: utf-8 -*-
import redis,random
from cookiepool.settings import *
class RedisClient(object):
    def __init__(self,host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD):
        if password:
            self._db = redis.Redis(host=host,port=port,password=password)
        else:
            self._db = redis.Redis(host=host,port=port)
        self.domain = REDIS_DOMAIN
        self.name = REDIS_NAME
    # 拼接key
    def _key(self,key):
        """
        得到格式化的key
        :param key: 最后一个参数key
        :return:
        """
        return "{domain}:{name}:{key}".format(domain=self.domain, name=self.name, key=key)

    def set(self, key, value):
        """
        设置键值对
        :param key:
        :param value:
        :return:
        """
        raise NotImplementedError

    def get(self, key):
        """
        根据键名获取键值
        :param key:
        :return:
        """
        raise NotImplementedError
    def delete(self, key):
        """
        根据键名删除键值对
        :param key:
        :return:
        """
        raise NotImplementedError
    def keys(self):
        """
        得到所有的键名
        :return:
        """
        return self._db.keys('{domain}:{name}:*'.format(domain=self.domain, name=self.name))

class CookiesRedisClient(RedisClient):
    def __init__(self, host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, domain='cookies', name='default'):
        """
        管理Cookies的对象
        :param host: 地址
        :param port: 端口
        :param password: 密码
        :param domain: 域, 如cookies, account等
        :param name: 名称, 一般为站点名, 如 weibo, 默认 default
        """
        RedisClient.__init__(self, host, port, password)
        self.domain = domain
        self.name = name
    def set(self, key, value):
        self._db.set(self._key(key), value)
    def get(self, key):
        return self._db.get(self._key(key)).decode('utf-8')
    def delete(self, key):
        print('Delete', key)
        return self._db.delete(self._key(key))
    def random(self):
        """
        随机得到一Cookies
        :return:
        """
        keys = self.keys()
        return self._db.get(random.choice(keys))
    def all(self):
        """
        获取所有账户, 以字典形式返回
        :return:
        """
        for key in self._db.keys('{domain}:{name}:*'.format(domain=self.domain, name=self.name)):
            group = key.decode('utf-8').split(':')
            if len(group) == 3:
                username = group[2]
                yield {
                    'username': username,
                    'password': self.get(username)
                }

class AccountRedisClient(RedisClient):
    def __init__(self, host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, domain='account', name='default'):
        RedisClient.__init__(self, host, port, password)
        self.domain = domain
        self.name = name
    def set(self, key, value):
        return self._db.set(self._key(key), value)

    def get(self, key):
        return self._db.get(self._key(key)).decode('utf-8')
    def delete(self, key):
        return self._db.delete(self._key(key))
    def all(self):
        """
        获取所有账户, 以字典形式返回
        :return:
        """
        for key in self._db.keys('{domain}:{name}:*'.format(domain=self.domain, name=self.name)):
            group = key.decode('utf-8').split(':')
            if len(group) == 3:
                username = group[2]
                print(username)
                yield {
                    'username': username,
                    'password': self.get(username)
                }