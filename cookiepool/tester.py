# -*- coding: utf-8 -*-
import json,requests
from cookiepool.db import *
class Tester(object):
    def __init__(self,name='default'):
        self.name = name
        self.cookies_db = CookiesRedisClient(name=self.name)

    def run(self):
        accounts = self.cookies_db.all()
        for account in accounts:
            username = account.get('username')
            cookies = self.cookies_db.get(username)
            self.test(account, cookies)
    def test(self,account,cookies):
        raise NotImplementedError

class WeiBoTester(Tester):
    def __init__(self, name='weibo'):
        Tester.__init__(self, name)
    def test(self,account,cookies):
        print('Testing Account', account.get('username'))
        try:
            cookies = json.loads(cookies)
        except TypeError:
            # Cookie 格式不正确
            print('Invalid Cookies Value', account.get('username'))
            self.cookies_db.delete(account.get('username'))
            print('Deleted User', account.get('username'))
            return None
        try:
            response = requests.get('https://weibo.com/u/6564086940/home?wvr=5&uut=fin&from=reg', cookies=cookies)
            if response.status_code == 200:
                if '我的首页' in response.content.decode("utf-8"):
                    print('Valid Cookies', account.get('username'))
                else:
                    print('Title is', title)
                    # Cookie已失效
                    print('Invalid Cookies', account.get('username'))
                    self.cookies_db.delete(account.get('username'))
                    print('Deleted User', account.get('username'))
        except ConnectionError as e:
            print('Error', e.args)
            print('Invalid Cookies', account.get('username'))
if __name__ == '__main__':
    WeiBoTester().run()